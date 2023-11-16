from platform import system
from flask import Flask, render_template, request
from flask_socketio import SocketIO

from src.utils import runCmd
from src.v1 import V1API
from src.game_server import ServerList

app = Flask(__name__, static_folder='static', static_url_path='/')
app.json.ensure_ascii = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/control/<pid>')
def control(pid: str):
    return render_template(f'control.html')

if __name__ == '__main__':
    if system() not in ['Linux']:
        print('不支持该平台')
    elif not runCmd('tmux -V 2>/dev/null'):
        print('未检测到tmux，请安装后继续')
    else:
        server_list = ServerList()
        V1API.register(app, route_base='/v1')
        V1API.server_list = server_list
        app.run('127.0.0.1', 9500)
