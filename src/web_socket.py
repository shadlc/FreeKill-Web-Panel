from flask import Flask
from flask_socketio import SocketIO, emit
import subprocess

socketio = SocketIO()
class SocketAPI:
    @classmethod
    def register(self, app: Flask, route_base: str):
        global socketio
        socketio = SocketIO(app)
        self.route_base = route_base
        
    @socketio.on('input')
    def handle_input(self, input):
        # 在这里执行与终端交互相关的逻辑，例如使用 subprocess 调用 tmux 命令
        output = self.run_terminal_command(input)
        emit('output', output)

    def run_terminal_command(self, command):
        # 使用 subprocess 执行命令
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        
        # 读取命令输出和错误信息
        output, error = process.communicate()
        
        # 解码输出为字符串
        output = output.decode('utf-8')
        error = error.decode('utf-8')
        
        # 返回输出或错误信息
        if output:
            return output
        else:
            return error