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
    library: OID = Field()
    author: str = Field()
    title: str = Field()
    subtitle: str = Field(default=None)
    pages: int = Field(default=None)
    read: bool = Field(default=False)
    favourite: bool = Field(default=False)
    cover: str = Field(default=None)
    publisher: str = Field(default=None)
    published: float = Field(default=None)

    # description: str = Field(default=None)

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
    def get_books_by_library_id(lib_id: str):
        docs = MongoModel.fetch_docs_exact(
            book_collection_name,
            "library",
            ObjectId(lib_id)

        )
        books = [Book.from_mongo(document) for document in docs]
        return books

    @staticmethod
    def remove_book_by_id(book_id: str):
        book = Book.get_book_by_id(book_id)
        (
            MongoModel
            .remove_doc_by_id(
                collection_name=book_collection_name,
                id=book_id
            )
        )
        return book
