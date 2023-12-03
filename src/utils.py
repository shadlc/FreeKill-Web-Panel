import re
import sys
import json
import time
import base64
import requests
import subprocess

from flask import jsonify
from src.connection import Connection

config_file = f'./config.json'

# 从指定图片链接获取base64格式的图片数据并返回
def getImgBase64FromURL(url: str) -> str:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            image_data = response.content
            base64_data = 'data:image/png;base64,' + base64.b64encode(image_data).decode('utf-8')
            return base64_data
        return ''
    except:
        return ''

# 取得FreeKill最新版本
def getFKVersion() -> str | None:
    try:
        url = 'https://gitee.com/notify-ctrl/FreeKill/releases/latest'
        response = requests.get(url)
        if response.status_code == 200:
            version = response.url.split('/').pop()
            return version
        return
    except:
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
    except:...
    return ''

# 运行Bash指令并获取结果
def runCmd(cmd: str) -> str | None:
    stime = time.time()
    try:
        result = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
    except:
        return None
    etime = time.time()
    if '--debug' in sys.argv[1:]:
        print(f' >>> 耗时({"{:.3f}".format(etime - stime)})执行指令 {cmd}')
    return result

# 从指定PID进程获取其运行时长
def getProcessRuntime(pid: int) -> str:
    command = f' ps -p {pid} -o etime='
    runtime = runCmd(command)
    runtime = runtime if runtime else '0'
    return runtime

# 获取正在运行的FreeKill服务器列表以及其信息
def getServerList() -> list[str]:
    command = ''' ps -ef | grep -E '\?.*tmux\s+.*FreeKill-.*FreeKill -s' | awk '{print $12" "$2" "$15}' '''
    running = runCmd(command)
    server_list = running if running else ''

    command = ''' ps -ef | grep -vE '(tee|grep)' | grep './FreeKill -s' | awk '{print $10" "$2}' '''
    port_pid = runCmd(command)
    port_pid_list = port_pid if port_pid else ''

    port_pid_list = [i.split(' ') for i in [j for j in port_pid.split('\n')]]
    port_pid_dict = {}
    for item in port_pid_list:
        if item == ['']: continue
        port_pid_dict[item[0]] = item[1]
    server_list = [i.split(' ') for i in [j for j in server_list.split('\n')]]
    for item in server_list:
        if item == ['']: continue
        item[0] = item[0].replace('FreeKill-', '')
        if item[2] in port_pid_dict:
            item[1] = int(port_pid_dict[item[2]])
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
    print(f' >>> 独立进程   执行指令 {command}')
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
            config_json[key] = config[key]
        json.dump(config_json, open(f'{path}/freekill.server.config.json', 'w'), ensure_ascii=False, indent=2)
    except Exception as e:
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
    player_text = captured.rsplit('lsplayer\n', 1)[1] if captured else ''
    if match := re.search(r'Current (.*) online player\(s\)', player_text):
        count = match.groups()[0]
        if count.isdigit():
            return int(count)
    return 0

# 获取指定服务器内在线玩家列表
def getPlayerList(name: str) -> dict:
    captured = runTmuxCmd(f'FreeKill-{name}', 'lsplayer')
    player_text = captured.rsplit('lsplayer\n', 1)[1] if captured else ''
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
    room_text = captured.rsplit('lsroom\n', 1)[1] if captured else ''
    room_dict = {}
    if match := re.search(r'Current (.*) running rooms are', room_text):
        for line in room_text.split('\n'):
            if match := re.search(r' ([0-9]+) , "(.*)"', line):
                index = match.groups()[0]
                name = match.groups()[1]
                room_dict[int(index)] = name
    return room_dict

# 获取指定服务器扩充包
def getPackList(name: str) -> dict:
    ...

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
        conn.socketio.emit('terminal', {'text': tailLogNum(log_file, 500), 'history': True})
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

def getPerfByPid(pid: int) -> list:
    command = ''' ps -up ''' + str(pid) + ''' --no-header 2>/dev/null | awk '{print $3"% "$6}' '''
    result = runCmd(command)
    perf = result if result else ''
    perf_list = perf.split(' ')
    if len(perf_list) < 2:
        return '0.0%', '0MB'
    return perf_list