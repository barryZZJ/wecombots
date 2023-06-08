import wecomsan
import traceback
import time
from config import load_conf
from check_port_open import is_port_open


enabled = True

def timetag():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def check_port(bot: wecomsan.WecomSan):
    global enabled
    if not enabled:
        print('bot is disabled!')
        return

    conf = load_conf()
    check_schedule = conf['check']
    timeout = check_schedule['timeout_seconds']

    host, port = check_schedule['host'], check_schedule['port']
    print(timetag(), 'checking ' + f'{host}:{port}')
    try:
        if not is_port_open(host, port, TIMEOUT=timeout):
            msg = f'{host}:{port} is down!'
            bot.send(msg)
        else:
            msg = f'{host}:{port} is open'
            if conf['debug']:
                print('sending msg')
                bot.send(msg)
        print(msg)

    except Exception as e:
        msg = traceback.format_exc()
        print(msg)
        bot.send(msg)


def on_msg(msg):
    global enabled
    if msg.plain == '/check disable':
        enabled = False
        print('disabled!')
        # bot.send_group_msg(group=msg.group, msg='Port check disabled!')
    elif msg.plain == '/check enable':
        enabled = True
        print('enabled!')
        # bot.send_group_msg(group=msg.group, msg='Port check enabled!')

if __name__ == '__main__':
    conf = load_conf()
    bot = wecomsan.WecomSan(**conf['bot'])
    check_port(bot)
