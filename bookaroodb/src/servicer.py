from proto import bookaroo_pb2_grpc, bookaroo_pb2
from schemas.user import get_user_by_email, User, get_user_by_id
import json

from schemas.library import get_library_by_id, Library, get_libraries
from schemas.book import Book
from database import Database
from datetime import datetime


class BookarooServicer(bookaroo_pb2_grpc.RequestProcessorServicer):
    def process(self, request, context):
        BookarooServicer.log(request)
        if request.collectionName == "admin":
            db = Database()
            db.drop_all()
            db.die()
        elif request.collectionName == "readers":
            return BookarooServicer.process_readers(request)
        elif request.collectionName == "books":
            return BookarooServicer.process_books(request)
        elif request.collectionName == "libraries":
            return BookarooServicer.process_libraries(request)
        else:
            return bookaroo_pb2.Response(
                code=500,
                message="no such collection"
            )

    @staticmethod
    def process_readers(request):
        message = ""
        user_json = request.data
        if request.operation == bookaroo_pb2.Operation.INSERT:
            user_dict = json.loads(user_json)
            user_dict.pop("id")
            user = User(**user_dict)

            if get_user_by_email(user.login) is not None:
                return bookaroo_pb2.Response(
                    code=403,
                    message="User already exists."
                )
            if (not user.has_valid_email()
                    or not user.has_valid_password()):
                return bookaroo_pb2.Response(
                    code=422,
                    message="Invalid email or password."
                )
            registered_user = user.register()
            registered_user.password = None
            registered_user.token = registered_user.id
            message = registered_user.to_grpc()
        elif request.operation == bookaroo_pb2.Operation.SELECT:
            if request.query == "":
                user_dict = json.loads(user_json)
                user = User(
                    login=user_dict["login"],
                    password=user_dict["password"],
                    name="",
                    token=""
                )
                logged_user = user.log_in()
                if logged_user is None:
                    return bookaroo_pb2.Response(
                        code=404,
                        message="Invalid email or password."
                    )
                logged_user.token = logged_user.id
                message = logged_user.to_grpc()
            else:
                users_cursor = User.get_users()
                users = [User.from_mongo(document) for document in users_cursor]
                jsoned_users = []
                for i in range(0, len(users) - 1):
                    users[i].password = None
                    jsoned_users.append(users[i].to_grpc())
                message = "[" + ", ".join(jsoned_users) + "]"
        elif request.operation == bookaroo_pb2.Operation.DELETE:
            try:
                user = get_user_by_id(request.token)
                # if user is None:
                #     raise Exception
            except:
                return bookaroo_pb2.Response(
                    code=404,
                    message="Invalid token."
                )
            if user is None:
                return bookaroo_pb2.Response(
                    code=404,
                    message="Invalid token."
                )
            user.close()
            user.password = None
            message = user.to_grpc()
        elif request.operation == bookaroo_pb2.Operation.UPDATE:
            message = "updated"
        else:
            return bookaroo_pb2.Response(
                code=500,
                message="no such operation"
            )
        return bookaroo_pb2.Response(
            code=200,
            message=message
        )

    @staticmethod
    def process_libraries(request):
        message = ""
        lib_json = request.data
        if request.operation == bookaroo_pb2.Operation.INSERT:
            lib_dict = json.loads(lib_json)
            lib_dict.pop("id")
            library = Library(**lib_dict)

            lib = (library
                   .create_library()
                   .update_total()
                   .update_favourite()
                   .update_read())

            if lib is None:
                return bookaroo_pb2.Response(
                    code=404,
                    message="Library does not exist."
                )
            message = lib.to_grpc()

        elif request.operation == bookaroo_pb2.Operation.SELECT:
            if request.query == "":
                try:
                    lib = get_library_by_id(request.data)
                except:
                    lib = None
                if lib is None:
                    return bookaroo_pb2.Response(
                        code=404,
                        message="Library does not exist."
                    )
                message = lib.to_grpc()
            else:
                token = request.token
                try:
                    libs_cursor = get_libraries(token)
                    libs = [Library.from_mongo(document)
                            .update_total()
                            .update_favourite()
                            .update_read()
                            for document in libs_cursor]
                    jsoned_libs = []
                    for lib in libs:
                        jsoned_libs.append(lib.to_grpc())
                    message = "[" + ", ".join(jsoned_libs) + "]"
                except:
                    return bookaroo_pb2.Response(
                        code=401,
                        message="Unauthorized."
                    )

        elif request.operation == bookaroo_pb2.Operation.UPDATE:
            try:
                lib = json.loads(lib_json)
                lib = get_library_by_id(lib["id"])
            except:
                lib = None
            if lib is None:
                return bookaroo_pb2.Response(
                    code=404,
                    message="Library does not exist."
                )
            updated_library = lib.update_library()
            message = updated_library.to_grpc()
        elif request.operation == bookaroo_pb2.Operation.DELETE:
            return bookaroo_pb2.Response(
                code=500,
                message="no such operation"
            )
        else:
            return bookaroo_pb2.Response(
                code=500,
                message="no such operation"
            )
        return bookaroo_pb2.Response(
            code=200,
            message=message
        )

    @staticmethod
    def process_books(request):
        message = ""
        if request.operation == bookaroo_pb2.Operation.INSERT:
            try:
                book_dict = json.loads(request.data)
                # book_id = book_dict.pop("id")
                # book_id = book_dict.pop("read")
                # book_id = book_dict.pop("favourite")
                book = Book(**book_dict)
                inserted_book = book.create_book()
            except:
                return bookaroo_pb2.Response(
                    code=404,
                    message="no such book"
                )
            message = inserted_book.to_grpc()
        elif request.operation == bookaroo_pb2.Operation.SELECT:
            if request.query == "":
                book_id = request.data
                try:
                    selected_book = Book.get_book_by_id(book_id)
                except:
                    return bookaroo_pb2.Response(
                        code=404,
                        message="no such book"
                    )
                message = selected_book.to_grpc()
            elif request.query == "all":
                token = request.token
                try:
                    libs_cursor = get_libraries(token)

                    libs = [
                        Library.from_mongo(document)
                        for document in libs_cursor
                    ]
                    books_list = [
                        Book.get_books_by_library_id(lib.id)
                        for lib in libs
                    ]
                    books = [item for sublist in books_list for item in sublist]
                    jsoned_books = []
                    for book in books:
                        jsoned_books.append(book.to_grpc())
                    message = "[" + ", ".join(jsoned_books) + "]"
                except:
                    return bookaroo_pb2.Response(
                        code=401,
                        message="Unauthorized."
                    )
            else:
                token = request.token
                library_id = request.data
                try:

                    if not get_library_by_id(library_id):
                        return bookaroo_pb2.Response(
                            code=401,
                            message="No such book."
                        )
                    books = Book.get_books_by_library_id(library_id)

                    jsoned_books = []
                    for book in books:
                        jsoned_books.append(book.to_grpc())
                    message = "[" + ", ".join(jsoned_books) + "]"
                except:
                    return bookaroo_pb2.Response(
                        code=401,
                        message="Unauthorized."
                    )

        elif request.operation == bookaroo_pb2.Operation.UPDATE:
            try:
                book_dict = json.loads(request.data)
                # book_id = book_dict.pop("id")
                # book_id = book_dict.pop("read")
                # book_id = book_dict.pop("favourite")
                book = Book(**book_dict)
                update_book = book.update_book()
            except:
                return bookaroo_pb2.Response(
                    code=404,
                    message="no such book"
                )
            message = update_book.to_grpc()
        elif request.operation == bookaroo_pb2.Operation.DELETE:
            try:
                book = Book.remove_book_by_id(request.data)
            except:
                book = None
            if book is None:
                return bookaroo_pb2.Response(
                    code=404,
                    message="no such book"
                )
            message = book.to_grpc()
        else:
            return bookaroo_pb2.Response(
                code=500,
                message="no such operation"
            )
        return bookaroo_pb2.Response(
            code=200,
            message=message
        )

    @staticmethod
    def log(request):
        print("||--------------------------------||")
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
        op = 1
        if request.operation == bookaroo_pb2.Operation.INSERT:
            op = "Operation.INSERT"
        if request.operation == bookaroo_pb2.Operation.DELETE:
            op = "Operation.DELETE"
        if request.operation == bookaroo_pb2.Operation.SELECT:
            op = "Operation.SELECT"
        if request.operation == bookaroo_pb2.Operation.UPDATE:
            op = "Operation.UPDATE"
        print("COLLECTION: " + request.collectionName)
        print("OPERATION : " + op)
        print("TOKEN     : " + request.token)
        print("DATA      : " + request.data)
        print("QUERY     : " + request.query)
        print("||--------------------------------||")
        print("||XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX||")
