# -*- coding: utf-8 -*-
import asyncio
from typing import Optional

import aiohttp
import bs4

from _task import Task


class GMWTask(Task):
    """
    Crawler for https://guancha.gmw.cn
    """
    def __init__(self):
        super().__init__('stopwords_cn.txt')

    @property
    def name(self) -> str:
        return 'gmw'

    def word_filter(self, word: str) -> Optional[str]:
        if len(word) > 0 and word not in self._stop_words:
            return word
        return None

    def extract_title_and_text(self, soup: bs4.BeautifulSoup) -> (str, str):
        title = str(soup.find('h1', {'class': 'u-title'}).contents[0]).strip()

        main_text = soup.find('div', {'class': 'u-mainText'})
        p_list = main_text.find_all('p')

        return title, '\n'.join(p.contents[0] for p in p_list if
                                isinstance(p, bs4.Tag) and isinstance(p.contents[0], bs4.NavigableString))

    def extract_news_url(self, html: str):
        soup = bs4.BeautifulSoup(html, features='lxml')
        ul = soup.find('ul', {'class': 'channel-newsGroup'})
        a = ul.find_all('a')
        for li in a:
            href: str = li.attrs['href']
            if not href.startswith('https'):
                href = 'https://guancha.gmw.cn/' + href
            self.pending.add(
                asyncio.create_task(self._fetch(href),
                                    name='download_news'))

    async def run(self):
        async with aiohttp.ClientSession() as self.session:
            self.pending = self.pending.union(
                asyncio.create_task(self._fetch(f'https://guancha.gmw.cn/node_{nodeid}_{i}.htm'),
                                    name='get_news_list')
                for nodeid in (7292, 26275, 86599, 87838) for i in range(2, 11))
            await self._event_loop()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    gmw = GMWTask()
    loop.run_until_complete(gmw.run())
