import asyncio
import typing as t


def run_in_executor(
    func: t.Coroutine,
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
) -> t.Callable[..., asyncio.Future]:
    def wrap() -> asyncio.Future:
        return asyncio.run_coroutine_threadsafe(func(), loop)
    return wrap
