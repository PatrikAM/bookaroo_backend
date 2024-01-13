import json

from docs.tags import tags
from fastapi import FastAPI, HTTPException, Request

from src.communication.RabbitMq import RabbitMq
from src.schemas.book import Book
from src.schemas.library import Library, get_library_by_id, get_libraries
from src.schemas.user import User, get_user_by_email, get_user_by_id
from src.schemas.PostBookarooLog import PostBookarooLog
from src.schemas.Methods import Methods
from src.communication.grpc import GRPC
from src.proto import bookaroo_pb2_grpc, bookaroo_pb2

from src.database import Database

from src.schemas.MongoModel import OID

app = FastAPI(openapi_tags=tags, port=51173)


# TODO 1: validate ids to be valid ObjectIDs by decorator
# TODO 2: handle security by decorator


@app.get("/book/find_by_library/{library_id}", tags=["book"])
async def get_books_from_library(
        library_id: str,
        token: str,
        request: Request
):
    bklog = PostBookarooLog(
        user_id=token,
        ip=request.client.host,
        method=Methods.GET.name,
        endpoint=f"/book/find_by_library/{library_id}"
    )
    RabbitMq().publish(bklog.to_json())
    # if not get_library_by_id(library_id):
    #     raise HTTPException(
    #         status_code=404,
    #         detail="No such book."
    #     )
    # books = Book.get_books_by_library_id(library_id)
    # return books

    response = GRPC.request(
        "books",
        bookaroo_pb2.Operation.SELECT,
        data=library_id,
        token=token,
        query="by-library"
    )
    if response.code != 200:
        raise HTTPException(
            status_code=response.code,
            detail=response.message
        )

    books = []
    for book in json.loads(response.message):
        books.append(Book(**book))
    return books


@app.get("/book/all_books", tags=["book"])
async def get_books(
        token: str,
        request: Request
):
    bklog = PostBookarooLog(
        user_id=token,
        ip=request.client.host,
        method=Methods.GET.name,
        endpoint="/book/all_books"
    )
    RabbitMq().publish(bklog.to_json())
    # libs_cursor = get_libraries(token)
    #
    # libs = [Library.from_mongo(document) for document in libs_cursor]
    # books_list = [
    #     Book.get_books_by_library_id(lib.id)
    #     for lib in libs
    # ]
    # books = [item for sublist in books_list for item in sublist]
    # return books
    response = GRPC.request(
        "books",
        bookaroo_pb2.Operation.SELECT,
        data="",
        token=token,
        query="all"
    )
    if response.code != 200:
        raise HTTPException(
            status_code=response.code,
            detail=response.message
        )

    books = []
    for book in json.loads(response.message):
        books.append(Book(**book))
    return books
    # return json.loads(response.message)


@app.get("/book/{book_id}", tags=["book"])
async def get_book_by_id(
        book_id: str,
        token: str,
        request: Request
):
    bklog = PostBookarooLog(
        user_id=token,
        ip=request.client.host,
        method=Methods.POST.name,
        endpoint="/rabbit"
    )
    RabbitMq().publish(bklog.to_json())
    # return Book.get_book_by_id(book_id)

    response = GRPC.request(
        "books",
        bookaroo_pb2.Operation.SELECT,
        data=book_id,
        token=token,
        query=""
    )
    if response.code != 200:
        raise HTTPException(
            status_code=response.code,
            detail=response.message
        )

    return Book(**json.loads(response.message))


# @app.get("/book/{isbn_or_custom_id}", tags=["book"])
# async def get_book_by_isbn(isbn: str) -> Book:
#     return {"message": f"{isbn}"}


