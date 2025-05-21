import asyncio
from language_tutor.async_runner import run_async


async def _dummy():
    await asyncio.sleep(0.01)
    return 42


def test_run_async():
    result = run_async(_dummy(), in_q_application=False)
    assert result == 42
