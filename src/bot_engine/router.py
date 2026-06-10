from typing import Callable, Awaitable
from .context import BotContext
from .filters import Filter
from .handler import HandlerRecord


class Router:
    def __init__(self):
        self.handlers: list[HandlerRecord] = []

    def message(self, *filters: Filter):
        def decorator(func: Callable[[BotContext], Awaitable[None]]):
            self.handlers.append(HandlerRecord(func=func, filters=list(filters)))
            return func
        return decorator

    # Alias — единый декоратор для callback-событий
    callback = message
