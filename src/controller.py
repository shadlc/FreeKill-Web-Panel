
import time

from src.utils import isPortBusy, getServerList, getServerFromConfig, saveServerToConfig, getFKVersion
from src.connection import Connection
from src.game_server import Server

class Controller:
    def __init__(self) -> None:
        self.server_list = []
        self.server_dict = {}
        self.list: list[Server | None] = []
        self.connection: Connection | None
        self.latest_fk_version = ''
        self.version_check_timestamp = 0

        self.refreshRunning()
        self.server_dict = getServerFromConfig()
        for server_name in self.server_dict:
            server_port = self.server_dict[server_name][0]
            server_path = self.server_dict[server_name][1]
            session_type = self.server_dict[server_name][2]

            if server_name not in [server.name for server in self.list]:
                server = Server()
                server.init(server_name, server_port, path=server_path, session_type=session_type)
                self.list.append(server)

    def refreshRunning(self) -> None:
        self.server_list = getServerList()
        del_server_list = []
        for server_info in self.server_list:
            server_name = server_info[0] if len(server_info) else ''
            server_pid = int(server_info[1]) if len(server_info) >1 else 0
            server_port = int(server_info[2]) if len(server_info) >2 else 9527
            server_type = server_info[3]

            if server_name and server_name not in [server.name for server in self.list]:
                if del_server := [server for server in self.list if server.port == server_port]:
                    del_server_list.append(del_server[0].name)
                    self.list.remove(del_server[0])
                server = Server()
                server.init(server_name, server_port, server_pid, session_type=server_type)
                self.list.append(server)

        for server in self.list:
            if not isPortBusy(server.port) and server.name not in self.server_dict:
                self.list.remove(server)

        for server_name in del_server_list:
            if server_name in self.server_dict:
                self.server_dict.pop(server_name)
            saveServerToConfig(self.server_dict)

    def refreshConfig(self) -> None:
        self.server_dict = getServerFromConfig()

    def getList(self) -> list[Server]:
        self.refreshRunning()
        return self.list

    def add(self, server: Server) -> None:
        self.list.append(server)
        self.server_dict[server.name] = [server.port, server.path, server.session_type]
        saveServerToConfig(self.server_dict)

    def remove(self, server: Server) -> None:
        self.list.remove(server)

    def getDict(self) -> dict:
        self.refreshRunning()
        return self.server_dict

    def modifyDict(self, name, key, value) -> None:
        if key == 'port':
            self.server_dict[name][0] = value
        elif key == 'path':
            self.server_dict[name][1] = value
        self.saveDict()

    def saveDict(self) -> bool:
        return saveServerToConfig(self.server_dict)

    def checkFKVersion(self) -> str:
        if not self.latest_fk_version or time.time() - self.version_check_timestamp > 600:
            self.latest_fk_version = getFKVersion()
            self.version_check_timestamp = int(time.time())
        return self.latest_fk_version
