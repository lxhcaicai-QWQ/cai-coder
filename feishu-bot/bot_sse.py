"""
Feishu Bot - SSE Event Subscription Mode
Uses long connection (SSE) to receive Feishu events in real-time
"""
import asyncio
import json
import time
import logging
from typing import Dict, Any, Optional

from fastapi import FastAPI
import uvicorn

from config import settings
from client import CaiCoderClient
from event_subscription import EventSubscriptionManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app (for health check)
app = FastAPI(title="Feishu Bot (SSE Mode)", description="Cai-Coder Feishu Integration - Event Subscription")

# Initialize Cai-Coder client
caicoder_client = CaiCoderClient(
    base_url=settings.caicoder_api_url,
    model=settings.caicoder_model,
    stream=settings.caicoder_stream
)

# Initialize event subscription manager
event_manager = EventSubscriptionManager()

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
        if len(session["messages"]) > settings.max_history * 2:
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


async def send_feishu_reply(message_id: str, content: str):
    """Send reply message to Feishu"""
    import aiohttp

    # Get tenant access token
    async with aiohttp.ClientSession() as session:
        token_response = await session.post(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={
                "app_id": settings.feishu_app_id,
                "app_secret": settings.feishu_app_secret
            }
        )
        token_data = await token_response.json()
        tenant_access_token = token_data.get("tenant_access_token")

        if not tenant_access_token:
            logger.error(f"Failed to get tenant access token: {token_data}")
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

        reply_response = await session.post(
            reply_url,
            headers=headers,
            json=reply_body,
            params={"message_id": message_id}
        )

        if reply_response.status != 200:
            error_text = await reply_response.text()
            logger.error(f"Failed to send reply: {reply_response.status} - {error_text}")


async def process_message_event(event_data: dict):
    """Process incoming Feishu message event"""
    try:
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

        logger.info(f"Processing message from {sender_id}: {user_message[:50]}...")

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
            logger.error(f"API error: {response.get('error')}")

        # Add assistant message to history
        SessionManager.add_message(session_id, "assistant", assistant_message)

        # Send reply to Feishu
        await send_feishu_reply(message_id, assistant_message)

        logger.info(f"Sent reply to {message_id}")

    except Exception as e:
        logger.error(f"Error processing message event: {e}")


async def event_callback(event_data: dict):
    """Event callback for event subscription"""
    try:
        event = event_data.get("event", {})
        header = event.get("header", {})

        event_type = header.get("event_type")

        logger.info(f"Received event type: {event_type}")

        # Handle message events
        if event_type == "im.message.receive_v1":
            await process_message_event(event_data)

    except Exception as e:
        logger.error(f"Error in event callback: {e}")


async def event_loop():
    """Main event processing loop"""
    logger.info("Starting event processing loop...")

    while True:
        try:
            # Wait for next event
            event = await event_manager.get_event()
            logger.debug(f"Processing event from queue")

            # Process event
            await event_callback(event)

        except asyncio.CancelledError:
            logger.info("Event loop cancelled")
            break
        except Exception as e:
            logger.error(f"Error in event loop: {e}")
            await asyncio.sleep(1)


@app.get("/health")
async def health():
    """Health check endpoint"""
    caicoder_healthy = caicoder_client.health_check()
    return {
        "status": "healthy" if caicoder_healthy else "degraded",
        "caicoder_api": "connected" if caicoder_healthy else "disconnected",
        "connection_mode": "subscription (SSE)",
        "active_sessions": len(sessions),
        "event_manager_running": event_manager.subscription is not None
    }


@app.on_event("startup")
async def startup_event():
    """Run on startup"""
    logger.info(f"🚀 {settings.bot_name} bot starting...")
    logger.info(f"📡 Connection mode: SSE (Event Subscription)")
    logger.info(f"🤖 Connecting to Cai-Coder API at {settings.caicoder_api_url}")

    # Check Cai-Coder connection
    if caicoder_client.health_check():
        logger.info("✅ Cai-Coder API connected successfully")
    else:
        logger.warning("⚠️  Warning: Cai-Coder API is not reachable")

    # Start event subscription
    await event_manager.start(event_callback=event_callback)

    # Start event processing loop
    asyncio.create_task(event_loop())

    logger.info("✅ Bot started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown"""
    logger.info(f"👋 {settings.bot_name} bot shutting down...")

    # Stop event subscription
    await event_manager.stop()

    logger.info("✅ Bot shutdown complete")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.bot_host,
        port=settings.bot_port,
        log_level="info"
    )
