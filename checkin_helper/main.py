from pathlib import Path

from loguru import logger
from modules import Doki8Checker, YuyunChecker
from config import load_conf

ROOT = Path(__file__).parent
logger.add(str(ROOT/'log'), retention='1 day')

if __name__ == '__main__':
    conf = load_conf()
    checkers = []
    switches = conf['module']
    if switches['doki8']:
        logger.info('checking doki8...')
        checkers.append(Doki8Checker(3, 60))
    if switches['yuyun']:
        logger.info('checking yuyun...')
        checkers.append(YuyunChecker(3, 60))

    for checker in checkers:
        try:
            checker.run()
        except Exception as err:
            logger.error(err)
