from .context import BotContext
from .handler import HandlerRecord
from .router import Router


class Dispatcher:
    def __init__(self):
        self._handlers: list[HandlerRecord] = []

    def include_router(self, router: Router) -> None:
        self._handlers.extend(router.handlers)

    def message(self, *filters):
        """Shortcut: register a handler directly on the dispatcher."""
        def decorator(func):
            self._handlers.append(HandlerRecord(func=func, filters=list(filters)))
            return func
        return decorator

    callback = message

    async def dispatch(self, ctx: BotContext) -> bool:
        """
        Passes context to the first matching handler.
        Returns True if a handler was found, False otherwise.
        """
        for record in self._handlers:
            if record.matches(ctx):
                await record.func(ctx)
                return True
        return False
