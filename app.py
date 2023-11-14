from flask import Flask, render_template
from flask_socketio import SocketIO

from src.v1 import V1API
from src.web_socket import SocketAPI
from src.game_server import ServerList

app = Flask(__name__, static_folder='lib', static_url_path='/lib')
app.json.ensure_ascii = False
#socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/control/<pid>')
def control(pid: str):
    return render_template('control.html')

if __name__ == '__main__':
    # socketio.run(app, '0.0.0.0', 9500, debug=True)
    server_list = ServerList()
    V1API.register(app, route_base='/v1')
    V1API.server_list = server_list
    app.run('0.0.0.0', 9500)
    #app.run('0.0.0.0', 9500, debug=True)
