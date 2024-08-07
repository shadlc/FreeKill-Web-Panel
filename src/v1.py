import os
import re
import json
import time
from flask import Response
from flask_classful import FlaskView, route, request

from src.utils import restful, isPortBusy, startGameServer, stopGameServer, deleteGameServer, updateGameServer, backupGameServer, getGameServerStat, getGameTransTable, readGameConfig, writeGameConfig, isFileExists, runTmuxCmd, runScreenCmd, appendFile, runCmdCorrect, getSessionPid, getGitTree, getBranchCommits, setPackVersionForServer
from src.game_server import Server
from src.controller import Controller
from src.utils import config

class V1API(FlaskView):
    
    def __init__(self):
        super().__init__()
        self.controller : Controller
    
    @route('/')
    def index(self):
        return 'V1 API'

    @route('servers', methods=['GET'])
    def servers(self):
        server_dict_list = []
        server_list = self.controller.getList()
        for server in server_list:
            server_dict_list.append(server.info(self.controller.server_list))
        return restful(200, '', {'list': server_dict_list})

    @route('details', methods=['GET'])
    def details(self):
        name = request.args.get('name', '')
        server_list = self.controller.getList()
        for server in server_list:
            if server.name == name:
                info_dict = server.details(self.controller.server_list)
                return restful(200, '', info_dict)
        return restful(404, '未找到该服务器')

    @route('player_list', methods=['GET'])
    def player_list(self):
        name = request.args.get('name', '')
        for server in self.controller.list:
            if server.name == name:
                info_dict = server.getPlayerList()
                return restful(200, '', info_dict)
        return restful(404, '未找到该服务器')

    @route('room_list', methods=['GET'])
    def room_list(self):
        name = request.args.get('name', '')
        for server in self.controller.list:
            if server.name == name:
                info_dict = server.getRoomList()
                return restful(200, '', info_dict)
        return restful(404, '未找到该服务器')

    @route('trans_table', methods=['GET'])
    def trans_table(self):
        name = request.args.get('name', '')
        raw = request.args.get('raw', False)
        for server in self.controller.list:
            if server.name == name:
                trans_table = getGameTransTable(server.path, raw)
                return restful(200, '', trans_table)
        return restful(404, '未找到该服务器')

    @route('execute', methods=['POST'])
    def execute(self):
        name = request.json.get('name', '')
        cmd = request.json.get('cmd', '')
        for char in ['`', '"', '$', '\x01']:
            cmd = cmd.replace(char, f'\\{char}')
        server_list = self.controller.getList()
        for server in server_list:
            if server.name == name:
                is_port_busy = isPortBusy(server.port)
                if cmd == 'start' and not is_port_busy:
                    appendFile(f'{server.path}/{config.log_file}', '\x01')
                    time.sleep(0.1)
                    error = server.start()
                    if error:
                        return restful(400, error)
                    self.controller.connection.set(server.name, 'path', server.path)
                    self.controller.connection.set(server.name, 'pid', server.pid)
                    return restful(200, '服务器启动成功')
                elif not is_port_busy:
                    return restful(405, '服务器未启动,请先启动')
                else:
                    if server.session_type == 'tmux':
                        runTmuxCmd(name, cmd)
                    elif server.handled:
                        runScreenCmd(name, cmd)
                    else:
                        return restful(403, '无法与终端交互，请关闭服务器后由本程序接管启动')
                    return restful(200, '')
        return restful(404, '未找到该服务器')
    
    @route('add_server', methods=['POST'])
    def add_server(self):
        name = request.json.get('name', None)
        port = int(request.json.get('port')) if request.json.get('port').isdigit() else None
        path = request.json.get('path', None)
        desc = request.json.get('desc', None)
        icon = request.json.get('icon', None) 
        capacity = int(request.json.get('capacity')) if request.json.get('capacity').isdigit() else None
        temp_ban_time = int(request.json.get('temp_ban_time')) if request.json.get('temp_ban_time').isdigit() else None
        motd = request.json.get('motd', None)
        enable_bots = request.json.get('enable_bots', None)
        if enable_bots != None:
            enable_bots = bool(enable_bots)
        session_type = request.json.get('session_type', None)
        
        server_list = self.controller.getList()
        if not name:
            return restful(405, f'服务器名称不能为空')
        elif not port:
            return restful(405, f'服务器端口无效')
        elif not path:
            return restful(405, f'服务器启动路径不能为空')
        elif name in [server.name for server in server_list]:
            return restful(409, f'该服务器名称重名：{name}')
        elif match := re.search(r'([<>:;"/\\\|\?\*\x00-\x1F\x7F\'\`\s])', name):
            result = match.groups()[0]
            return restful(409, f'该服务器名称存在不可用字符：<{result}>')
        elif isPortBusy(port):
            return restful(409, f'该端口已被占用：{port}')
        elif port < 1025 or port > 65535:
            return restful(409, f'该端口不可用：{port}')
        elif not isFileExists(os.path.join(path,'FreeKill')):
            return restful(409, f'该路径无效\n确保该路径下存在可执行的“FreeKill”文件')
        elif match := re.search(r'([<>:;"\\|\?\*\x00-\x1F\x7F\'\`\s])', path):
            result = match.groups()[0]
            return restful(409, f'该服务器路径存在不可用字符：<{result}>')
        elif path in [server.path for server in server_list]:
            return restful(409, f'该路径已经启动了一个服务器')
        elif session_type not in ['tmux', 'screen']:
            return restful(409, f'本程序仅支持启动tmux或screen服')
        elif session_type == 'tmux' and not runCmdCorrect('tmux -V'):
            return restful(409, f'服务器未安装tmux，无法以此方式启动')
        elif session_type == 'screen' and not runCmdCorrect('screen -v'):
            return restful(409, f'服务器未安装screen，无法以此方式启动')

        if e := writeGameConfig(path, {
            "description": desc,
            "iconUrl": icon,
            "capacity": capacity,
            "tempBanTime": temp_ban_time,
            "motd": motd,
            "enableBots": enable_bots,
        }):
            return restful(400, f'服务器配置写入错误，启动失败：\n{e}')
        pid = startGameServer(name, port, path, session_type)
        if pid == 0:
            return restful(400, '服务器启动失败，请联系管理员')
        server = Server()
        if session_type == 'tmux':
            server.init(name, port, path=path, session_type=session_type)
        else:
            spid = getSessionPid(pid)
            server.init(f'{spid}.{name}', port, path=path, session_type=session_type)
        self.controller.add(server)
        return restful(200, f'服务器已添加并启动')

    @route('start_server', methods=['POST'])
    def start_server(self):
        server_name = request.json.get('name', '')
        server_list = self.controller.getList()
        for server in server_list:
            if server.name == server_name:
                if isPortBusy(server.port):
                    return restful(405, '服务器已经在运行中')
                appendFile(f'{server.path}/{config.log_file}', '\x01')
                time.sleep(0.1)
                error = server.start()
                if error:
                    return restful(400, error)
                if server.session_type == 'screen':
                    self.controller.remove(server)
                    self.controller.add(server)
                    data = {'redirect': True, 'name': server.name}
                else:
                    data = {}
                self.controller.connection.set(server.name, 'path', server.path)
                self.controller.connection.set(server.name, 'pid', server.pid)
                return restful(200, '服务器启动成功', data)

        return restful(404, '无法找到该服务器')

    @route('stop_server', methods=['POST'])
    def stop_server(self):
        server_name = request.json.get('name', '')
        server_list = self.controller.getList()
        for server in server_list:
            if server.name == server_name:
                if not isPortBusy(server.port):
                    return restful(405, '服务器已经是停止状态')
                if server.name == server_name and stopGameServer(server.name, server.session_type):
                    return restful(200, '服务器停止成功')

        return restful(404, '无法找到该服务器')

    @route('del_server', methods=['POST'])
    def del_server(self):
        server_name = request.json.get('name', '')
        list = self.controller.getList()
        for server in list:
            if server.name == server_name:
                if isPortBusy(server.port):
                    return restful(405, '请先停止该服务器')
                if e := deleteGameServer(server_name):
                    return restful(400, e)
                self.controller.remove(server)
                self.controller.refreshConfig()
                return restful(200, '已删除该服务器')

        return restful(404, '无法找到该服务器')

    @route('update_server', methods=['GET'])
    def update_server(self):
        server_name = request.args.get('name', '')
        for server in self.controller.getList():
            if server.name == server_name:
                if isPortBusy(server.port):
                    return Response(f'event: message\ndata: 只能在服务器未运行时更新\n\n', mimetype='text/event-stream')
                return Response(updateGameServer(server_name), mimetype='text/event-stream')

        return Response('event: message\ndata: 无法找到该服务器\n\n', mimetype='text/event-stream')

    @route('config', methods=['GET', 'POST'])
    def config(self):
        if request.method == 'GET':
            server_name = request.args.get('name', '')
            server_list = self.controller.getList()
            for server in server_list:
                if server.name == server_name:
                    result, config = readGameConfig(server.path)
                    if result:
                        return restful(200, '', {'config': config})
                    else:
                        return restful(500, f'服务器<{server_name}>配置文件读取出错，目录为：'
                                    f'\n{server.path}/freekill.server.config.json')
        elif request.method == 'POST':
            server_name = request.json.get('name', '')
            config_text = request.json.get('config', '')
            # 不解析直接覆写配置文件
            config = config_text
            server_list = self.controller.getList()
            for server in server_list:
                if server.name == server_name:
                    e = writeGameConfig(server.path, config)
                    if e:
                        return restful(500, f'{e}')
                    else:
                        return restful(200, f'服务器<{server_name}>配置文件修改成功\n重启后生效')
            

        return restful(404, '无法找到该服务器')

    @route('modify', methods=['POST'])
    def modify(self):
        server_name = request.json.get('name', '')
        server_port = int(request.json.get('port')) if request.json.get('port').isdigit() else 0
        for server in self.controller.getList():
            if server.name == server_name:
                if isPortBusy(server.port):
                    return restful(405, f'只能在服务器未运行时操作')
                elif server_port:
                    if not server_port:
                        return restful(405, f'服务器端口无效')
                    elif isPortBusy(server_port):
                        return restful(409, f'该端口已被占用：{server_port}')
                    elif server_port < 1025 or server_port > 65535:
                        return restful(409, f'该端口不可用：{server_port}')
                    server.port = server_port
                    self.controller.modifyDict(server_name, 'port', server_port)
                    return restful(200, f'服务器<{server_name}>端口号修改成功')
                else:
                    return restful(405, '该值无效')

        return restful(404, '无法找到该服务器')

    @route('backup', methods=['POST'])
    def backup(self):
        server_name = request.json.get('name', '')
        for server in self.controller.getList():
            if server.name == server_name:
                result, msg = backupGameServer(server.path)
                if result:
                    return restful(200, f'服务器<{server_name}>备份成功\n{msg}')
                else:
                    return restful(500, f'服务器<{server_name}>备份失败\n{msg}')

        return restful(404, '无法找到该服务器')

    @route('statistics', methods=['GET'])
    def statistics(self):
        server_name = request.args.get('name', '')
        list = self.controller.getList()
        for server in list:
            if server.name == server_name:
                result, data = getGameServerStat(server.path)
                if result:
                    return restful(200, '', data)
                else:
                    return restful(500, f'获取服务器<{server_name}>统计数据失败，原因：<br>{data}')

        return restful(404, '无法找到该服务器')

    @route('set_pack_version', methods=['GET'])
    def set_pack_version(self):
        server_name = request.args.get('name', '')
        pack_code = request.args.get('code', '')
        pack_branch = request.args.get('branch', '')
        pack_hash = request.args.get('hash', '')
        illegal_char = r'([<>:;"/\\\|\?\*\x00-\x1F\x7F\'\`\s])'
        if match := re.search(illegal_char, server_name):
            result = match.groups()[0]
            return Response(
                f'event: message\ndata: 切换失败，服务器名存在非法字符：<{result}>\n\n',
                mimetype='text/event-stream'
            )
        elif match := re.search(illegal_char, pack_code):
            result = match.groups()[0]
            return Response(
                f'event: message\ndata: 切换失败，包名存在非法字符：<{result}>\n\n',
                mimetype='text/event-stream'
            )
        elif match := re.search(illegal_char, pack_branch):
            result = match.groups()[0]
            return Response(
                f'event: message\ndata: 切换失败，包版本存在非法字符：<{result}>\n\n',
                mimetype='text/event-stream'
            )
        elif match := re.search(illegal_char, pack_hash):
            result = match.groups()[0]
            return Response(
                f'event: message\ndata: 切换失败，包分支存在非法字符：<{result}>\n\n',
                mimetype='text/event-stream'
            )
        list = self.controller.getList()
        for server in list:
            if server.name == server_name:
                return Response(
                    setPackVersionForServer(server.path, pack_code, pack_branch, pack_hash)
                    , mimetype='text/event-stream'
                )

        return Response('event: message\ndata: 无法找到该服务器\n\n', mimetype='text/event-stream')

    @route('check_version', methods=['GET'])
    def check_version(self):
        check_type = request.args.get('type', '')
        if check_type == 'FreeKill':
            version = self.controller.checkFKVersion()
            if version:
                return restful(200, '', {'version': version})
            else:
                return restful(400, f'获取FreeKill最新版本号时发生网络错误', {'version': '未知版本'})

        return restful(404, '无法解析该请求')

    @route('get_git_tree', methods=['GET'])
    def get_git_tree(self):
        git_url = request.args.get('url', '')
        token = request.args.get('token', '')
        if git_url:
            result, data = getGitTree(git_url, token)
            if result:
                return restful(200, '', data)
            else:            
                return restful(400, f'获取拓展包失败！原因：<br>{data}')

        return restful(404, '无法解析该请求')

    @route('get_branch_commits', methods=['GET'])
    def get_branch_commits(self):
        git_url = request.args.get('url', '')
        branch = request.args.get('hash', '')
        token = request.args.get('token', '')
        if git_url:
            result, data = getBranchCommits(git_url, branch, token, parse=True)
            if result:
                return restful(200, '', data)
            else:            
                return restful(400, f'获取拓展包失败！原因：<br>{data}')

        return restful(404, '无法解析该请求')
