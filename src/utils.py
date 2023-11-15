import re
import json
import base64
import requests
import subprocess

from flask import jsonify

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

# 从指定PID进程获取其运行时长
def getProcessRuntime(pid: int) -> str:
    command = f"ps -p {pid} -o etime="
    runtime = '0'
    try:
        runtime = subprocess.check_output(command, shell=True).decode('utf-8').strip()
    except:...
    return runtime

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
            return version
    except:...
    return ''

# 获取正在运行的FreeKill服务器列表以及其信息
def getServerList() -> list[str]:
    command = ''' ps -ef | grep -E '\?.*tmux\s+.*FreeKill-.*FreeKill -s' | awk '{print $12" "$2" "$15}' '''
    server_list = []
    try:
        server_list = subprocess.check_output(command, shell=True).decode('utf-8').strip()
    except:...
    server_list = [i.split(" ") for i in [j for j in server_list.split("\n")]]
    for i in server_list:
        if i == ['']: continue
        i[0] = i[0].replace('FreeKill-', '')
        i[1] = int(i[1]) + 1
    return server_list

# 通过PID获取程序的执行路径
def getProcPathByPid(pid: int) -> str:
    command = f"readlink /proc/{pid}/exe"
    path = ''
    try:
        path = subprocess.check_output(command, shell=True).decode('utf-8').strip()
    except:...
    path = path.rsplit("/", 1)[0].rstrip("build").rstrip("/")
    return path

# 通过PID获取程序的监听端口
def getProcPortByPid(pid: int) -> int:
    command = '''netstat -tlnp | grep ''' + str(pid) + ''' | awk '{print $4}' '''
    port = ''
    try:
        port = subprocess.check_output(command, shell=True).decode('utf-8').strip()
    except:...
    port = port.rsplit(":").pop()
    if port.isdigit():
        return int(port)
    else:
        return 0

# 判断端口号是否是被占用
def isPortBusy(port: int) -> bool:
    command = f"lsof -i:{port}"
    try:
        subprocess.check_output(command, shell=True)
    except:
        return False
    return True

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
    command = f''' cd {path};tmux new -d -s "FreeKill-{name}" "./FreeKill -s {port}" '''
    subprocess.Popen([command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).wait()
    command = ''' ps -ef | grep -E '\?.*tmux\s+.*FreeKill-''' + name + ''' ' | awk '{print $2}' '''
    result = subprocess.check_output(command, shell=True).decode('utf-8').strip()
    if result.isdigit():
        return int(result)
    else:
        return 0

# 停止服务器
def stopGameServer(name: str) -> bool:
    command = f''' tmux send-keys -t "FreeKill-{name}" C-d '''
    try:
        subprocess.check_output(command, shell=True).decode('utf-8').strip()
    except:
        return False
    return True

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
    command = f'tmux capture-pane -pS - -t {tid}'
    result = ''
    try:
        result = subprocess.check_output(command, shell=True).decode('utf-8').strip()
    except: ...
    return result

# 在指定tmux内执行语句，并对Tmux窗口进行内容捕获
def runTmuxCmd(tid: str, cmd: str) -> str:
    command = f'tmux send-keys -t {tid} "{cmd}" Enter;sleep 0.1;tmux capture-pane -peS - -t {tid}'
    result = ''
    try:
        result = subprocess.check_output(command, shell=True).decode('utf-8').strip()
    except: ...
    return result

# 获取指定服务器内在线人数
def getPlayers(name: str) -> int:
    captured = runTmuxCmd(f'FreeKill-{name}', 'lsplayer')
    player_text = captured.rsplit('lsplayer\n', 1)[1]
    if match := re.search(r'Current (.*) online player\(s\)', player_text):
        count = match.groups()[0]
        if count.isdigit():
            return int(count)
    return 0