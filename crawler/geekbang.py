# -*- coding: utf-8 -*-
import asyncio
import json
import logging
from http.client import OK
from pathlib import Path

import aiohttp

from crawler.commons import fetch, process_htmls

_PAYLOAD_HEADER = {
    'Origin': 'https://s.geekbang.org',
    'Host': 's.geekbang.org',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/86.0.4240.111 Safari/537.36',
    'Content-Type': 'application/json;charset=UTF-8',
}

_GEEKBANG_QUERY_URL = 'https://s.geekbang.org/api/gksearch/search'


async def post_query(session: aiohttp.ClientSession, keyword: str, num: int, page: int) -> dict:
    response: aiohttp.ClientResponse = await session.post(_GEEKBANG_QUERY_URL,
                                                          data=json.dumps({'q': keyword, 't': 1, 's': num, 'p': page}),
                                                          headers=_PAYLOAD_HEADER)
    if response.status == OK:
        data: dict = await response.json(content_type='text/plain')
        return data
    else:
        logging.warning(f'POST failed. status: {response.status}')
        return {}


async def run(keyword: str, data_dir_path: str, num=500):
    Path(data_dir_path).mkdir(parents=True, exist_ok=True)
    async with aiohttp.ClientSession() as session:
        data: dict = await post_query(session, keyword, num, 2)

        pending = [asyncio.create_task(fetch(session, item['content_url']),
                                       name=fetch.__name__) for item in
                   data['data']['list']]

        await process_htmls(pending, data_dir_path)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run('数据库', 'geekbang_pages'))
    logging.info('done')
