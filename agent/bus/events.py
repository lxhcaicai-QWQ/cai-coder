from dataclasses import field, dataclass
from typing import Any

@dataclass
class InMessage:
    """Message received from a chat channel."""
    channel: str
    chat_id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class OutMessage:
    """Message to send to a chat channel."""
    channel: str
    chat_id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)