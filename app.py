from platform import system
from flask import Flask, render_template, request
from flask_socketio import SocketIO

from src.utils import runCmd, tailLog, queryPerf
from src.v1 import V1API
from src.game_server import Controller
from src.connection import Connection

app = Flask(__name__, static_folder='static', static_url_path='/')
app.json.ensure_ascii = False
socketio = SocketIO(app, async_mode='gevent', cors_allowed_origins="*")

conn = Connection(socketio)
controller = Controller()
controller.connection = conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/control/<name>')
def control(name: str):
    return render_template(f'control.html')

@socketio.on('connect')
def connect():
    req_name = request.args.get('name', '')
    if not conn.contains(request.sid):
        conn.add(request.sid, req_name)
        socketio.start_background_task(tailLog, conn, request.sid)
        socketio.start_background_task(queryPerf, conn, request.sid)

@socketio.on('disconnect')
def disconnect():
    conn.remove(request.sid)

if __name__ == '__main__':
    if system() not in ['Linux']:
        print('不支持该平台')
    elif not runCmd('tmux -V 2>/dev/null'):
        print('未检测到tmux，请安装后继续')
    else:
        V1API.register(app, route_base='/v1')
        V1API.controller = controller
        socketio.run(app, '127.0.0.1', 9500, debug=True)