@app.post("/book", tags=["book"])
async def create_book(
        request: Request,
        author: str,
        title: str,
        library: str,
        isbn: str,
        token: str,
        subtitle=None,
        pages=None,
        read=False,
        favourite=False,
        cover=None,
        publisher=None,
        published=None
):
    bklog = PostBookarooLog(
        user_id=token,
        ip=request.client.host,
        method=Methods.POST.name,
        endpoint="/book"
    )
    RabbitMq().publish(bklog.to_json())
    book = Book(
        author=author,
        owner_id=token,
        library=library,
        title=title,
        read=read,
        favourite=favourite
    )

    if subtitle is not None:
        book.subtitle = subtitle

    if pages is not None:
        book.pages = pages

    if cover is not None:
        book.cover = cover

    if publisher is not None:
        book.publisher = publisher

    if published is not None:
        book.published = published

    if isbn is not None:
        book.isbn = isbn

    # book_from_db = Book.get_book_by_id(book.create_book().id)
    # return book_from_db.to_response()

    response = GRPC.request(
        "books",
        bookaroo_pb2.Operation.INSERT,
        data=book.to_grpc(),
        token=token,
        query=""
    )
    if response.code != 200:
        raise HTTPException(
            status_code=response.code,
            detail=response.message
        )

    return Book(**json.loads(response.message))


@app.put("/book", tags=["book"])
async def update_book(
        book: Book,
        token: str,
        request: Request
):
    bklog = PostBookarooLog(
        user_id=token,
        ip=request.client.host,
        method=Methods.PUT.name,
        endpoint="/book"
    )
    RabbitMq().publish(bklog.to_json())
    # return book.update_book()

    response = GRPC.request(
        "books",
        bookaroo_pb2.Operation.UPDATE,
        data=book.to_grpc(),
        token=token,
        query=""
    )
    if response.code != 200:
        raise HTTPException(
            status_code=response.code,
            detail=response.message
        )

    return Book(**json.loads(response.message))


@app.get("/book/remove_by_id/{book_id}", tags=["book"])
async def remove_book(
        book_id: str,
        token: str,
        request: Request
):
    bklog = PostBookarooLog(
        user_id=token,
        ip=request.client.host,
        method=Methods.GET.name,
        endpoint=f"/book/remove_by_id/{book_id}"
    )
    RabbitMq().publish(bklog.to_json())

    # return Book.remove_book_by_id(book_id)
    response = GRPC.request(
        "books",
        bookaroo_pb2.Operation.DELETE,
        data=book_id,
        token=token,
        query=""
    )
    if response.code != 200:
        raise HTTPException(
            status_code=response.code,
            detail=response.message
        )

    return Book(**json.loads(response.message))


@app.get("/library/all_libraries", tags=["library"])
async def get_all_libraries(
        token: str,
        request: Request
):
    bklog = PostBookarooLog(
        user_id=token,
        ip=request.client.host,
        method=Methods.GET.name,
        endpoint="/library/all_libraries"
    )

    RabbitMq().publish(bklog.to_json())

    # libs_cursor = get_libraries(token)
    # libs = [Library.from_mongo(document)
    #         .update_total()
    #         .update_favourite()
    #         .update_read()
    #         for document in libs_cursor]
    # return libs
    response = GRPC.request(
        "libraries",
        bookaroo_pb2.Operation.SELECT,
        data="",
        token=token,
        query="all"
    )
    if response.code != 200:
        raise HTTPException(
            status_code=response.code,
            detail=response.message
        )
    return json.loads(response.message)


@app.get("/library/{library_id}", tags=["library"])
async def get_library(
        library_id: str,
        request: Request
):
    bklog = PostBookarooLog(
        user_id="",
        ip=request.client.host,
        method=Methods.GET.name,
        endpoint=f"/library/{library_id}"
    )
    RabbitMq().publish(bklog.to_json())
    # lib = get_library_by_id(library_id)
    # return lib.to_response()
    response = GRPC.request(
        "libraries",
        bookaroo_pb2.Operation.SELECT,
        data=library_id,
        token="token",
        query=""
    )
    if response.code != 200:
        raise HTTPException(
            status_code=response.code,
            detail=response.message
        )
    return json.loads(response.message)


