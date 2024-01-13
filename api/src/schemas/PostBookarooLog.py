import json


class PostBookarooLog:
    user_id: str
    ip: str
    endpoint: str
    method: str

    def __init__(self, user_id, ip, endpoint, method):
        # Constructor code here
        self.user_id = user_id
        self.method = method
        self.ip = ip
        self.endpoint = endpoint

    def to_json(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(msg: str):
        return PostBookarooLog(**json.load(msg))
