import wecomsan
from loguru import logger

from config import load_conf


def report(title, content=None, url=None):
    logger.info('report:\n{}\n{}', title, content)
    conf = load_conf()
    bot = wecomsan.WecomSan(**conf['bot'])
    if content is not None:
        url = url or 'http://myflaskserver.barryzzj.top:23354/test'
        bot.send_textcard(title, content, url)
    else:
        bot.send(title)