@app.post("/library", tags=["library"])
async def create_library(
        name: str,
        token: str,
        request: Request
):
    bklog = PostBookarooLog(
        user_id=token,
        ip=request.client.host,
        method=Methods.POST.name,
        endpoint="/library"
    )
    RabbitMq().publish(bklog.to_json())
    library = Library(
        owner_id=OID(token),
        name=name
    )

    # lib = (library
    #        .create_library()
    #        .update_total()
    #        .update_favourite()
    #        .update_read())
    # return lib.to_response()
    response = GRPC.request(
        "libraries",
        bookaroo_pb2.Operation.INSERT,
        data=library.to_grpc(),
        token="token",
        query=""
    )
    if response.code != 200:
        raise HTTPException(
            status_code=response.code,
            detail=response.message
        )
    return json.loads(response.message)


@app.put("/library", tags=["library"])
async def update_library(
        library: Library,
        request: Request
):
    bklog = PostBookarooLog(
        user_id="",
        ip=request.client.host,
        method=Methods.PUT.name,
        endpoint="/library"
    )
    RabbitMq().publish(bklog.to_json())
    # lib = get_library_by_id(library.id)
    # if lib is None:
    #     raise HTTPException(
    #         status_code=404,
    #         detail="Library does not exist."
    #     )
    # updated_library = library.update_library()
    # return {"data": updated_library}

    response = GRPC.request(
        "libraries",
        bookaroo_pb2.Operation.UPDATE,
        data=library.to_grpc(),
        token="token",
        query=""
    )
    if response.code != 200:
        raise HTTPException(
            status_code=response.code,
            detail=response.message
        )
    return json.loads(response.message)


@app.post("/user/register", tags=["user"])
async def register(
        name: str,
        login: str,
        password: str,
        request: Request
):
    bklog = PostBookarooLog(
        user_id="",
        ip=request.client.host,
        method=Methods.POST.name,
        endpoint="/user/register"
    )
    RabbitMq().publish(bklog.to_json())
    user = User(
        login=login,
        password=password,
        name=name,
        token=""
    )

    # if get_user_by_email(user.login) is not None:
    #     raise HTTPException(
    #         status_code=403,
    #         detail="User already exists."
    #     )
    # if (not user.has_valid_email()
    #         or not user.has_valid_password()):
    #     raise HTTPException(
    #         status_code=422,
    #         detail="Invalid email or password."
    #     )
    # registered_user = user.register()
    # registered_user.password = None
    # registered_user.token = registered_user.id
    # return registered_user.to_response()

    user = User(
        login=login,
        password=password,
        name=name,
        token=""
    )
    response = GRPC.request(
        "readers",
        bookaroo_pb2.Operation.INSERT,
        data=user.to_grpc(),
        token="token",
        query=""
    )
    if response.code != 200:
        raise HTTPException(
            status_code=response.code,
            detail=response.message
        )
    user_dict = json.loads(response.message)
    # user_id = user_dict.pop("id")

    return User(**user_dict, password="").to_response()


@app.post("/user/login", tags=["user"])
async def login(login: str, password: str, request: Request):
    bklog = PostBookarooLog(
        user_id=login,
        ip=request.client.host,
        method=Methods.POST.name,
        endpoint="/user/login"
    )
    RabbitMq().publish(bklog.to_json())
    if login is None or password is None:
        raise HTTPException(
            status_code=404,
            detail="Both password and login are needed."
        )
    user = User(
        login=login,
        password=password,
        name="",
        token=""
    )
    # print(user)
    # user.login = login
    # user.password = password
    # logged_user = user.log_in()
    # if logged_user is None:
    #     raise HTTPException(
    #         status_code=404,
    #         detail="Invalid email or password."
    #     )
    # logged_user.token = logged_user.id
    # return logged_user.to_response()

    response = GRPC.request(
        "readers",
        bookaroo_pb2.Operation.SELECT,
        data=user.to_grpc(),
        token="token",
        query=""
    )
    if response.code != 200:
        raise HTTPException(
            status_code=response.code,
            detail=response.message
        )
    user_dict = json.loads(response.message)
    # user_id = user_dict.pop("id")

    return User(**user_dict, password="").to_response()


