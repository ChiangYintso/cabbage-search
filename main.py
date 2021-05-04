# -*- coding: utf-8 -*-
import asyncio
import logging

from text_process import ChinaDailyTask, GMWTask


def pre_process():
    cd = ChinaDailyTask()
    gmw = GMWTask()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(cd.run(), gmw.run()))


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
    logging.info('start')
    pre_process()
    logging.info('done')
