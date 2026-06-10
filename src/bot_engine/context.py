from dataclasses import dataclass, field
from typing import Any


@dataclass
class MessageContext:
    user_id: int
    text: str
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class CallbackContext:
    user_id: int
    payload: dict[str, Any]
    extra: dict[str, Any] = field(default_factory=dict)


BotContext = MessageContext | CallbackContext
