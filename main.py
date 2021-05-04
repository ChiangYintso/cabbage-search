# -*- coding: utf-8 -*-
import logging
import os
import subprocess

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
    logging.info('start')

    ps = []
    dirs = os.listdir('./text_process')
    for script_name in dirs:
        if script_name[0] != '_' and script_name[-2:] == 'py':
            p = subprocess.Popen(f'python ./text_process/{script_name}')
            ps.append((script_name, p))

    all_success = True
    for script_name, p in ps:
        p.wait()
        if p.returncode != 0:
            logging.error(f'error in {script_name}')
            all_success = False
    if all_success:
        logging.info('All the scripts run successfully.')
    logging.info('done')
