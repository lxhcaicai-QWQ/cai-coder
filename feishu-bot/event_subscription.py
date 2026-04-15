"""
Feishu Event Subscription Service (SSE Long Connection)
Implements server-sent events (SSE) long connection for real-time event streaming
"""
import json
import asyncio
import logging
from typing import AsyncGenerator, Optional, Callable, Any
import aiohttp

from config import settings

logger = logging.getLogger(__name__)


class FeishuEventSubscription:
    """Feishu event subscription client using SSE"""

    def __init__(
        self,
        app_id: str = None,
        app_secret: str = None,
        event_callback: Callable = None
    ):
        self.app_id = app_id or settings.feishu_app_id
        self.app_secret = app_secret or settings.feishu_app_secret
        self.event_callback = event_callback

        self.access_token: Optional[str] = None
        self.token_expires_at: float = 0
        self.is_running: bool = False
        self.session: Optional[aiohttp.ClientSession] = None

    async def get_tenant_access_token(self) -> str:
        """Get tenant access token from Feishu"""
        now = asyncio.get_event_loop().time()

        # Reuse token if still valid
        if self.access_token and now < self.token_expires_at:
            return self.access_token

        # Request new token
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"

        async with self.session.post(url, json={
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }) as response:
            data = await response.json()

            if data.get("code") != 0:
                raise Exception(f"Failed to get tenant access token: {data}")

            self.access_token = data.get("tenant_access_token")
            self.token_expires_at = now + data.get("expire", 7200) - 60  # Refresh 1 min early

            logger.info(f"Tenant access token refreshed, expires in {data.get('expire')}s")
            return self.access_token

    async def subscribe_events(
        self,
        event_types: list = None,
        listener_id: str = None
    ) -> AsyncGenerator[dict, None]:
        """
        Subscribe to Feishu events using SSE

        Args:
            event_types: List of event types to subscribe (e.g., ["im.message.receive_v1"])
            listener_id: Unique listener ID (will be generated if not provided)

        Yields:
            Event data as dict
        """
        if event_types is None:
            event_types = ["im.message.receive_v1"]

        if not listener_id:
            import uuid
            listener_id = f"listener_{uuid.uuid4().hex}"

        logger.info(f"Starting event subscription for types: {event_types}")
        logger.info(f"Listener ID: {listener_id}")

        self.is_running = True

        while self.is_running:
            try:
                token = await self.get_tenant_access_token()

                # SSE endpoint
                url = "https://open.feishu.cn/open-apis/event/v1/stream"

                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }

                # Subscribe request
                subscribe_data = {
                    "event_types": event_types,
                    "listener_id": listener_id
                }

                logger.info(f"Connecting to Feishu SSE endpoint...")

                async with self.session.post(
                    url,
                    headers=headers,
                    json=subscribe_data
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"SSE connection failed: {response.status} - {error_text}")

                    # Read SSE stream
                    async for line in response.content:
                        if not self.is_running:
                            break

                        line_str = line.decode('utf-8').strip()

                        if not line_str:
                            continue

                        # SSE format: data: {...}
                        if line_str.startswith("data:"):
                            data_str = line_str[5:].strip()  # Remove "data:" prefix

                            if data_str == "[DONE]":
                                logger.info("SSE stream ended normally")
                                break

                            try:
                                event_data = json.loads(data_str)

                                # Handle different event types
                                if event_data.get("type") == "event":
                                    await self._handle_event(event_data)

                                    yield event_data

                                elif event_data.get("type") == "heartbeat":
                                    logger.debug("Received heartbeat")

                                elif event_data.get("type") == "error":
                                    logger.error(f"SSE error: {event_data}")

                            except json.JSONDecodeError as e:
                                logger.warning(f"Failed to parse SSE data: {e} - {data_str}")

            except asyncio.CancelledError:
                logger.info("Event subscription cancelled")
                break

            except Exception as e:
                logger.error(f"Event subscription error: {e}")
                logger.info("Reconnecting in 5 seconds...")
                await asyncio.sleep(5)

        logger.info("Event subscription stopped")

    async def _handle_event(self, event_data: dict):
        """Handle incoming event"""
        try:
            # Extract event payload
            event = event_data.get("event", {})
            header = event.get("header", {})

            event_type = header.get("event_type")
            event_id = header.get("event_id")

            logger.info(f"Received event: {event_type} (id: {event_id})")

            # Call callback if provided
            if self.event_callback:
                await self.event_callback(event_data)

        except Exception as e:
            logger.error(f"Error handling event: {e}")

    async def start(self):
        """Start event subscription"""
        if not self.session:
            self.session = aiohttp.ClientSession()

        logger.info("Starting Feishu event subscription service...")

    async def stop(self):
        """Stop event subscription"""
        logger.info("Stopping Feishu event subscription service...")
        self.is_running = False

        if self.session:
            await self.session.close()
            self.session = None

        logger.info("Feishu event subscription service stopped")


class EventSubscriptionManager:
    """Manages event subscription lifecycle"""

    def __init__(self):
        self.subscription: Optional[FeishuEventSubscription] = None
        self.event_queue = asyncio.Queue()
        self.task: Optional[asyncio.Task] = None

    async def start(self, event_callback: Callable = None):
        """Start event subscription"""
        self.subscription = FeishuEventSubscription(event_callback=event_callback)
        await self.subscription.start()

        # Start event stream task
        self.task = asyncio.create_task(self._event_stream())

        logger.info("Event subscription manager started")

    async def _event_stream(self):
        """Event stream loop"""
        async for event in self.subscription.subscribe_events():
            await self.event_queue.put(event)

    async def get_event(self) -> dict:
        """Get next event from queue (blocking)"""
        return await self.event_queue.get()

    async def stop(self):
        """Stop event subscription"""
        if self.subscription:
            await self.subscription.stop()

        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

        logger.info("Event subscription manager stopped")

    def has_events(self) -> bool:
        """Check if there are pending events"""
        return not self.event_queue.empty()
