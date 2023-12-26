import json

from src.utils import getProcessUptime, getSessionPid, getVersionFromPath, getImgBase64FromURL, getProcPathByPid, isPortBusy, startGameServer, isHandledByPid, getServerInfo, getPlayerList, getRoomList, getPackList


class Server:
    def __init__(self) -> None:
        self.name = ''
        self.port = 0
        self.pid = 0
        self.path = ''

        self.ban_words = []
        self.desc = ''
        self.icon_url = ''
        self.capacity = 0
        self.temp_ban_time = 0
        self.motd = ''
        self.hidden_packs = []
        self.enable_bots = True

        self.players = 0
        self.status = '初始化'
        self.version = 'v0.0.1'

        self.player_dict = {}
        self.room_dict = {}
        self.pack_dict = {}
        self.handled = False
        self.session_type = ''

    def init(self, name:str, port: int, pid: int = 0, path: str = '', session_type = '') -> None:
        if name == '' or port == '':
            return
        self.name = name
        self.port = port
        self.pid = pid
        self.session_type = session_type
        if pid:
            self.path = getProcPathByPid(self.pid)
        elif path:
            self.path = path
        if not self.readConfig():
            return
        try:
            if not self.pid or getProcessUptime(self.pid) == '0':
                self.status = '未运行'
            self.version = getVersionFromPath(self.path)
        except:
            self.status = '版本读取异常'

    def start(self) -> str | None:
        session_type = self.session_type if self.session_type else 'tmux'
        if pid := startGameServer(self.name, self.port, self.path, session_type):
            self.pid = pid
            if self.session_type == 'screen':
                self.name = f'{getSessionPid(self.pid)}.{self.name.split(".", 1).pop()}'
            return
        return '服务器启动失败，该端口可能已被占用'

    def info(self, server_list: list) -> dict:
        uptime = '0'
        if not isPortBusy(self.port):
            self.status = '已停止'
        else:
            self.status = '运行中'
            for server_info in server_list:
                server_name = server_info[0] if len(server_info) else ''
                server_pid = int(server_info[1]) if len(server_info) >=2 else self.pid
                if self.name == server_name:
                    self.pid = server_pid
                    uptime = getProcessUptime(self.pid)
                    break
            info = getServerInfo(self.name, self.port)
            if info:
                [self.version,
                 self.icon_url,
                 self.desc,
                 self.capacity,
                 self.players,
                 self.ip] = info

        return {
            'name': self.name,
            'port': self.port,
            'desc': self.desc,
            'icon': getImgBase64FromURL(self.icon_url),
            'capacity': self.capacity,
            'players': self.players,
            'status': self.status,
            'version': getVersionFromPath(self.path),
            'uptime': uptime,
            'pid': self.pid,
            'session_type': self.session_type,
        }

    def details(self, server_list: list) -> dict:
        self.readConfig()
        self.readPacks()
        self.handled = isHandledByPid(self.pid)
        info_dict = self.info(server_list)
        info_dict = {
            **info_dict,
            'ban_words': self.ban_words,
            'motd': self.motd,
            'temp_ban_time': self.temp_ban_time,
            'hidden_packs': self.hidden_packs,
            'enable_bots': self.enable_bots,
            'pack_list': self.pack_dict,
            'room_list': self.room_dict,
            'player_list': self.player_dict,
            'session_type': self.session_type,
            'handled': self.handled,
        }
        return info_dict
    
    def getPlayerList(self) -> dict:
        if isPortBusy(self.port):
            self.readPlayers()
        else:
            self.player_dict = {}
        return self.player_dict
    
    def getRoomList(self) -> dict:
        if isPortBusy(self.port):
            self.readRooms()
        else:
            self.room_dict = {}
        return self.room_dict

    def readConfig(self) -> bool:
        try:
            json_data : dict = json.load(open(f'{self.path}/freekill.server.config.json'))
            self.ban_words = json_data.get('banwords', [])
            self.desc = json_data.get('description', '')
            self.icon_url = json_data.get('iconUrl', '')
            self.capacity = json_data.get('capacity', 0)
            self.temp_ban_time = json_data.get('tempBanTime', 0)
            self.motd = json_data.get('motd', '')
            self.hidden_packs = json_data.get('hiddenPacks', [])
            self.enable_bots = json_data.get('enableBots', True)
            self.status = '运行中' if isPortBusy(self.port) else '已停止'
            return True
        except Exception as e:
            self.status = '配置读取异常'
            return False

    def readPlayers(self) -> None:
        self.player_dict = getPlayerList(self.name, self.session_type, self.path)
        self.players = len(self.player_dict)

    def readRooms(self) -> None:
        self.room_dict = getRoomList(self.name, self.session_type, self.path)

    def readPacks(self) -> None:
        self.pack_dict = getPackList(self.path)
