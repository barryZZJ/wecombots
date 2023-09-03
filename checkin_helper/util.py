import wecomsan
from loguru import logger

from config import load_conf


def report(title, content=None):
    logger.info('title: {}\ncontent: {}', title, content)
    if content is not None:
        msg = f'{title=}\n{content=}'
    else:
        msg = title
    conf = load_conf()
    bot = wecomsan.WecomSan(**conf['bot'])
    bot.send(msg)
