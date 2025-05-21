import asyncio
from language_tutor import utils


async def _dummy():
    await asyncio.sleep(0.01)
    return 42


def test_run_async():
    result = utils.run_async(_dummy(), in_q_application=False)
    assert result == 42
