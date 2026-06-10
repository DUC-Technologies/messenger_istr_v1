from dataclasses import dataclass, field
from typing import Callable, Awaitable
from .context import BotContext
from .filters import Filter


@dataclass
class HandlerRecord:
    func: Callable[[BotContext], Awaitable[None]]
    filters: list[Filter] = field(default_factory=list)

    def matches(self, ctx: BotContext) -> bool:
        return all(f(ctx) for f in self.filters)
