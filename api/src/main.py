from docs.tags import tags
from fastapi import FastAPI, HTTPException

from src.schemas.book import Book
from src.schemas.library import Library, get_library_by_id, get_libraries
from src.schemas.user import User, get_user_by_email, get_user_by_id

from src.database import Database

from src.schemas.MongoModel import OID

app = FastAPI(openapi_tags=tags, port=51173)

# TODO 1: validate ids to be valid ObjectIDs by decorator
# TODO 2: handle security by decorator


@app.get("/book/find_by_library/{library_id}", tags=["book"])
async def get_books_from_library(library_id: str):
    books = Book.get_books_by_library_id(library_id)
    if not books:
        raise HTTPException(
            status_code=404,
            detail="No such book."
        )
    return {"data": books}


@app.get("/book/all_books", tags=["book"])
async def get_books(token: str):
    libs_cursor = get_libraries(token)
    libs = [Library.from_mongo(document) for document in libs_cursor]
    books_list = [
        Book.get_books_by_library_id(lib.id)
        for lib in libs
    ]
    books = [item for sublist in books_list for item in sublist]
    print(books)
    return books


@app.get("/book/{book_id}", tags=["book"])
async def get_book_by_id(book_id: str):
    return {"data": Book.get_book_by_id(book_id)}


@app.get("/book/{isbn_or_custom_id}", tags=["book"])
async def get_book_by_isbn(isbn: str) -> Book:
    return {"message": f"{isbn}"}


@app.post("/book", tags=["book"])
async def create_book(book: Book):
    return Book.get_book_by_id(book.create_book().id).to_response()


@app.put("/book", tags=["book"])
async def update_book(book: Book):
    return {"message": "book updated"}


@app.get("/library/all_libraries", tags=["library"])
async def get_all_libraries(token: str):
    # lib = Library()
    # lib.owner_id = ""
    libs_cursor = get_libraries(token)
    # return {"data": libs}
    libs = [Library.from_mongo(document) for document in libs_cursor]
    return libs


@app.get("/library/{library_id}", tags=["library"])
async def get_library(library_id: str):
    lib = get_library_by_id(library_id)
    return {"data": lib.to_response()}


@app.post("/library", tags=["library"])
async def create_library(name: str, token: str):
    library = Library(
        owner_id=OID(token),
        name=name
    )

    lib = library.create_library()
    return {"data": lib.to_response()}


@app.put("/library", tags=["library"])
async def update_library(library: Library):
    lib = get_library_by_id(library.id)
    if lib is None:
        raise HTTPException(
            status_code=404,
            detail="Library does not exist."
        )
    updated_library = library.update_library()
    return {"data": updated_library}


@app.post("/user/register", tags=["user"])
async def register(
        name: str,
        login: str,
        password: str
):
    user = User(
        login=login,
        password=password,
        name=name,
        token=""
    )

    if get_user_by_email(user.login) is not None:
        raise HTTPException(
            status_code=403,
            detail="User already exists."
        )
    if (not user.has_valid_email()
            or not user.has_valid_password()):
        raise HTTPException(
            status_code=422,
            detail="Invalid email or password."
        )
    registered_user = user.register()
    registered_user.password = None
    registered_user.token = registered_user.id
    return registered_user.to_response()


@app.post("/user/login", tags=["user"])
async def login(login: str, password: str):
    user = User(
        login=login,
        password=password,
        name="",
        token=""
    )
    print(user)
    # user.login = login
    # user.password = password
    logged_user = user.log_in()
    if logged_user is None:
        raise HTTPException(
            status_code=404,
            detail="Invalid email or password."
        )
    logged_user.token = logged_user.id
    return logged_user.to_response()


@app.get("/user/logout", tags=["user"])
async def logout():
    return {"data": "logged out"}


@app.get("/user/close_account", tags=["user"])
async def remove_user(token: str):
    user = get_user_by_id(token)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Invalid token."
        )
    user.close()
    user.password = None
    return {"data": user.to_response()}


@app.get("/badge/{badge_id}", tags=["badge"])
async def get_badge(badge_id: str):
    return {"data": f"badge {badge_id}"}


@app.post("/db/reset", tags=["admin"])
async def drop_all_collections(password: str):
    if password != "delejvoledropuj":
        raise HTTPException(
            status_code=401,
            detail="nesahej na to"
        )
    db = Database()
    db.drop_all()
    db.die()
    return {"detail": "dropped"}
