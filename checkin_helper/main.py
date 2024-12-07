from pathlib import Path
import asyncio

from loguru import logger
from checker import BaseChecker
from modules import Doki8Checker, YuyunChecker, NssctfChecker
from config import load_conf

ROOT = Path(__file__).parent
logger.add(str(ROOT/'log'), retention='1 day')

async def main(tasks):
    for task in tasks:
        try:
            await task
        except Exception as err:
            logger.error(err)

async def run_checker(checker: BaseChecker):
    logger.info('checking ' + checker.name + '...')
    checker.run()

#TODO 可以把签到搬到github action上，每天自动签到. 参考: https://github.com/Marven11/NSSCTFAutoLogin/blob/main/.github/workflows/run-tests.yml
if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    conf = load_conf()
    tasks = []
    switches = conf['module']
    if conf['debug']:
        logger.warning('debuging ' + conf['debug'])
        switches = {conf['debug']: True}
    if switches.get('doki8'):
        tasks.append(loop.create_task(run_checker(Doki8Checker(3, 60))))
    if switches.get('yuyun'):
        tasks.append(loop.create_task(run_checker(YuyunChecker(3, 60))))
    if switches.get('nssctf'):
        tasks.append(loop.create_task(run_checker(NssctfChecker(3, 60, conf['nssctf']))))
    loop.run_until_complete(main(tasks))
