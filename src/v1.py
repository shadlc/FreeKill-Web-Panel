import re
import time
from flask_classful import FlaskView, route, request

from src.utils import restful, isPortBusy, startGameServer, stopGameServer, deleteGameServer, writeGameConfig, isFileExists, runTmuxCmd, appendFile
from src.game_server import Server, ServerList

class V1API(FlaskView):
    
    def __init__(self):
        super().__init__()
        self.server_list : ServerList
    
    @route('/')
    def index(self):
        return 'V1 API'

    @route('servers', methods=['GET'])
    def servers(self):
        server_dict_list = []
        list = self.server_list.getList()
        for server in list:
            server_dict_list.append(server.info())
        return restful(200, '', {'list': server_dict_list})

    @route('details', methods=['POST'])
    def details(self):
        name = request.json.get('name', '')
        for server in self.server_list.list:
            if server.name == name:
                info_dict = server.details()
                return restful(200, '', info_dict)
        return restful(404, '未找到该服务器')

    @route('execute', methods=['POST'])
    def execute(self):
        name = request.json.get('name', '')
        cmd = request.json.get('cmd', '')
        for char in ['`', '"', '$']:
            cmd = cmd.replace(char, f'\\{char}')
        list = self.server_list.getList()
        for server in list:
            if server.name == name:
                if cmd == 'start' and not isPortBusy(server.port):
                    appendFile(f'{server.path}/fk-latest.log', '\x02')
                    time.sleep(0.1)
                    error = server.start()
                    if error:
                        return restful(400, error)
                    self.server_list.connection.set(server.name, 'path', server.path)
                    return restful(200, '服务器启动成功')
                else:
                    runTmuxCmd(f'FreeKill-{name}', cmd)
                    return restful(200, '')
        return restful(404, '未找到该服务器')
    
    @route('add_server', methods=['POST'])
    def add_server(self):
        name = request.json.get('name', '')
        port = int(request.json.get('port')) if request.json.get('port').isdigit() else 0
        path = request.json.get('path', '')
        desc = request.json.get('desc', '')
        icon = request.json.get('icon', '') 
        capacity = int(request.json.get('capacity')) if request.json.get('capacity').isdigit() else 0
        temp_ban_time = int(request.json.get('temp_ban_time')) if request.json.get('temp_ban_time').isdigit() else 20
        motd = request.json.get('motd', '')
        enable_bots = bool(request.json.get('enable_bots', True))
        
        list = self.server_list.getList()
        if not name:
            return restful(400, f'服务器名称不能为空')
        elif not port:
            return restful(400, f'服务器端口无效')
        elif not path:
            return restful(400, f'服务器启动路径不能为空')
        elif not capacity:
            return restful(400, f'服务器最大人数值无效')
        elif not capacity:
            return restful(400, f'服务器最大人数值无效')
        elif name in [server.name for server in list]:
            return restful(409, f'该服务器名称重名：{name}')
        elif match := re.search(r'([<>:;"/\\\|\?\*\x00-\x1F\x7F\'\`\s])', name):
            result = match.groups()[0]
            return restful(409, f'该服务器名称存在不可用字符：<{result}>')
        elif isPortBusy(port):
            return restful(409, f'该端口已被占用：{port}')
        elif port < 1025 and port > 65535:
            return restful(409, f'该端口不可用：{port}')
        elif not isFileExists(f'{path}/FreeKill'):
            return restful(409, f'该路径无效')
        elif match := re.search(r'([<>:;"\\|\?\*\x00-\x1F\x7F\'\`\s])', path):
            result = match.groups()[0]
            return restful(409, f'该服务器路径存在不可用字符：<{result}>')
        elif path in [server.path for server in list]:
            return restful(409, f'该路径已经启动了一个服务器')

        if e := writeGameConfig(path, {
            "description": desc,
            "iconUrl": icon,
            "capacity": capacity,
            "tempBanTime": temp_ban_time,
            "motd": motd,
            "enableBots": enable_bots,
        }):
            return restful(400, f'服务器配置写入错误，启动失败：{e}')
        pid = startGameServer(name, port, path)
        if pid == 0:
            return restful(400, '服务器启动失败，请联系管理员')
        server = Server()
        server.init(name, port, path=path)
        self.server_list.add(server)
        return restful(200, f'服务器已添加并启动')

    @route('start_server', methods=['GET'])
    def restart_server(self):
        server_name = request.args.get('name', '')
        list = self.server_list.getList()
        for server in list:
            if server.name == server_name:
                if isPortBusy(server.port):
                    return restful(400, '服务器已经在运行中')
                error = server.start()
                if error:
                    return restful(400, error)
                return restful(200, '服务器启动成功')

        return restful(400, '服务器启动失败，该端口可能已被占用')

    @route('stop_server', methods=['GET'])
    def stop_server(self):
        server_name = request.args.get('name', '')
        list = self.server_list.getList()
        for server in list:
            if not isPortBusy(server.port):
                return restful(400, '服务器已经是停止状态')
            if server.name == server_name and stopGameServer(server.name):
                return restful(200, '服务器停止成功')

        return restful(400, '服务器停止失败')

    @route('del_server', methods=['GET'])
    def del_server(self):
        server_name = request.args.get('name', '')
        list = self.server_list.getList()
        for server in list:
            if server.name == server_name:
                if isPortBusy(server.port):
                    return restful(400, '请先停止该服务器')
                if e := deleteGameServer(server_name):
                    return restful(400, e)
                self.server_list.remove(server)
                self.server_list.refreshConfig()
                return restful(200, '已删除该服务器')

        return restful(404, '无法找到该服务器')

    @route('check_version', methods=['GET'])
    def del_server(self):
        check_type = request.args.get('type', '')
        if check_type == 'FreeKill':
            version = self.server_list.checkFKVersion();
            if version:
                return restful(200, '', {'version': version})
            else:
                return restful(400, f'获取FreeKill最新版本号时发生网络错误', {'version': '未知版本'})

        return restful(404, '无法解析该请求')