@app.get("/user/logout", tags=["user"])
async def logout(request: Request):
    bklog = PostBookarooLog(
        user_id="",
        ip=request.client.host,
        method=Methods.GET.name,
        endpoint="/user/logout"
    )
    RabbitMq().publish(bklog.to_json())
    return {"message": "logged out"}


@app.get("/user/all_readers", tags=["user"])
async def get_readers(request: Request):
    bklog = PostBookarooLog(
        user_id="",
        ip=request.client.host,
        method=Methods.GET.name,
        endpoint="/user/all_readers"
    )
    RabbitMq().publish(bklog.to_json())
    # users_cursor = User.get_users()
    # users = [User.from_mongo(document) for document in users_cursor]
    # for i in range(0, len(users) - 1):
    #     users[i].password = None
    # return users

    response = GRPC.request(
        "readers",
        bookaroo_pb2.Operation.SELECT,
        data="",
        token="token",
        query="all"
    )

    if response.code != 200:
        raise HTTPException(
            status_code=response.code,
            detail=response.message
        )

    return json.loads(response.message)


@app.get("/user/close_account", tags=["user"])
async def remove_user(token: str, request: Request):
    bklog = PostBookarooLog(
        user_id=token,
        ip=request.client.host,
        method=Methods.GET.name,
        endpoint="/user/close_account"
    )
    RabbitMq().publish(bklog.to_json())
    # user = get_user_by_id(token)
    # if user is None:
    #     raise HTTPException(
    #         status_code=404,
    #         detail="Invalid token."
    #     )
    # user.close()
    # user.password = None
    # return {"data": user.to_response()}

    response = GRPC.request(
        "readers",
        bookaroo_pb2.Operation.DELETE,
        data="",
        token=token,
        query=""
    )

    if response.code != 200:
        raise HTTPException(
            status_code=response.code,
            detail=response.message
        )

    return json.loads(response.message)


@app.get("/badge/{badge_id}", tags=["badge"])
async def get_badge(badge_id: str):
    return {"data": f"badge {badge_id}"}


@app.post("/db/reset", tags=["admin"])
async def drop_all_collections(password: str, request: Request):
    bklog = PostBookarooLog(
        user_id="",
        ip=request.client.host,
        method=Methods.POST.name,
        endpoint="/db/reset"
    )
    RabbitMq().publish(bklog.to_json())
    if password != "delejvoledropuj":
        raise HTTPException(
            status_code=401,
            detail="nesahej na to"
        )
    # db = Database()
    # db.drop_all()
    # db.die()
    # return {"detail": "dropped"}
    response = GRPC.request(
        "admin",
        bookaroo_pb2.Operation.DELETE,
        data="",
        token=password,
        query=""
    )
    return "dropped"


@app.post("/rabbit")
async def rabbit(msg: str, request: Request):
    bklog = PostBookarooLog(
        user_id="",
        ip=request.client.host,
        method=Methods.POST.name,
        endpoint="/rabbit"
    )
    RabbitMq().publish(bklog.to_json())
    # print(bklog.to_json())
    return {"data": f"msg <{msg}> sent"}


@app.post("/grpc")
async def grpc(msg: str, request: Request):
    user = User(
        login="login@ex.com",
        password="pass.123",
        name="jmeno",
        token=""
    )
    response = GRPC.request(
        "readers",
        bookaroo_pb2.Operation.INSERT,
        data=user.to_grpc(),
        token="token",
        query=""
    )
    if response.code != 200:
        raise HTTPException(
            status_code=response.code,
            detail=response.message
        )
    return {"data": f"msg <{msg}> sent"}
