"""Helper to run asynchronous coroutines in GUI applications."""

import asyncio
try:
    import nest_asyncio
except Exception:  # pragma: no cover - fallback when dependency missing
    class _NestAsyncIO:
        def apply(self):
            pass

    nest_asyncio = _NestAsyncIO()  # type: ignore

try:
    from PyQt6.QtWidgets import QApplication
except Exception:  # pragma: no cover - fallback when dependency missing
    class QApplication:
        @staticmethod
        def processEvents():
            pass


def run_async(coro, in_q_application=True):
    """Run an async coroutine from a synchronous method without blocking UI.

    Args:
        coro: The coroutine to run
        in_q_application: Whether running in Qt application
    """
    # Apply nest_asyncio to allow nested event loops
    try:
        nest_asyncio.apply()
    except RuntimeError:
        # If already applied or not needed, continue
        pass

    # Get or create an event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Create a future for the coroutine
    future = asyncio.ensure_future(coro)

    # Process Qt events while waiting for the coroutine to complete
    if in_q_application:
        while not future.done():
            QApplication.processEvents()
            loop.run_until_complete(asyncio.sleep(0.01))  # Short sleep to avoid CPU hogging
    else:
        # If not in Qt application, just run the event loop until the coroutine is done
        loop.run_until_complete(future)
    # Return the result
    return future.result()
