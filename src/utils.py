import os
import re
import sys
import json
import time
import base64
import psutil
import socket
import logging
import sqlite3
import requests
import subprocess

from flask import jsonify
from src.connection import Connection

config_file = f'./config.json'

logging.getLogger().name = 'utils'
if '--debug' in sys.argv[1:]:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

hasTmux = None
hasScreen = None

# 从指定图片链接获取base64格式的图片数据并返回
def getImgBase64FromURL(url: str) -> str:
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            image_data = response.content
            base64_data = 'data:image/png;base64,' + base64.b64encode(image_data).decode('utf-8')
            return base64_data
        return ''
    except Exception as e:
        logging.error(e)
        return ''

# 取得FreeKill最新版本
def getFKVersion() -> str | None:
    try:
        url = 'https://github.com/Qsgs-Fans/FreeKill/releases/latest'
        response = requests.get(url)
        if response.status_code == 200:
            version = response.url.split('/').pop()
            return version
        return
    except Exception as e:
        logging.error(e)
        return

# 从CMakeList.txt中获取游戏版本
def getVersionFromPath(path: str) -> str:
    try:
        with open(f'{path}/CMakeLists.txt', 'r') as file:
            content = file.read()

        # 使用正则表达式匹配版本号
        pattern = r'(?<=FreeKill\sVERSION\s)([^\)]*)'
        match = re.search(pattern, content)
        if match:
            version = match.group()
            return f'v{version}'
    except Exception as e:
        logging.error(e)
    return ''

# 运行Bash指令并获取结果
def runCmd(cmd: str, log=True) -> str:
    try:
        stime = time.time()
        comm = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
        stdout, stderr = comm.communicate()
        etime = time.time()
        if log:
            logging.debug(f' >>> 耗时({round(etime - stime, 3)})执行指令 {cmd}')
        if stderr:
            logging.info(f' >>> 执行上述指令出错：{stderr}')
        if stdout:
            return stdout.strip()
        else:
            return 'ok'
    except Exception as e:
        logging.error(f'执行外部指令出错：{e}')
        return ''

# 运行Bash指令并判断是否成功
def runCmdCorrect(cmd: str, log=True) -> bool:
    stime = time.time()
    try:
        result = subprocess.run(f'{cmd}', shell=True, capture_output=True, text=True)
        etime = time.time()
        if log:
            logging.debug(f' >>> 耗时({round(etime - stime, 3)})执行指令 {cmd}')
        if result.returncode != 0:
            raise EOFError(result.stderr)
        return True
    except Exception as e:
        logging.debug(f'执行外部指令不成功：{e}')
        return False

# 从指定PID进程获取其运行时长
def getProcessUptime(pid: int) -> str:
    uptime = 0
    try:
        process = psutil.Process(pid)
        uptime = process.create_time()
        uptime = psutil.time.time() - uptime
    except psutil.NoSuchProcess:...
    return uptime

# 获取正在运行的FreeKill服务器列表以及其信息
def getServerList() -> list[str]:
    global hasTmux, hasScreen
    spid_dict = {}
    # 获取tmux列表
    if hasTmux == None:
        hasTmux = runCmdCorrect('tmux -V')
    if hasScreen == None:
        hasScreen = runCmdCorrect('screen -v')
    if hasTmux:
        command = ''' tmux ls -F "#{pane_pid} #{session_name}" 2>/dev/null '''
        spid_name = runCmd(command)
        spid_list = [i.split(' ') for i in [j for j in spid_name.split('\n')]]
        spid_dict.update({int(i[0]): [i[1], 'tmux'] for i in spid_list if len(i) > 1})
    # 获取screen列表
    if hasScreen:
        command = ''' screen -ls | sed '1d;$d' | awk '{print $1}' | sed -E 's/\.([^.]*)/ \\1/' '''
        spid_name = runCmd(command)
        spid_list = [i.split(' ') for i in [j for j in spid_name.split('\n')]]
        spid_dict.update({int(i[0]): [f'{i[0]}.{i[1]}', 'screen'] for i in spid_list if len(i) > 1})

    spid_pid_port_list = []
    try:
        for process in psutil.process_iter():
            cmd = process.cmdline()
            if './FreeKill' in cmd and '-s' in cmd and 'SCREEN' not in cmd:
                port = int(cmd[2]) if len(cmd) > 2 and cmd[2].isdigit() else ''
                spid_pid_port_list.append([getSessionPid(process.ppid()), process.pid, port])
    except psutil.NoSuchProcess:...

    server_list = []
    for item in spid_pid_port_list:
        spid = item[0]
        pid = item[1]
        port = item[2]
        if spid in spid_dict:
            name = spid_dict[spid][0]
            session_type = spid_dict[spid][1]
            server_list.append([name, pid, port, session_type])
    return server_list

