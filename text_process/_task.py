# -*- coding: utf-8 -*-
import abc
import asyncio
import os
from asyncio import FIRST_COMPLETED
from pathlib import Path
from typing import Optional
from collections import OrderedDict

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

        self.titles = OrderedDict()
        self.next_article_id = 0

        self._file_write_tasks = []
        self._stop_words = set()

        with open(os.path.join(os.path.dirname(__file__), stopwords), encoding='utf-8') as f:
            self._stop_words = self._stop_words.union(w.strip() for w in f.readlines())

        self.session: Optional[aiohttp.ClientSession] = None

        self._event_map = {'get_news_list': self.extract_news_url, 'download_news': self._process_news}

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Name of the task."""
        pass

    @abc.abstractmethod
    def extract_title_and_text(self, soup: bs4.BeautifulSoup) -> (str, str):
        """
        Extract title and text from html.
        Args:
            soup:
                The data structure representing the parsed html of an article.
        Returns:
            (title, content) of the article.
        """
        pass

    @abc.abstractmethod
    def extract_news_url(self, html: str) -> None:
        """
        Extract news url from given html of a website.
        Args:
            html:
                html of the website to crawl.
        """
        pass

    def _process_news(self, html: str) -> None:
        self._file_write_tasks.append(self._save_files(html, self.origin_dir, self.next_article_id, 'html'))
        soup = bs4.BeautifulSoup(html, features='lxml')
        title, content = self.extract_title_and_text(soup)
        if title not in self.titles:
            self._file_write_tasks.append(self._save_files(content, self.article_dir, self.next_article_id, 'txt'))

            terms = '/'.join(self._cut_words(content))
            self._file_write_tasks.append(self._save_files(terms, self.terms_dir, self.next_article_id, 'txt'))
            self.titles.setdefault(title, self.next_article_id)
            self.next_article_id += 1

    def _cut_words(self, text: str):
        for t in jieba.cut_for_search(text):
            t = t.strip()
            t = self.word_filter(t)
            if t is not None:
                yield t

    @abc.abstractmethod
    def word_filter(self, word: str) -> Optional[str]:
        """
        Filter and may transform the word by stopwords list and the Porter Stemming Algorithm.
        Args:
            word:
                word to process
        Returns:
            If the word is in stopwords list, returns None, else returns transformed word.
        """
        pass

    async def _fetch(self, url: str) -> str:
        async with self.session.get(url, headers=_HEADERS) as response:
            return await response.text()

    async def _save_files(self, article: str, dirname: str, article_id: int, prefix: str):
        async with aiofiles.open(f'{dirname}/{self.name}_{"%05d" % article_id}.{prefix}',
                                 mode='w',
                                 encoding='utf-8') as f:
            await f.write(article)

    async def _save_titles(self):
        async with aiofiles.open(f'{self._DATA_ROOT}/{self.name}_titles.txt', mode='w', encoding='utf-8') as f:
            await f.write('\n'.join(k for k in self.titles.keys()))

    async def _event_loop(self):
        while len(self.pending) > 0:
            self.done, self.pending = await asyncio.wait(self.pending, return_when=FIRST_COMPLETED)
            for task in self.done:
                task: asyncio.Task
                name = task.get_name()
                if len(name):
                    html: str = await task
                    self._event_map[name](html)
        await asyncio.gather(*self._file_write_tasks, self._save_titles())

    @abc.abstractmethod
    async def run(self):
        """Run the task."""
        pass
