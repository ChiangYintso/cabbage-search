# -*- coding: utf-8 -*-
import asyncio
import logging
from asyncio import FIRST_COMPLETED

import aiofiles
import aiohttp


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        return await response.text()


async def save_html(response_text: str, article_id: int, data_dir_path: str) -> int:
    """Write html to local file"""
    async with aiofiles.open(f'./{data_dir_path}/page_{article_id}_org.html',
                             mode='w',
                             encoding='utf-8') as f:
        return await f.write(response_text)


async def process_htmls(pending: list, data_dir_path: str):
    article_id = 1
    logging.info('start downloading HTMLs...')
    while len(pending) > 0:
        done, pending = await asyncio.wait(pending, return_when=FIRST_COMPLETED)
        for task in done:
            task: asyncio.Task
            name = task.get_name()
            if name == fetch.__name__:
                result: str = await task

                pending.add(
                    asyncio.create_task(save_html(result, article_id, data_dir_path), name=save_html.__name__))
                article_id += 1
