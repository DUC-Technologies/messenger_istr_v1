from typing import Protocol, Any
from .context import BotContext, MessageContext, CallbackContext


class Filter(Protocol):
    def __call__(self, ctx: BotContext) -> bool: ...


class Text:
    def __init__(self, *values: str):
        self.values = {v.lower() for v in values}

    def __call__(self, ctx: BotContext) -> bool:
        return isinstance(ctx, MessageContext) and ctx.text.lower() in self.values


class Command:
    def __init__(self, *commands: str):
        self.commands = {c.lstrip("/").lower() for c in commands}

    def __call__(self, ctx: BotContext) -> bool:
        if not isinstance(ctx, MessageContext):
            return False
        text = ctx.text.lstrip("/").lower().split()[0]
        return text in self.commands


class Callback:
    """Matches CallbackContext by one or more payload fields."""

    def __init__(self, **match: Any):
        self.match = match

    def __call__(self, ctx: BotContext) -> bool:
        if not isinstance(ctx, CallbackContext):
            return False
        return all(ctx.payload.get(k) == v for k, v in self.match.items())


