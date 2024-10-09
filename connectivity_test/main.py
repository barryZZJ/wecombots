import wecomsan
from config import load_conf

def report(title, content=None):
    if content is not None:
        msg = f'{title=}\n{content=}'
    else:
        msg = title
    conf = load_conf()
    bot = wecomsan.WecomSan(**conf['bot'])
    bot.send(msg)

if __name__ == '__main__':
    report('test')