# 根据PID获取该程序所属的Tmux或则Screen的PID
def getSessionPid(pid: int, recursion: bool=True) -> int:
    if pid == 1 or pid == 0:
        return 0
    try:
        for process in psutil.process_iter():
            if pid == process.pid:
                cmd = process.cmdline()
                if 'SCREEN' in cmd:
                    return process.pid
                elif 'bash' in cmd or '-bash' in cmd:
                    session_pid = getSessionPid(process.ppid(), False)
                    if session_pid:
                        return session_pid
                    return process.pid
                elif recursion:
                    return getSessionPid(process.ppid())
    except psutil.NoSuchProcess:...
    return 0

# 根据PID判断该程序是否是FKWP启动的
def isHandledByPid(pid: int) -> bool:
    if pid == 1 or pid == 0:
        return False
    try:
        for process in psutil.process_iter():
            if pid == process.pid:
                cmd = process.cmdline()
                if 'tee ./fk-latest.log' in ' '.join(cmd):
                    return True
                else:
                    return isHandledByPid(process.ppid())
    except psutil.NoSuchProcess:...
    return False

# 通过PID获取程序的执行路径
def getProcPathByPid(pid: int) -> str:
    try:
        process = psutil.Process(pid)
        path = process.exe()
        if '/build/FreeKill' in path:
            path = path.rsplit('/', 1)[0].rstrip('build').rstrip('/')
        return path
    except psutil.NoSuchProcess:
        return ''

# 通过PID获取程序的监听端口
def getProcPortByPid(pid: int) -> int:
    for conn in psutil.net_connections():
        if conn.status == 'LISTEN' and conn.pid == pid:
            return conn.laddr.port
    return 0

# 判断端口号是否是被占用
def isPortBusy(port: int) -> bool:
    for conn in psutil.net_connections():
        if conn.status == 'LISTEN' and conn.laddr.port == port:
            return True
    return False

# 判断某文件是否存在
def isFileExists(path: str) -> bool:
    try: open(path)
    except: return False
    return True

# 获取保存的历史服务器列表
def getServerFromConfig() -> dict:
    if not isFileExists(config_file):
        json.dump({'server_dict': {}}, open(config_file, 'w'), ensure_ascii=False)
    json_data = json.load(open(config_file)).get('server_dict')
    return json_data

# 保存历史服务器列表
def saveServerToConfig(server_dict: list[str]) -> str:
    try:
        json_data = json.load(open(config_file))
        json_data['server_dict'] = server_dict
        json.dump(json_data, open(config_file, 'w'), ensure_ascii=False, indent=2)
    except Exception as e:
        return f'保存配置文件发生错误\n {e}'
    return ''

# 以RESTful的方式进行返回响应
def restful(code: int, msg: str = '', data: dict = {}) -> None:
    retcode = 1
    if code == 200:
        retcode = 0
    return jsonify({'code': code,
            'retcode': retcode,
            'msg': msg,
            'data': data
    }), code

