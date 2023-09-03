import abc
import time

from loguru import logger

from util import report


class CheckError(BaseException):
    def __init__(self, msg='', detail=''):
        super().__init__(msg)
        self.detail = detail


class BaseChecker:
    def __init__(self, name: str, retry: int = 3, timeout: int = 60):
        self.name = name
        self.retry = retry
        self.timeout = timeout
        self.context = {}

    def _prepare(self, context: dict, *args, **kwargs):
        ...

    def _finally(self, context: dict, *args, **kwargs):
        ...

    @abc.abstractmethod
    def _check(self, context: dict, *args, **kwargs):
        ...

    def run(self):
        self._prepare(self.context)
        for i in range(self.retry, 0, -1):
            try:
                self._check(self.context)
                title = f'{self.name}：签到成功'
                report(title)
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
