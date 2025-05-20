import asyncio
import logging
import colorlog
import os

from krunker_market_api.api.krunker_api import KrunkerApi


def setup_colored_logging():
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        fmt="%(log_color)s[%(levelname)s] %(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    ))

    logger = colorlog.getLogger()
    logger.setLevel(logging.INFO)  # Adjust as needed
    logger.handlers = [handler]


setup_colored_logging()


async def main():
    email = os.environ["KRUNKER_EMAIL"]
    password = os.environ["KRUNKER_PASSWORD"]

    k = KrunkerApi()
    await k.ready()
    await k.login(email, password)

    while True:
        await asyncio.sleep(10)
        print(k.ping())


if __name__ == "__main__":
    asyncio.run(main())
