import abc
import time

from loguru import logger

from util import report


class CheckError(BaseException):
    def __init__(self, msg='', detail=''):
        super().__init__(msg)
        self.detail = detail


class BaseChecker:
    def __init__(self, name: str, retry: int = 3, timeout: int = 60, conf: dict = None):
        self.name = name
        self.retry = retry
        self.timeout = timeout
        self.context = {}
        self.conf = conf or {}

    def _prepare(self, context: dict, *args, **kwargs):
        ...

    def _finally(self, context: dict, *args, **kwargs):
        ...

    @abc.abstractmethod
    def _check(self, context: dict, *args, **kwargs) -> str:
        ...

    def run(self):
        for i in range(self.retry, 0, -1):
            try:
                self._prepare(self.context)
                detail = self._check(self.context)
                title = f'{self.name}：'
                report(title, detail)
                break
            except CheckError as err:
                logger.error(err)
                title = f"{self.name}：{str(err)}！" + ("finished" if i == 0 else ('remain: ' + str(i - 1)))
                if err.detail:
                    report(title, err.detail)
                else:
                    report(title)
                if i != 0:
                    time.sleep(self.timeout)
            except Exception as err:
                logger.error(err)
                title = f"{self.name}：签到失败！" + ("finished" if i == 0 else ('remain: ' + str(i - 1)))
                content = str(type(err).__name__ + '\n' + str(err))
                report(title, content)
                if i != 0:
                    time.sleep(self.timeout)
        self._finally(self.context)
