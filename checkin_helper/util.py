import wecomsan
from loguru import logger

from config import load_conf


def report(title, content=None):
    logger.info('title: {}\ncontent: {}', title, content)
    conf = load_conf()
    bot = wecomsan.WecomSan(**conf['bot'])
    if content is not None:
        bot.send_textcard(title, content, 'http://myflaskserver.barryzzj.top:23354/test')
    else:
        bot.send(title)
