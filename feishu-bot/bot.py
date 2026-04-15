"""
Feishu Bot - Main Application
Bridges Feishu messages to Cai-Coder AI service
"""
import hashlib
import hmac
import base64
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse, TextResponse
from pydantic import BaseModel

from config import settings
from client import CaiCoderClient

# Initialize FastAPI app
app = FastAPI(title="Feishu Bot", description="Cai-Coder Feishu Integration")

# Initialize Cai-Coder client
caicoder_client = CaiCoderClient(
    base_url=settings.caicoder_api_url,
    model=settings.caicoder_model,
    stream=settings.caicoder_stream
)

# Session storage: session_id -> conversation data
sessions: Dict[str, Dict[str, Any]] = {}


class SessionManager:
    """Manage conversation sessions with TTL"""

    @staticmethod
    def get_or_create_session(session_id: str) -> Dict[str, Any]:
        """Get existing session or create new one"""
        now = time.time()

        if session_id not in sessions:
            sessions[session_id] = {
                "messages": [],
                "created_at": now,
                "last_activity": now
            }
        else:
            # Update activity time
            sessions[session_id]["last_activity"] = now

        return sessions[session_id]

    @staticmethod
    def add_message(session_id: str, role: str, content: str):
        """Add message to session history"""
        session = SessionManager.get_or_create_session(session_id)
        session["messages"].append({
            "role": role,
            "content": content
        })

        # Limit history size
        if len(session["messages"]) > settings.max_history * 2:  # Both user and assistant messages
            session["messages"] = session["messages"][-settings.max_history * 2:]

    @staticmethod
    def get_history(session_id: str) -> list:
        """Get conversation history for API"""
        session = SessionManager.get_or_create_session(session_id)
        return session["messages"]

    @staticmethod
    def cleanup_expired_sessions():
        """Remove expired sessions based on TTL"""
        now = time.time()
        expired = [
            sid for sid, data in sessions.items()
            if now - data["last_activity"] > settings.session_ttl
        ]
        for sid in expired:
            del sessions[sid]


class FeishuEvent(BaseModel):
    """Feishu event model"""
    token: str
    timestamp: str
    nonce: str
    type: str
    challenge: Optional[str] = None


def verify_signature(
    timestamp: str,
    nonce: str,
    body: str,
    signature: str
) -> bool:
    """Verify Feishu request signature"""
    string_to_sign = f"{timestamp}{nonce}{body}"
    sign_str = hmac.new(
        settings.feishu_encrypt_key.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).digest()
    sign = base64.b64encode(sign_str).decode('utf-8')
    return sign == signature


@app.get("/health")
async def health():
    """Health check endpoint"""
    caicoder_healthy = caicoder_client.health_check()
    return {
        "status": "healthy" if caicoder_healthy else "degraded",
        "caicoder_api": "connected" if caicoder_healthy else "disconnected",
        "active_sessions": len(sessions)
    }


@app.post("/feishu/events")
async def handle_feishu_events(
    request: Request,
    x_lark_request_timestamp: Optional[str] = Header(None),
    x_lark_request_nonce: Optional[str] = Header(None),
    x_lark_signature: Optional[str] = Header(None)
):
    """
    Handle Feishu event callbacks

    Supports:
    - URL verification (url_verification)
    - Message events (im.message.receive_v1)
    """
    # Get raw body for signature verification
    body_bytes = await request.body()
    body_str = body_bytes.decode('utf-8')

    # Verify signature if encryption is enabled
    if settings.feishu_encrypt_key and x_lark_signature:
        if not verify_signature(
            x_lark_request_timestamp,
            x_lark_request_nonce,
            body_str,
            x_lark_signature
        ):
            raise HTTPException(status_code=403, detail="Invalid signature")

    # Parse event data
    try:
        event_data = json.loads(body_str)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Handle URL verification
    if event_data.get("type") == "url_verification":
        challenge = event_data.get("challenge")
        return JSONResponse(content={"challenge": challenge})

    # Handle message events
    if event_data.get("header", {}).get("event_type") == "im.message.receive_v1":
        try:
            await process_message_event(event_data)
            return JSONResponse(content={"code": 0, "msg": "success"})
        except Exception as e:
            print(f"Error processing message: {e}")
            return JSONResponse(content={"code": 1, "msg": str(e)}, status_code=500)

    return JSONResponse(content={"code": 0, "msg": "success"})


async def process_message_event(event_data: Dict[str, Any]):
    """Process incoming Feishu message event"""
    event = event_data.get("event", {})
    message = event.get("message", {})

    # Extract message content
    content = message.get("content", "")
    message_type = message.get("message_type")

    # Only handle text messages
    if message_type != "text":
        return

    # Parse content (Feishu sends JSON string)
    try:
        content_obj = json.loads(content)
        user_message = content_obj.get("text", "").strip()
    except json.JSONDecodeError:
        return

    if not user_message:
        return

    # Get session ID (use chat_id or message_id)
    chat_id = event.get("chat", {}).get("chat_id", "")
    message_id = message.get("message_id", "")
    session_id = chat_id if chat_id else message_id

    # Get user info
    sender = event.get("sender", {})
    sender_id = sender.get("sender_id", "")
    sender_type = sender.get("sender_type", "")

    # Only respond to user messages (not bot messages)
    if sender_type == "app":
        return

    # Add user message to history
    SessionManager.add_message(session_id, "user", user_message)

    # Get conversation history
    messages = SessionManager.get_history(session_id)

    # Call Cai-Coder API
    response = caicoder_client.chat_completion(
        messages=messages,
        session_id=session_id,
        temperature=0.7
    )

    assistant_message = response.get("content", "")
    if response.get("error"):
        assistant_message = response.get("content", "抱歉，AI 服务暂时不可用。")

    # Add assistant message to history
    SessionManager.add_message(session_id, "assistant", assistant_message)

    # Send reply to Feishu
    await send_feishu_reply(
        message_id=message_id,
        content=assistant_message
    )


async def send_feishu_reply(message_id: str, content: str):
    """Send reply message to Feishu"""
    # This requires Feishu API implementation
    # For now, we'll implement a basic version
    # You'll need to implement the actual Feishu API call

    import requests

    # Get tenant access token
    token_response = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={
            "app_id": settings.feishu_app_id,
            "app_secret": settings.feishu_app_secret
        }
    )
    token_data = token_response.json()
    tenant_access_token = token_data.get("tenant_access_token")

    if not tenant_access_token:
        print(f"Failed to get tenant access token: {token_data}")
        return

    # Send message reply
    reply_url = "https://open.feishu.cn/open-apis/im/v1/messages/reply"
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json"
    }
    reply_body = {
        "reply_in_thread": False,
        "msg_type": "text",
        "content": json.dumps({"text": content})
    }

    reply_response = requests.post(
        reply_url,
        headers=headers,
        json=reply_body,
        params={"message_id": message_id}
    )

    if reply_response.status_code != 200:
        print(f"Failed to send reply: {reply_response.text}")


@app.on_event("startup")
async def startup_event():
    """Run on startup"""
    print(f"🚀 {settings.bot_name} bot starting...")
    print(f"📡 Listening on {settings.bot_host}:{settings.bot_port}")
    print(f"🤖 Connecting to Cai-Coder API at {settings.caicoder_api_url}")

    # Check Cai-Coder connection
    if caicoder_client.health_check():
        print("✅ Cai-Coder API connected successfully")
    else:
        print("⚠️  Warning: Cai-Coder API is not reachable")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown"""
    print(f"👋 {settings.bot_name} bot shutting down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.bot_host,
        port=settings.bot_port,
        log_level="info"
    )
