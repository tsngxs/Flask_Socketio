from threading import Lock
import psutil
import time
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit
import random

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = random.random()
socketio = SocketIO(app, async_mode=async_mode)

thread = None
thread_lock = Lock()

''' 后台线程 生产数据 立即推送至前端'''


def backgroud_thread():
    count = 0
    while True:
        socketio.sleep(2)
        count += 1
        t = time.strftime('%M:%S', time.localtime())
        cpus = psutil.cpu_percent(interval=None, percpu=True)
        socketio.emit('server_response', {'data': [t, *cpus], 'count': count}, namespace='/test')


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


'''与前端建立socket连接并启动线程'''


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=backgroud_thread)


if __name__ == '__main__':
    socketio.run(app, port=8888, debug=True)
