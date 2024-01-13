from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from pydantic import BaseModel, BaseConfig, Extra
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from src.database import Database


class OID(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, b=None, **kwargs):
        try:
            if v is None or v == "":
                return
            return ObjectId(str(v))
        except InvalidId:
            raise ValueError("Not a valid ObjectId")

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type,
                                     _handler) -> core_schema.CoreSchema:
        # assert source_type is ObjectId
        return core_schema.no_info_wrap_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema,
                                     handler) -> JsonSchemaValue:
        return handler(core_schema.str_schema())


class MongoModel(BaseModel):
    class Config(BaseConfig):
        populate_by_name = True
        # extra = Extra.forbid
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            ObjectId: lambda oid: str(oid),
        }

    @classmethod
    def from_mongo(cls, data: dict):
        """We must convert _id into "id". """
        if not data:
            return data
        if '_id' in data:
            mongo_id = data['_id']
            del data['_id']
            return cls(**dict(data, id=mongo_id))
        return cls(**dict(data))

    def to_response(self):
        response = {}

        for key, value in self.__dict__.items():
            # Convert values to string
            if value is not None:
                response[key] = str(value)

        return response

    def to_grpc(self):
        response = {}

        l = []
        delimiter = ", "
        for key, value in self.__dict__.items():

            if value is not None:
                l.append(f'\"{key}\": \"{value}"')
                response[key] = str(value)

        return "{ " + delimiter.join(l) + " }"

    def mongo(self, **kwargs):
        exclude_unset = kwargs.pop('exclude_unset', True)
        by_alias = kwargs.pop('by_alias', True)

        parsed = self.dict(
            exclude_unset=exclude_unset,
            by_alias=by_alias,
            **kwargs,
        )
        # Mongo uses `_id` as default key. We should stick to that as well.
        if 'id' in parsed and parsed['id'] is not None:
            if '_id' not in parsed and 'id' in parsed:
                parsed['_id'] = parsed.pop('id')
        elif 'id' in parsed:
            del parsed['id']

        return parsed

    @staticmethod
    def fetch_doc(collection_name, id):
        db = Database()
        q = {"_id": ObjectId(id)}
        doc = db.get_collection(collection_name).find_one(q)
        db.die()
        return doc

    def insert_doc(self, collection_name):
        db = Database()
        doc = db.get_collection(collection_name).insert_one(
            self.mongo())
        db.die()
        return doc

    @staticmethod
    def fetch_docs_exact(collection_name, key, value):
        db = Database()
        q = {key: value}
        docs = db.get_collection(collection_name).find(q)
        # db.die()
        return docs

    @staticmethod
    def fetch_all_docs(collection_name, ):
        db = Database()
        q = {}
        docs = db.get_collection(collection_name).find(q)
        # db.die()
        return docs

    @staticmethod
    def remove_doc_by_id(collection_name: str, id: str):
        db = Database()
        q = {"_id": ObjectId(id)}
        (
            db
            .get_collection(collection_name)
            .delete_one(q)
        )
        db.die()

    def update_doc_by_id(self, collection_name: str, id: str):
        db = Database()
        q = {"_id": id}
        values = {"$set": self.mongo()}
        (
            db
            .get_collection(collection_name)
            .update_one(q, values)
        )
        db.die()
