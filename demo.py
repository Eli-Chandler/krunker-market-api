import asyncio
from krunker_market_api.websocket.krunker_websocket import KrunkerWebSocket
import logging

import logging
import colorlog

def setup_colored_logging():
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        fmt="%(log_color)s[%(levelname)s] %(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'bold_red',
        }
    ))

    logger = colorlog.getLogger()
    logger.setLevel(logging.INFO)  # Adjust as needed
    logger.handlers = [handler]

setup_colored_logging()

async def main():
    kws = KrunkerWebSocket()
    await kws.start()
    await asyncio.sleep(10)
    await kws.close()


if __name__ == "__main__":
    asyncio.run(main())