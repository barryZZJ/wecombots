from flask import Flask, request, jsonify
import wecomsan
from config import load_conf


app = Flask(__name__)


@app.route('/', methods=['POST'])
def receive_post():
    try:
        # print(request.form)
        # ([('task_id', 'as1ji3zk8'),
        # ('task_title', 'Twitter @Barry'),
        # ('text', '测试2'),
        # ('title', '测试2'),
        # ('link', 'https://twitter.com/850462618Doe/status/1661768883538391050'),
        # ('desp', '测试2')])
        title = request.form.get('title')
        desp = request.form.get('desp')
        link = request.form.get('link')
        task_id = request.form.get('task_id')
        task_title = request.form.get('task_title')

        redirect(title, desp, link, task_id, task_title)
        return jsonify({'message': 'Success'})

    except Exception as e:
        print('error', str(e))
        return jsonify({'error': str(e)}), 500


def redirect(title, desp, link, task_id, task_title):
    # redirect to wecomchan
    if 'テレビ王国' in task_title:
        msg = f'来自{task_title}的更新：\n标题：{title}\n内容：\n{desp}\n查看详情：{link}'
    else:
        msg = f'来自{task_title}的更新：\n标题：{title}\n<a href="{link}">查看详情</a>'
    
    conf = load_conf()
    bot = wecomsan.WecomSan(**conf['bot'])
    bot.send(msg)


if __name__ == '__main__':
    app.run(port=12345)
