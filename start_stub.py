import asyncio
import logging
from opencj_listener import OpenCJListener

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Stub():
    """
Fake Discord module that just logs received events to console
    """
    async def on_game_event(self, event):
        logger.info(f'Received event: {type(event).__name__}')

async def main():
    dc = Stub()
    ls = OpenCJListener(dc, 'stub')

    logger.info('Starting stub listener')

    await ls.start()

if __name__ == "__main__":
    asyncio.run(main())
