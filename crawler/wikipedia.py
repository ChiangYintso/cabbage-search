# -*- coding: utf-8 -*-

import asyncio
import logging

import aiohttp
from pathlib import Path

from commons import fetch, process_htmls


async def run(url: str, data_dir_path: str, count=1000):
    Path(data_dir_path).mkdir(parents=True, exist_ok=True)
    async with aiohttp.ClientSession() as session:
        pending: list = [
            asyncio.create_task(fetch(session, url), name=fetch.__name__)
            for _ in range(count)
        ]
        await process_htmls(pending, data_dir_path)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run('https://en.wikipedia.org/wiki/Special:Random', './wikipedia_pages'))
    logging.info('done')
