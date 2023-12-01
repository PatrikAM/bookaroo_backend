from __future__ import annotations

from bson import ObjectId
from src.schemas.MongoModel import MongoModel, OID
from pydantic import Field

book_tag = {
    "name": "book",
    "description": "Endpoints for your books.",
}

book_collection_name = "books"


class Book(MongoModel):
    id: OID = Field(default=None)
    # custom_id: str | None = None
    isbn: str = Field(default=None)
    library_id: OID = Field()
    author: str = Field()
    title: str = Field()
    subtitle: str = Field(default=None)
    page_count: int = Field(default=None)
    read: bool = Field(default=False)
    favourite: bool = Field(default=False)
    cover: str = Field(default=None)

    def create_book(self):
        # db = Database()
        # doc_result = db.get_collection(book_collection_name).insert_one(
        #     self.mongo())
        # db.die()
        doc = self.insert_doc(book_collection_name)
        return Book.get_book_by_id(doc.inserted_id)

    @staticmethod
    def get_book_by_id(book_id):
        # db = Database()
        # q = {"_id": ObjectId(lib_id)}
        # doc = db.get_collection(book_collection_name).find_one(q)
        # db.die()
        doc = MongoModel.fetch_doc(book_collection_name, book_id)
        return Book.from_mongo(doc)

    @staticmethod
    def get_books_by_library_id(lib_id: OID):
        docs = MongoModel.fetch_docs_exact(
            book_collection_name,
            "library_id",
            lib_id
        )
        books = [Book.from_mongo(document) for document in docs]
        return books
