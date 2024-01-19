import pymongo


class Database:
    client = None
    db = None

    def __create_conn(self):
        # self.client = pymongo.MongoClient("mongodb://%s:%s@localhost:27017/" % ("root", "password"))
        self.client = pymongo.MongoClient("mongodb://%s:%s@mongo:27017/" % ("root", "password"))

    def __open_db(self):
        self.__create_conn()
        self.db = self.client["bookaroo"]

    def get_collection(self, collection_name):
        self.__open_db()
        return self.db[collection_name]

    def die(self):
        self.db = None
        self.client.close()

    def drop_all(self):
        self.__open_db()
        for collection in self.db.list_collections():
            self.db.drop_collection(collection['name'])
            # print(collection['name'])
        self.die()
