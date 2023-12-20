import os
import re
import sys
import json
import time
import base64
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

# 从指定图片链接获取base64格式的图片数据并返回
def getImgBase64FromURL(url: str) -> str:
    try:
        response = requests.get(url)
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
def runCmd(cmd: str, log=True) -> str | None:
    try:
        stime = time.time()
        comm = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
        stdout, stderr = comm.communicate()
        etime = time.time()
        if log:
            logging.debug(f' >>> 耗时({"{:.3f}".format(etime - stime)})执行指令 {cmd}')
        if stderr:
            logging.info(f' >>> 执行上述指令出错：{stderr}')
        return stdout.strip()
    except Exception as e:
        logging.error(f'执行外部指令出错：{e}')
        return None

# 从指定PID进程获取其运行时长
def getProcessRuntime(pid: int) -> str:
    command = f' ps -p {pid} -o etime='
    runtime = runCmd(command)
    runtime = runtime if runtime else '0'
    return runtime

# 获取正在运行的FreeKill服务器列表以及其信息
def getServerList() -> list[str]:
    command = ''' tmux ls -F "#{session_name} #{pane_pid}" 2>/dev/null '''
    name_p_pid = runCmd(command)
    name_p_pid = name_p_pid if name_p_pid else ''
    name_p_pid_list = [i.split(' ') for i in [j for j in name_p_pid.split('\n')]]

    command = ''' ps -ef | grep -vE '(tee|grep)' | grep './FreeKill -s' | awk '{print $3" "$2" "$10}' '''
    pid_port = runCmd(command)
    pid_port = pid_port if pid_port else ''
    pid_port_list = [i.split(' ') for i in [j for j in pid_port.split('\n')]]

    pid_port_dict = {}
    for item in pid_port_list:
        if item == ['']: continue
        pid_port_dict[item[0]] = [item[1], item[2]]

    server_list = []
    for item in name_p_pid_list:
        if item == ['']: continue
        name = item[0].replace('FreeKill-', '')
        p_pid = item[1]
        if p_pid in pid_port_dict:
            pid = pid_port_dict[p_pid][0]
            port = pid_port_dict[p_pid][1]
            server_list.append([name, pid, port])
    return server_list

# 通过PID获取程序的执行路径
def getProcPathByPid(pid: int) -> str:
    command = f' readlink /proc/{pid}/exe 2>/dev/null'
    result = runCmd(command)
    path = result if result else ''
    path = path.rsplit('/', 1)[0].rstrip('build').rstrip('/')
    return path

# 通过PID获取程序的监听端口
def getProcPortByPid(pid: int) -> int:
    command = ''' netstat -tlnp 2>/dev/null | grep ''' + str(pid) + ''' | awk '{print $4}' '''
    result = runCmd(command)
    port = result if result else ''
    port = port.rsplit(':').pop()
    if port.isdigit():
        return int(port)
    else:
        return 0

# 判断端口号是否是被占用
def isPortBusy(port: int) -> bool:
    command = f' netstat -tlnp 2>/dev/null | grep :{port}'
    if runCmd(command):
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
        json.dump(json_data, open(config_file, 'w'), ensure_ascii=False)
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
def startGameServer(name: str, port: int, path: str) -> int:
    command = f''' cd {path};tmux new -d -s "FreeKill-{name}" "./FreeKill -s {port} 2>&1 | tee ./fk-latest.log" '''
    logging.debug(f' >>> 独立进程   执行指令 {command}')
    subprocess.Popen([command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).wait()
    command = ''' ps -ef | grep -vE '(tee|grep)' | grep './FreeKill -s ''' + str(port) + '''' | awk '{print $2}' '''
    result = ''
    attempt = 0
    while not result and attempt <= 3:
        result = runCmd(command)
        if result.isdigit():
            return int(result)
        time.sleep(1)
        attempt += 1
    return 0 

# 停止服务器
def stopGameServer(name: str) -> bool:
    command = f''' tmux send-keys -t "FreeKill-{name}" C-d '''
    if runCmd(command) != None:
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

# 简单的对tmux窗口进行内容捕获
def captureTmux(tid: str) -> str:
    command = f' tmux capture-pane -pS - -t {tid} 2>&1'
    result = runCmd(command)
    result = result if result else ''
    return result

# 在指定tmux内执行语句，并对Tmux窗口进行内容捕获
def runTmuxCmd(tid: str, cmd: str) -> str:
    command = f' tmux send-keys -t {tid} "{cmd}" Enter;sleep 0.1;tmux capture-pane -peS - -t {tid} 2>&1'
    result = runCmd(command)
    result = result if result else ''
    return result

# 获取指定服务器内在线人数
def getPlayers(name: str) -> int:
    captured = runTmuxCmd(f'FreeKill-{name}', 'lsplayer')
    if captured and 'lsplayer\n' in captured:
        player_text = captured.rsplit('lsplayer\n', 1)[1]
    else:
        player_text = ''
    if match := re.search(r'Current (.*) online player\(s\)', player_text):
        count = match.groups()[0]
        if count.isdigit():
            return int(count)
    return 0

# 获取指定服务器内在线玩家列表
def getPlayerList(name: str) -> dict:
    captured = runTmuxCmd(f'FreeKill-{name}', 'lsplayer')
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
def getRoomList(name: str) -> dict:
    captured = runTmuxCmd(f'FreeKill-{name}', 'lsroom')
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
def banFromServer(server_name: str, player_name: str) -> bool:
    captured = runTmuxCmd(f'FreeKill-{server_name}', f'ban {player_name}')
    result_text = captured.rsplit('ban\n', 1)[1]
    if re.search(r'Running command:', result_text):
        return True
    return False

# 向指定服务器发送消息
def sendMsgTo(name: str, msg: str) -> bool:
    captured = runTmuxCmd(f'FreeKill-{name}', f'msg {msg}')
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
        path = ''
        server_list = getServerList()
        for server in server_list:
            if conn.clients[sid].get('name') == server[0]:
                path = getProcPathByPid(server[1])

        if path == '':
            conn.socketio.emit('terminal', {'text': f'{date} FKWP [[0;32mI[0;0m] 服务器未启动，输入指令[0;33m start [0;0m启动服务器\n'})
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
        conn.socketio.emit('terminal', {'text': f'{date} FKWP [[0;32mI[0;0m] 读取日志异常: {e}\n'})

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
        conn.socketio.emit('perf', {'data': {'cpu': '获取异常', 'ram': '获取异常'}})
    ...

# 根据PID返回进程占用的CPU与内存使用量
def getPerfByPid(pid: int) -> list:
    command = ''' ps -up ''' + str(pid) + ''' --no-header 2>/dev/null | awk '{print $3"% "$6}' '''
    result = runCmd(command, log=False)
    perf = result if result else ''
    perf_list = perf.split(' ')
    if len(perf_list) < 2:
        return '0.0%', '0MB'
    return perf_list

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
