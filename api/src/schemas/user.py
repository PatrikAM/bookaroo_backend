import re
from uuid import UUID, uuid4

from bson import ObjectId
from pydantic import BaseModel, Field, BaseConfig

from src.schemas.MongoModel import MongoModel

from src.database import Database
import hashlib

from src.schemas.MongoModel import OID

user_tag = {
    "name": "user",
    "description": "Endpoints for your user account.",
}

salt = "42hitch"
user_collection_name = "readers"


class User(MongoModel):
    id: OID = Field(default_factory=uuid4)
    login: str = Field()
    password: str = Field()
    name: str = Field()
    token: str = Field()

    # locked: bool = False
    # token: str

    def register(self):
        db = Database()
        self.password = hash_password(self.password)
        doc_result = (
            db
            .get_collection(user_collection_name)
            .insert_one(self.mongo())
        )
        db.die()
        return get_user_by_id(doc_result.inserted_id)

    def log_in(self):
        user = get_user_by_email(self.login)
        if user.password != hash_password(self.password):
            return None
        user.password = None
        return user

    def logout(self):
        pass

    def close(self):
        db = Database()
        q = {"_id": ObjectId(self.id)}
        doc_result = (
            db
            .get_collection(user_collection_name)
            .delete_one(q)
        )
        db.die()

    def has_valid_email(self):
        # Define a regular expression pattern for a simple email validation
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

        # Use re.match to check if the email matches the pattern
        match = re.match(pattern, self.login)

        # If there is a match, the email is valid; otherwise, it's not
        return bool(match)

    def has_valid_password(self):
        # Check if the password is at least 6 characters long
        if len(self.password) < 6:
            return False

        # Check if the password contains at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', self.password):
            return False

        # Check if the password contains at least one digit
        if not re.search(r'\d', self.password):
            return False

        # If all conditions are met, the password is considered valid
        return True

    @staticmethod
    def get_users():
        docs = MongoModel.fetch_all_docs(
            user_collection_name
        )
        readers = [User.from_mongo(document) for document in docs]
        return readers


def hash_password(password: str) -> str:
    password += salt
    password_bytes = password.encode('utf-8')
    hash_object = hashlib.sha256(password_bytes)
    return hash_object.hexdigest()


def get_user_by_id(user_id):
    db = Database()
    q = {"_id": ObjectId(user_id)}
    doc = db.get_collection(user_collection_name).find_one(q)
    db.die()
    return User.from_mongo(doc)


def get_user_by_email(email):
    db = Database()
    q = {"login": email}
    doc = db.get_collection(user_collection_name).find_one(q)
    db.die()
    return User.from_mongo(doc)
