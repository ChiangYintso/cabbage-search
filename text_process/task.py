# -*- coding: utf-8 -*-
import abc
import asyncio
import os
from asyncio import FIRST_COMPLETED
from pathlib import Path
from typing import Optional

import aiofiles
import aiohttp
import bs4
import jieba
from fake_useragent import FakeUserAgent

_UA = FakeUserAgent()

_HEADERS = {
    'User-Agent': _UA.chrome
}


class Task(metaclass=abc.ABCMeta):
    _DATA_ROOT = os.path.join(os.path.dirname(__file__), '../build')

    def __init__(self, stopwords: str):
        self.origin_dir = f'{self._DATA_ROOT}/{self.name}_org'
        self.article_dir = f'{self._DATA_ROOT}/{self.name}_article'
        self.terms_dir = f'{self._DATA_ROOT}/{self.name}_terms'
        Path(self.origin_dir).mkdir(parents=True, exist_ok=True)
        Path(self.article_dir).mkdir(parents=True, exist_ok=True)
        Path(self.terms_dir).mkdir(parents=True, exist_ok=True)

        self.pending: set = set()
        self.done: set = set()
        self.next_article_id = 0

        self._stop_words = set()

        with open(os.path.join(os.path.dirname(__file__), stopwords), encoding='utf-8') as f:
            self._stop_words = self._stop_words.union(w.strip() for w in f.readlines())

        self.session: Optional[aiohttp.ClientSession] = None

        self._event_map = {'get_news_list': self.extract_news_url, 'download_news': self._process_news}

    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @abc.abstractmethod
    def extract_title_and_text(self, soup: bs4.BeautifulSoup) -> str:
        pass

    @abc.abstractmethod
    def extract_news_url(self, html: str) -> None:
        pass

    def _process_news(self, html: str) -> None:
        self.pending.add(
            asyncio.create_task(self.save_article(html, self.origin_dir, self.next_article_id, 'html'), name=''))
        soup = bs4.BeautifulSoup(html, features='lxml')
        article = self.extract_title_and_text(soup)
        self.pending.add(
            asyncio.create_task(self.save_article(article, self.article_dir, self.next_article_id, 'txt'),
                                name=''))
        terms = '/'.join(self._cut_words(article))
        self.pending.add(
            asyncio.create_task(
                self.save_article(terms, self.terms_dir, self.next_article_id, 'txt'), name=''))
        self.next_article_id += 1

    def _cut_words(self, text: str):
        for t in jieba.cut_for_search(text):
            t = t.strip()
            t = self.word_filter(t)
            if t is not None:
                yield t

    @abc.abstractmethod
    def word_filter(self, word: str) -> Optional[str]:
        pass

    async def _fetch(self, url: str) -> str:
        async with self.session.get(url, headers=_HEADERS) as response:
            return await response.text()

    async def save_article(self, article: str, dirname: str, article_id: int, prefix: str):
        async with aiofiles.open(f'{dirname}/{self.name}_{article_id}.{prefix}',
                                 mode='w',
                                 encoding='utf-8') as f:
            await f.write(article)

    async def event_loop(self):
        while len(self.pending) > 0:
            self.done, self.pending = await asyncio.wait(self.pending, return_when=FIRST_COMPLETED)
            for task in self.done:
                task: asyncio.Task
                name = task.get_name()
                if len(name):
                    self._event_map[name](await task)

    @abc.abstractmethod
    async def run(self):
        pass