# 启动服务器,返回PID
def startGameServer(name: str, port: int, path: str, session_type: str) -> int:
    if session_type == 'tmux':
        command = f''' cd {path}; tmux new -d -s "{name}" "./FreeKill -s {port} 2>&1 | tee ./fk-latest.log" '''
    else:
        name = name.split(".", 1).pop()
        command = f''' cd {path}; screen -dmS "{name}" bash -c "./FreeKill -s {port} 2>&1 | tee ./fk-latest.log" '''
    logging.debug(f' >>> 独立进程   执行指令 {command}')
    subprocess.Popen([command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).wait()
    time.sleep(0.5)
    try:
        for process in psutil.process_iter():
            cmd = process.cmdline()
            if './FreeKill' in cmd and '-s' in cmd and f'{port}' in cmd:
                return process.pid
    except psutil.NoSuchProcess:...
    return 0

# 停止服务器
def stopGameServer(name: str, session_type: str) -> bool:
    if session_type == 'tmux':
        command = f''' tmux send-keys -t "{name}" C-d '''
    else:
        command = f''' screen -S {name} -X stuff "\004\004" '''
    result = runCmd(command)
    print(result)
    if result != '':
        return True
    return False

# 删除服务器
def deleteGameServer(server_name: str) -> str:
    server_dict = getServerFromConfig()
    del_name = ''
    for name in server_dict:
        if name == server_name:
            del_name = name
    if del_name:
        server_dict.pop(del_name)
        return saveServerToConfig(server_dict)
    return '服务器已经不存在'

# 更新服务器
def updateGameServer(server_name: str) -> str:
    server_path = ''
    server_dict = getServerFromConfig()
    for name in server_dict:
        if name == server_name:
            server_path = server_dict[name][1]
    update_cmd = f'''
        cd {server_path} \
        && echo "正在读取最新版本...\n" \
        && git reset --hard 2>&1 \
        && git pull --tags origin master 2>&1 \
        && latest_tag=$(git describe --tags `git rev-list --tags --max-count=1`) 2>&1 \
        && git checkout $latest_tag 2>&1 \
        && echo "\n正在编译...\n" \
        && ([ -f include/lua.h ] || cp -r /usr/include/lua5.4/* include) \
        && ([ -d build ] || mkdir build) \
        && cd build \
        && cmake .. \
        && make \
        && cd .. \
        && ([ -f FreeKill ] || ln -s build/FreeKill)
    '''
    logging.debug(f' >>> 独立进程   执行指令' + update_cmd.replace('\n', '').replace('    ',''))
    process = subprocess.Popen(update_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
    while True:
        output = process.stdout.readline()
        if output:
            yield f'event: message\ndata: {output}\n\n'
        elif process.poll() is not None:
            if process.poll() == 0:
                yield f'event: message\ndata: <span class="green">服务器更新成功</span>\n\n'
            else:
                yield f'event: message\ndata: <span class="red">服务器更新失败，错误码：{process.poll()}</span><br>\n\n'
            return
# 读取游戏配置文件
def readGameConfig(path: str) -> [bool, str]:
    try:
        with open(f'{path}/freekill.server.config.json') as f:
            config_text = f.read()
        return True, config_text
    except Exception as e:
        return False, e

# 写入游戏配置文件
def writeGameConfig(path: str, config: dict) -> str | None:
    try:
        config_json = json.load(open(f'{path}/freekill.server.config.json'))
        for key in config:
            if config[key]:
                config_json[key] = config[key]
        json.dump(config_json, open(f'{path}/freekill.server.config.json', 'w'), ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(e)
        return e

# 在指定screen内执行语句，并获取返回值
def runScreenCmd(name: str, cmd: str, path: str='') -> str:
    command = command = f' screen -S {name} -X stuff "{cmd}\n" '
    if not path:
        return runCmd(command)
    log_file = f'{path}/fk-latest.log'
    with open(log_file) as f:
        f.seek(0, 2)
        runCmd(command)
        time.sleep(0.1)
        result = rmSpecialChar(f.read())
    return result

# 在指定tmux内执行语句，并对Tmux窗口进行内容捕获
def runTmuxCmd(name: str, cmd: str) -> str:
    command = f' tmux send-keys -t {name} "{cmd}" Enter;sleep 0.1;tmux capture-pane -peS - -t {name} 2>&1'
    result = runCmd(command)
    return result

# 使用UDP协议获取指定服务器信息
def getServerInfo(name: str, port : int) -> list:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('127.0.0.1', port)
    try:
        message = 'fkGetDetail,127.0.0.1'
        sock.sendto(message.encode(), server_address)
        data, address = sock.recvfrom(10240)
        server_data = json.loads(data.decode())
        return server_data
    except Exception as e:
        logging.error(f'UDP连接服务器[{name}](127.0.0.1:{port})失败：{e}')
    finally:
        sock.close()
    return []

# 获取指定服务器内在线玩家列表
def getPlayerList(name: str, session_type: str, path: str) -> dict:
    if session_type == 'tmux':
        captured = runTmuxCmd(name, 'lsplayer')
    else:
        captured = runScreenCmd(name, 'lsplayer', path)
    if captured and 'lsplayer\n' in captured:
        player_text = captured.rsplit('lsplayer\n', 1)[1]
    else:
        player_text = ''
    player_dict = {}
    if re.search(r'Current (.*) online player\(s\)', player_text):
        for line in player_text.split('\n'):
            if match := re.search(r' ([0-9]+) , "(.*)"', line):
                index = match.groups()[0]
                name = match.groups()[1]
                player_dict[int(index)] = name
    return player_dict

# 获取指定服务器内已房间列表
def getRoomList(name: str, session_type: str, path: str) -> dict:
    if session_type == 'tmux':
        captured = runTmuxCmd(name, 'lsroom')
    else:
        captured = runScreenCmd(name, 'lsroom', path)
    if captured and 'lsroom\n' in captured:
        room_text = captured.rsplit('lsroom\n', 1)[1]
    else:
        room_text = ''
    room_dict = {}
    if match := re.search(r'Current (.*) running rooms are', room_text):
        for line in room_text.split('\n'):
            if match := re.search(r' ([0-9]+) , "(.*)"', line):
                index = match.groups()[0]
                name = match.groups()[1]
                room_dict[int(index)] = name
    return room_dict

# 获取指定服务器扩充包
def getPackList(path: str) -> dict:
    pack_dict = getPackListFromDir(os.path.join(path, 'packages'))
    trans_dict = {
        'mobile_effect': '手杀特效',
        'utility': '常用函数',
    }
    try:
        db_file = os.path.join(path, 'packages/packages.db')
        logging.debug(f'读取数据库 {db_file}')
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM packages')
        pack_list: list[tuple] = cursor.fetchall()
        db_pack_dict = {pack[0]: pack[1:] for pack in pack_list}
        for name in db_pack_dict:
            package = {
                'url': db_pack_dict[name][0],
                'hash': db_pack_dict[name][1],
                'enabled': db_pack_dict[name][2],
            }
            if name in pack_dict:
                pack_dict[name].update(package)
            else:
                pack_dict[name] = package
                pack_dict[name]['name'] = trans_dict.get(name, name)
        return pack_dict
    except Exception as e:
        logging.error(f'读取扩充包数据库发生错误：{e}')
        return pack_dict

# 向指定服务器封禁玩家
def banFromServer(server_name: str, player_name: str, session_type: str, path: str) -> bool:
    if session_type == 'tmux':
        captured = runTmuxCmd(server_name, f'ban {player_name}')
    else:
        captured = runScreenCmd(server_name, f'ban {player_name}', path)
    result_text = captured.rsplit('ban\n', 1)[1]
    if re.search(r'Running command:', result_text):
        return True
    return False

# 向指定服务器发送消息
def sendMsgTo(name: str, msg: str, session_type: str, path: str) -> bool:
    if session_type == 'tmux':
        captured = runTmuxCmd(name, f'msg {msg}')
    else:
        captured = runScreenCmd(name, f'msg {msg}', path)
    result_text = captured.rsplit('msg\n', 1)[1]
    if re.search(r'Banned', result_text):
        return True
    return False

# 去除特殊控制字符
def rmSpecialChar(text: str) -> str:
    special_chars = ['[?2004l', '[?2004h', '\x1b[K', '\x1b']
    for char in special_chars:
        text = text.replace(char, '')
    return text

# 获取指定文件倒数行数的文本
def tailLogNum(file_path: str, num: int) -> str:
    try:
        with open(file_path) as file:
            lines = file.readlines()
            last_lines = lines[-num:]
            text = ''
            for line in last_lines:
                if rmSpecialChar(line).strip():
                    text += line
            text = rmSpecialChar(text)
            return text
    except:
        return ''

# 根据连接客户端实时获取执行日志
def tailLog(conn: Connection, sid: str) -> None:
    try:
        date = time.strftime('%m/%d %H:%M:%S', time.localtime())
        name = conn.clients[sid].get('name')
        path = ''
        handled = False
        server_list = getServerList()
        for server in server_list:
            if name == server[0]:
                path = getProcPathByPid(server[1])
                handled = isHandledByPid(server[1])
        server_dict = getServerFromConfig()
        if path == '':
            if name not in server_dict:
                conn.socketio.emit('terminal', {'text': f'{date} FKWP [[0;31mE[0;0m] 服务器无效\n'})
                return
            conn.socketio.emit('terminal', {'text': f'{date} FKWP [[0;33mI[0;0m] 服务器未启动，输入指令[0;33m start [0;0m启动服务器\n'})
        elif not handled:
            conn.socketio.emit('terminal', {'text': f'{date} FKWP [[0;33mW[0;0m] 服务器不是由本程序接管启动，只能进行其他操作，无法与终端交互，请关闭服务器后由本程序接管启动，再刷新本页面实现与终端交互\n'})
            while conn.contains(sid):
                time.sleep(1)
        while conn.contains(sid) and not path and not conn.clients[sid].get('path'):
            time.sleep(0.1)
            continue
        if temp_path := conn.clients[sid].get('path'):
            path = temp_path

        log_file = f'{path}/fk-latest.log'
        conn.socketio.emit('terminal', {'text': tailLogNum(log_file, 1000), 'history': True})
        with open(log_file) as f:
            f.seek(0, 2)
            while conn.contains(sid):
                line = rmSpecialChar(f.readline())
                if not line:
                    time.sleep(0.1)
                    continue
                elif re.match(r'^(\n|\^@|\x07|\x02)*$', line):
                    continue
                elif line == '\x01':
                    conn.socketio.emit('terminal', {'text': f'{date} FKWP [[0;32mI[0;0m] 正在启动中...\n', 'start': True})
                    time.sleep(0.5)
                    f = open(log_file)
                else:
                    conn.socketio.emit('terminal', {'text': line})
    except Exception as e:
        conn.socketio.emit('terminal', {'text': f'{date} FKWP [[0;31mE[0;0m] 读取日志异常: {e}\n'})

# 根据文件名添加额外内容
def appendFile(path: str, content: str) -> str | None:
    try:
        open(path, mode='a').write(content)
    except Exception as e:
        return f'写入错误：{e}'

# 持续返回性能参数
def queryPerf(conn: Connection, sid: str) -> None:
    try:
        for server_info in getServerList():
            name = conn.clients[sid].get('name')
            if name == server_info[0]:
                conn.set(name, 'pid', server_info[1])
                break
        if not conn.clients[sid].get('pid'):
            conn.socketio.emit('perf', {'data': {'cpu': '请求失败', 'ram': '请求失败'}})
        while conn.contains(sid):
            cpu, ram = getPerfByPid(conn.clients[sid].get('pid'))
            conn.socketio.emit('perf', {'data': {'cpu': cpu, 'ram': ram}})
            time.sleep(2)
    except Exception as e:
        logging.error(f'性能监控异常：{e}')
        conn.socketio.emit('perf', {'data': {'cpu': '获取异常', 'ram': '获取异常'}})
    ...

# 根据PID返回进程占用的CPU与内存使用量
def getPerfByPid(pid: int) -> list:
    cpu_percent = '0.0%'
    memory_info = '0MB'
    if not pid:
        return cpu_percent, memory_info
    try:
        process = psutil.Process(pid)
        cpu_percent = process.cpu_percent(interval=1.0)
        memory_info = process.memory_info().rss
    except psutil.NoSuchProcess:...
    return f'{cpu_percent}%', memory_info

# 寻找所有指定目录下的新月杀扩展包
def getPackListFromDir(directory: str) -> dict:
    package_dict = {'vanilla':{'name': '新月杀', 'packs': {}}}
    root_path, pack_dir = os.path.split(directory.rstrip('/'))
    pack_path_list = [f.path for f in os.scandir(directory) if f.is_dir()]
    for pack_path in pack_path_list:
        pack_name = os.path.basename(pack_path)
        init_file = os.path.join(pack_dir, pack_name, 'init.lua')
        extension_name, pack_dict, trans_dict = extractExtension(root_path, init_file)
        package = {
            "name": trans_dict.get(extension_name, extension_name),
            "packs": {}
        }
        for pack_name in pack_dict:
            package['packs'][pack_name] = pack_dict[pack_name]
            package['packs'][pack_name]['name'] = trans_dict.get(pack_name, pack_name)
        if len(pack_dict):
            if extension_name:
                package_dict[extension_name] = package
            else:
                package_dict['vanilla']['packs'].update(package['packs'])
    return package_dict

# 解析指定目录下的扩展包，返回包名、子包与字典表
def extractExtension(root_path: str, lua_file: str) -> tuple:
    extension_name = ''
    pack_dict = {}
    trans_dict = {}
    lua_path = os.path.join(root_path, lua_file)
    if not os.path.exists(lua_path):
        return '', [], {}
    lua_code = open(lua_path, encoding='utf-8').read()
    lua_code = '\n'.join([line for line in lua_code.split('\n') if '--' not in line])

    if result := re.search(r'extension.extensionName[^"\']*["\']([^"\']*)', lua_code):
        extension_name = result.groups()[0]

    package_list = re.findall(r'Package(:new)?\(["\']([^"\']*)["\'][, ]*(Package\.[^\)\s]*|[^\)\s]*)', lua_code)
    for _, package, pack_type in package_list:
        if pack_type == 'Package.CardPack':
            pack_type = 'card'
        elif pack_type:
            continue
        else:
            pack_type = 'role'
        pack_dict[package] = {
            'name': '',
            'type': pack_type,
        }
    mode_package_list = re.findall(r'fk.CreateGameMode\(?{[\S\s]*name[^"\']*"([^"\']*)[\S\s]*}\)?', lua_code)
    for package in mode_package_list:
        pack_dict[package] = {
            'name': '',
            'type': 'mode',
        }

    if 'i18n' not in lua_file or 'zh_CN' in lua_file:
        trans_table_list = re.findall(r'Fk:loadTranslationTable\(?{([\S\s]+)}\)?', lua_code)
        for table in trans_table_list:
            matches = re.findall(r'\[["\'](.+)["\']\][^/]= ]*["\'](.+)["\']', table)
            trans_dict.update({key: value for key, value in matches})

    require_list = re.findall(r'require[^"\']*["\'](.+)["\']', lua_code)
    dofile_list = re.findall(r'dofile[^"\']*["\'](.+)["\']', lua_code)
    for extra_file in (require_list + dofile_list):
        extra_file = extra_file.replace('.','/')
        if '/lua' in extra_file:
            extra_file = extra_file.replace('/lua','.lua')
        else:
            extra_file += '.lua'
        e_name, packs, trans = extractExtension(root_path, extra_file)
        if e_name: extension_name = e_name
        if trans: trans_dict.update(trans)
        if packs: pack_dict.update(packs)
    return extension_name, pack_dict, trans_dict
