import wecomsan
import traceback

from config import load_conf
from check_rss_available import is_rss_available

global_conf = load_conf()


def status(show_available) -> (str, bool):
    conf = load_conf()
    url = conf['check_url']
    msg = [
        'rss check of: ' + url,
    ]
    fails = []
    avails = []
    for route in conf['routes']:
        path = route['path']
        timeout = route['timeout_seconds']

        if not is_rss_available(path, url, timeout=timeout):
            fails.append(path)
        else:
            avails.append(path)

    if fails:
        msg.append('failed:')
        for path in fails:
            msg.append(str(path))

    if avails and (show_available or conf['debug']):
        msg.append('available:')
        for path in avails:
            msg.append(str(path))

    msg = '\n'.join(msg)
    return msg, bool(fails)


def manual_check(bot: wecomsan.WecomSan):
    try:
        msg, has_fails = status(show_available=True)
    except Exception as e:
        msg = traceback.format_exc()

    bot.send(msg)


def check(bot: wecomsan.WecomSan):
    try:
        msg, has_fails = status(show_available=False)
        if has_fails:
            bot.send(msg)
    except Exception as e:
        msg = traceback.format_exc()
        bot.send(msg)


if __name__ == '__main__':
    conf = load_conf()
    # TODO add manual check
    bot = wecomsan.WecomSan(**conf['bot'])
    check(bot)
