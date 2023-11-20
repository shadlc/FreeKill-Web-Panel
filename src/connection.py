from flask_socketio import SocketIO

class Connection:
    def __init__(self, socketio: SocketIO) -> None:
        self.socketio  = socketio
        self.clients = {}

    def add(self, sid: str, type: str, name: str) -> None:
        self.clients[sid] = {'type': type, 'name': name}

    def remove(self, sid: str) -> None:
        self.clients.pop(sid)

    def contains(self, sid: str) -> bool:
        return sid in self.clients

    def set(self, type: str, name: str, property: str, value: str) -> None:
        for sid in self.clients:
            if self.clients[sid]['type'] == type and self.clients[sid]['name'] == name :
                self.clients[sid][property] = value