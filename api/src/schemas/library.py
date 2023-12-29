from bson import ObjectId
from pydantic import BaseModel, Field, BaseConfig
from src.database import Database
from uuid import uuid4

from src.schemas.MongoModel import MongoModel, OID

from src.schemas.book import Book

library_tag = {
    "name": "library",
    "description": "Endpoints for your libraries.",
}

library_collection_name = "libraries"


class Library(MongoModel):
    id: OID = Field(default_factory=uuid4)
    owner_id: OID = Field(default_factory=uuid4)
    name: str = Field()
    total: int = Field(default=0)
    favourite: int = Field(default=0)
    read: int = Field(default=0)

    def create_library(self):
        db = Database()
        doc_result = db.get_collection(library_collection_name).insert_one(
            self.mongo())
        db.die()
        return get_library_by_id(doc_result.inserted_id)

    def update_library(self):
        db = Database()
        q = {"_id": self.id}
        data = {"$set": self.mongo()}
        doc_result = (
            db
            .get_collection(library_collection_name)
            .update_one(q, data)
        )
        db.die()
        return get_library_by_id(self.id)

    def update_total(self):
        size = len(Book.get_books_by_library_id(self.id))
        self.total = size
        return self

    def update_favourite(self):
        favourites = list(
            filter(
                lambda book: book.favourite,
                Book
                .get_books_by_library_id(self.id)
            )
        )
        self.favourite = len(favourites)
        return self

    def update_read(self):
        reads = list(
            filter(
                lambda book: book.read,
                Book
                .get_books_by_library_id(self.id)
            )
        )
        self.read = len(reads)
        return self


def get_library_by_id(lib_id):
    db = Database()
    q = {"_id": ObjectId(lib_id)}
    doc = db.get_collection(library_collection_name).find_one(q)
    db.die()
    return Library.from_mongo(doc)


def get_libraries(owner_id):
    db = Database()
    q = {"owner_id": ObjectId(owner_id)}
    docs = db.get_collection(library_collection_name).find(q)
    # db.die()
    return docs
