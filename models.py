from pydantic import BaseModel


class BookCreateRequest(BaseModel):
    title: str = None
    subtitle: str = None
    author: str = None
    binding: str = None
    cover_image: str = None
    reader_id: int
    publisher: str = None
    published: int = None
    isbn: str = None
    borrower_id: int = None
    library_id: int = None
    interval_value: int = None


class ReaderCreateRequest(BaseModel):
    name: str = None
    sex: str = None
    email: str = None
    surname: str = None


class LibraryCreateRequest(BaseModel):
    name: str = None
    address: str = None
    floor: str = None
