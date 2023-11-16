import json
import time

from src.utils import getProcessRuntime, getVersionFromPath, getImgBase64FromURL, getProcPathByPid, isPortBusy, getServerList, getServerFromConfig, saveServerToConfig, getPlayers, getFKVersion

class Server:
    def __init__(self) -> None:
        self.name = ''
        self.port = 0
        self.pid = 0
        self.path = ''

        self.ban_words = []
        self.desc = ''
        self.icon = ''
        self.capacity = 0
        self.temp_ban_time = 0
        self.motd = ''
        self.hidden_packs = []
        self.enable_bots = True

        self.players = 0
        self.status = '初始化'
        self.version = 'v0.0.1'

    def init(self, name:str, port: int, pid: int = 0, path: str = '') -> None:
        if name == '' or port == '':
            return
        self.name = name
        self.port = port
        self.pid = pid
        if pid:
            self.path = getProcPathByPid(self.pid)
        elif path:
            self.path = path

        try:
            json_data : dict = json.load(open(f'{self.path}/freekill.server.config.json'))
            self.ban_words = json_data.get('banwords', '')
            self.desc = json_data.get('description', '')
            self.icon = json_data.get('iconUrl', '')
            self.capacity = json_data.get('capacity', 0)
            self.temp_ban_time = json_data.get('tempBanTime', 0)
            self.motd = json_data.get('motd', '')
            self.hidden_packs = json_data.get('hiddenPacks', [])
            self.enable_bots = json_data.get('enableBots', True)
            self.status = '运行中' if isPortBusy(self.port) else '已停止'
        except Exception as e:
            self.status = '配置读取异常'

        try:
            if not self.pid or getProcessRuntime(self.pid) == '0':
                self.status = '未运行'
            self.version = getVersionFromPath(self.path)
        except:
            self.status = '版本读取异常'

    def info(self):
        runtime = 0
        if not isPortBusy(self.port):
            self.status = '已停止'
        else:
            self.status = '运行中'
            server_list = getServerList()
            for server_info in server_list:
                server_name = server_info[0] if len(server_info) else ''
                server_pid = int(server_info[1]) if len(server_info) >=2 else self.pid
                if self.name == server_name:
                    self.pid = server_pid
                    self.players = getPlayers(self.name)
                    runtime = getProcessRuntime(self.pid)
                    break

        return {
            'name': self.name,
            'port': self.port,
            'desc': self.desc,
            'icon': getImgBase64FromURL(self.icon),
            'capacity': self.capacity,
            'players': self.players,
            'status': self.status,
            'version': getVersionFromPath(self.path),
            'runtime': runtime,
            'pid': self.pid,
        }

class ServerList:
    def __init__(self) -> None:
        self.dict = {}
        self.list: list[Server | None] = []
        self.latest_fk_version = ''
        self.version_check_timestamp = 0
        
        self.refreshRunning()
        self.dict = getServerFromConfig()
        for server_name in self.dict:
            server_port = self.dict[server_name][0]
            server_path = self.dict[server_name][1]

            if server_name not in [server.name for server in self.list]:
                server = Server()
                server.init(server_name, server_port, path=server_path)
                self.list.append(server)

    def refreshRunning(self) -> None:
        for server_info in getServerList():
            server_name = server_info[0] if len(server_info) else ''
            server_pid = int(server_info[1]) if len(server_info) >1 else 0
            server_port = int(server_info[2]) if len(server_info) >2 else 9527

            if server_name and server_name not in [server.name for server in self.list]:
                server = Server()
                server.init(server_name, server_port, server_pid)
                self.list.append(server)

        for server in self.list:
            if not isPortBusy(server.port) and server.name not in self.dict:
                self.list.remove(server)
    
    def refreshConfig(self) -> None:
        self.dict = getServerFromConfig()

    def getList(self) -> list[Server]:
        self.refreshRunning()
        return self.list
    
    def add(self, server: Server) -> None:
        self.list.append(server)
        self.dict[server.name] = [server.port, server.path]
        saveServerToConfig(self.dict)
    
    def remove(self, server: Server) -> None:
        self.list.remove(server)

    def getDict(self) -> dict:
        self.refreshRunning()
        return self.dict
    
    def checkFKVersion(self) -> str:
        if not self.latest_fk_version or time.time() - self.version_check_timestamp > 3600:
            self.latest_fk_version = getFKVersion()
            self.version_check_timestamp = int(time.time())
        return self.latest_fk_version