# -*- coding: utf-8 -*-
import asyncio
from typing import Optional

import aiohttp
import bs4
import nltk

from text_process.task import Task


class ChinaDailyTask(Task):

    def __init__(self):
        super().__init__('stopwords_en.txt')
        self._ps = nltk.PorterStemmer()

    @property
    def name(self) -> str:
        return 'china_daily'

    def word_filter(self, word: str) -> Optional[str]:
        """English documentations will use The Porter Stemming Algorithm"""
        if len(word) > 0 and word not in self._stop_words:
            return self._ps.stem(word.lower())
        return None

    def extract_news_url(self, html: str) -> None:
        soup = bs4.BeautifulSoup(html, features='lxml')
        divs = soup.find_all('div', attrs={'class': 'mb10 tw3_01_2'})
        for div in divs:
            div: bs4.Tag
            a_list = div.find_all('a')
            for a in a_list:
                a: bs4.Tag
                self.pending.add(
                    asyncio.create_task(self._fetch('http:' + a.attrs['href']),
                                        name='download_news'))

    def extract_title_and_text(self, soup: bs4.BeautifulSoup) -> str:
        title = soup.find('h1').contents[0]
        text = '\n'.join(p.text for p in soup.find_all('p', attrs={'class': None}))

        return title + '\n' + text

    async def run(self):
        async with aiohttp.ClientSession() as self.session:
            self.pending = self.pending.union(
                asyncio.create_task(self._fetch(f'http://www.chinadaily.com.cn/world/america/page_{i}.html'),
                                    name='get_news_list')
                for i in range(1, 21))
            await self.event_loop()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    cd = ChinaDailyTask()
    loop.run_until_complete(cd.run())
