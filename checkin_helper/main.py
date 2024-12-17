from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from loguru import logger
from checker import BaseChecker
from modules import Doki8Checker, YuyunChecker, NssctfChecker, CtfhubChecker
from config import load_conf

ROOT = Path(__file__).parent
logger.add(str(ROOT/'log'), retention='1 day')

def run_checker(checker: BaseChecker):
    logger.info('checking ' + checker.name + '...')
    checker.run()

#TODO 可以把签到搬到github action上，每天自动签到. 参考: https://github.com/Marven11/NSSCTFAutoLogin/blob/main/.github/workflows/run-tests.yml
if __name__ == '__main__':
    conf = load_conf()
    tasks = []
    switches = conf['module']
    if conf['debug']:
        logger.warning('debuging ' + conf['debug'])
        switches = {conf['debug']: True}
    with ThreadPoolExecutor(max_workers=5) as executor:
        futs = []
        if switches.get('doki8'):
            futs.append(executor.submit(run_checker, Doki8Checker(3, 60, conf['doki8'])))
        if switches.get('yuyun'):
            futs.append(executor.submit(run_checker, YuyunChecker(3, 60, conf['yuyun'])))
        if switches.get('nssctf'):
            futs.append(executor.submit(run_checker, NssctfChecker(3, 60, conf['nssctf'])))
        if switches.get('ctfhub'):
            futs.append(executor.submit(run_checker, CtfhubChecker(3, 60, conf['ctfhub'])))
        for fut in as_completed(futs):
            fut.result()
