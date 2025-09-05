from __future__ import annotations

from typing import List

from fastapi import FastAPI, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from collections.abc import AsyncGenerator
from fastapi.middleware.cors import CORSMiddleware

from models import *
from settings import DATABASE_URL
from docs.tags import tags


def get_engine():
    return create_async_engine(DATABASE_URL, echo=True, future=True)


def get_session():
    engine = get_engine()
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    SessionLocal = get_session()
    async with SessionLocal() as session:
        yield session

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/check-db", status_code=status.HTTP_200_OK, tags=[tags["db_tag"]])
async def select_demo(session: AsyncSession = Depends(get_db_session)):
    try:
        result = await session.execute(text("SELECT NOW() as now"))
        row = result.fetchone()
        return {"status": "ok", "result": dict(row._mapping) if row else None}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.get("/db-schema", status_code=status.HTTP_200_OK, tags=[tags["db_tag"]])
async def db_schema(session: AsyncSession = Depends(get_db_session)):
    try:
        # Get all table names in the public schema
        tables_result = await session.execute(text("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """))
        table_names = [row[0] for row in tables_result.fetchall()]

        schema = {}
        for table in table_names:
            columns_result = await session.execute(text(f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = :table
            """), {"table": table})
            columns = [
                {"name": col[0], "type": col[1]} for col in columns_result.fetchall()
            ]
            schema[table] = columns
        return {"status": "ok", "schema": schema}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.get("/books", status_code=status.HTTP_200_OK, tags=[tags["book_tag"]])
async def read_books(session: AsyncSession = Depends(get_db_session)):
    try:
        result = await session.execute(text("SELECT * FROM book"))
        books = [dict(row._mapping) for row in result.fetchall()]
        books.reverse()
        return {"books": books}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.get("/libraries", status_code=status.HTTP_200_OK, tags=[tags["library_tag"]])
async def read_libraries(session: AsyncSession = Depends(get_db_session)):
    try:
        result = await session.execute(text("SELECT * FROM library"))
        library = [dict(row._mapping) for row in result.fetchall()]
        return {"library": library}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.get("/readers", status_code=status.HTTP_200_OK, tags=[tags["reader_tag"]])
async def read_readers(session: AsyncSession = Depends(get_db_session)):
    try:
        result = await session.execute(text("SELECT * FROM reader"))
        readers = [dict(row._mapping) for row in result.fetchall()]
        return {"readers": readers}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.get("/books/borrowed/{reader_id}", status_code=status.HTTP_200_OK,
         tags=[tags["book_tag"]])
async def read_libraries(session: AsyncSession = Depends(get_db_session)):
    try:
        result = await session.execute(text("SELECT * FROM book WHERE borrower_id = :reader_id"))
        books = [dict(row._mapping) for row in result.fetchall()]
        return {"books": books}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/books/owned/{reader_id}", status_code=status.HTTP_200_OK, tags=[tags["book_tag"]])
async def read_libraries(session: AsyncSession = Depends(get_db_session)):
    try:
        result = await session.execute(text("SELECT * FROM book WHERE reader_id = :reader_id"))
        books = [dict(row._mapping) for row in result.fetchall()]
        return {"books": books}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.post("/reader", status_code=status.HTTP_201_CREATED, tags=[tags["reader_tag"]])
async def create_reader(payload: ReaderCreateRequest, session: AsyncSession = Depends(get_db_session)):
    try:
        result = await session.execute(text("""
            INSERT INTO reader (name, sex, email, surname)
            VALUES (:name, :sex, :email, :surname)
            RETURNING *
        """), {
            "name": payload.name,
            "sex": payload.sex,
            "email": payload.email,
            "surname": payload.surname
        })
        await session.commit()
        reader = [dict(row._mapping) for row in result.fetchall()]
        return {"reader": reader}
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.put("/reader/{reader_id}", status_code=status.HTTP_202_ACCEPTED, tags=[tags["reader_tag"]])
async def update_reader(reader_id: int, payload: ReaderCreateRequest, session: AsyncSession = Depends(get_db_session)):
    try:
        result = await session.execute(text("""
            UPDATE reader
            SET name = :name,
                sex = :sex,
                email = :email,
                surname = :surname
            WHERE id = :reader_id
            RETURNING *
        """), {
            "name": payload.name,
            "sex": payload.sex,
            "email": payload.email,
            "surname": payload.surname,
            "reader_id": reader_id
        })
        await session.commit()
        reader = [dict(row._mapping) for row in result.fetchall()]
        return {"reader": reader}
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.post("/library", status_code=status.HTTP_201_CREATED, tags=[tags["library_tag"]])
async def create_library(payload: LibraryCreateRequest, session: AsyncSession = Depends(get_db_session)):
    try:
        result = await session.execute(text("""
            INSERT INTO library (name, address, floor)
            VALUES (:name, :address, :floor)
            RETURNING *
        """), {
            "name": payload.name,
            "address": payload.address,
            "floor": payload.floor,
        })
        await session.commit()
        reader = [dict(row._mapping) for row in result.fetchall()]
        return {"reader": reader}
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.put("/library/{library_id}", status_code=status.HTTP_202_ACCEPTED, tags=[tags["library_tag"]])
async def update_library(library_id: int, payload: LibraryCreateRequest, session: AsyncSession = Depends(get_db_session)):
    try:
        result = await session.execute(text("""
            UPDATE library
            SET name = :name,
                address = :address,
                floor = :floor
            WHERE id = :library_id
            RETURNING *
        """), {
            "name": payload.name,
            "address": payload.address,
            "floor": payload.floor,
            "library_id": library_id
        })
        await session.commit()
        library = [dict(row._mapping) for row in result.fetchall()]

        if not library:
            return JSONResponse(status_code=404, content={"status": "error", "message": "Library not found"})

        return {"library": library}
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.post("/book", status_code=status.HTTP_201_CREATED, tags=[tags["book_tag"]])
async def create_book(payload: BookCreateRequest, session: AsyncSession = Depends(get_db_session)):
    try:
        result = await session.execute(text("""
            INSERT INTO book (
                title, series, author, binding, cover_image,
                reader_id, publisher, published, isbn,
                borrower_id, library_id, interval_value
            )
            VALUES (
                :title, :series, :author, :binding, :cover_image,
                :reader_id, :publisher, :published, :isbn,
                :borrower_id, :library_id, :interval_value
            )
            RETURNING *
        """), {
            "title": payload.title,
            "series": payload.series,
            "author": payload.author,
            "binding": payload.binding,
            "cover_image": payload.cover_image,
            "reader_id": payload.reader_id,
            "publisher": payload.publisher,
            "published": payload.published,
            "isbn": payload.isbn,
            "borrower_id": payload.borrower_id,
            "library_id": payload.library_id,
            "interval_value": payload.interval_value,
        })
        await session.commit()
        books = [dict(row._mapping) for row in result.fetchall()]
        return {"books": books}
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.get("/book/{book_id}", status_code=status.HTTP_200_OK, tags=[tags["book_tag"]])
async def read_book_by_id(book_id: int, session: AsyncSession = Depends(get_db_session)):
    try:
        result = await session.execute(text("SELECT * FROM book WHERE id = :book_id"), {"book_id": book_id})
        book = [dict(row._mapping) for row in result.fetchall()][0]
        if not book:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"status": "error", "message": f"Config with id {book_id} not found"}
            )
        return {"book": book}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.get("/library/{library_id}", status_code=status.HTTP_200_OK, tags=[tags["library_tag"]])
async def read_library_by_id(library_id: int, session: AsyncSession = Depends(get_db_session)):
    try:
        result = await session.execute(text("SELECT * FROM library WHERE id = :library_id"), {"library_id": library_id})
        library = result.fetchone()
        if not library:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"status": "error", "message": f"Measurement with id {library_id} not found"}
            )
        return {"library": dict(library._mapping)}
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.put("/books/{book_id}", status_code=status.HTTP_202_ACCEPTED, tags=[tags["book_tag"]])
async def update_book(book_id: int, payload: BookCreateRequest, session: AsyncSession = Depends(get_db_session)):
    try:
        result = await session.execute(text("""
            UPDATE books
            SET title = :title,
                subtitle = :subtitle,
                author = :author,
                binding = :binding,
                cover_image = :cover_image,
                reader_id = :reader_id,
                publisher = :publisher,
                published = :published,
                isbn = :isbn,
                borrower_id = :borrower_id,
                library_id = :library_id,
                interval_value = :interval_value
            WHERE id = :book_id
            RETURNING *
        """), {
            "title": payload.title,
            "subtitle": payload.subtitle,
            "author": payload.author,
            "binding": payload.binding,
            "cover_image": payload.cover_image,
            "reader_id": payload.reader_id,
            "publisher": payload.publisher,
            "published": payload.published,
            "isbn": payload.isbn,
            "borrower_id": payload.borrower_id,
            "library_id": payload.library_id,
            "interval_value": payload.interval_value,
            "book_id": book_id
        })
        await session.commit()
        book = [dict(row._mapping) for row in result.fetchall()]

        if not book:
            return JSONResponse(status_code=404, content={"status": "error", "message": "Book not found"})

        return {"book": book}
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})



@app.get("/reader/{reader_id}", status_code=status.HTTP_200_OK, tags=[tags["reader_tag"]])
async def read_reader_by_id(reader_id: int, session: AsyncSession = Depends(get_db_session)):
    try:
        result = await session.execute(text("SELECT * FROM reader WHERE id = :reader_id"), {"reader_id": reader_id})
        reader = result.fetchone()
        if not reader:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"status": "error", "message": f"Reader with id {reader_id} not found"}
            )
        return {"reader": dict(reader._mapping)}
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.get("/books/{library_id}", status_code=status.HTTP_200_OK, tags=[tags["book_tag"]])
async def read_book_by_library_id(library_id: int, session: AsyncSession = Depends(get_db_session)):
    try:
        result = await session.execute(text("SELECT * FROM book WHERE library_id = :library_id"), {"library_id": library_id})
        books = result.fetchall()
        if not books:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"status": "error", "message": f"Books with library id {library_id} not found"}
            )
        return {"books": [dict(row._mapping) for row in books]}
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.post("/readers/bulk", status_code=status.HTTP_201_CREATED, tags=[tags["reader_tag"]])
async def bulk_import_readers(payload: List[ReaderCreateRequest], session: AsyncSession = Depends(get_db_session)):
    try:
        values = [dict(
            name=item.name,
            sex=item.sex,
            email=item.email,
            surname=item.surname
        ) for item in payload]

        result = await session.execute(text("""
            INSERT INTO reader (name, sex, email, surname)
            VALUES (:name, :sex, :email, :surname)
            RETURNING *
        """), values)

        await session.commit()
        readers = [dict(row._mapping) for row in result.fetchall()]
        return {"readers": readers}
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.post("/libraries/bulk", status_code=status.HTTP_201_CREATED, tags=[tags["library_tag"]])
async def bulk_import_libraries(payload: List[LibraryCreateRequest], session: AsyncSession = Depends(get_db_session)):
    try:
        values = [dict(
            name=item.name,
            address=item.address,
            floor=item.floor
        ) for item in payload]

        result = await session.execute(text("""
            INSERT INTO library (name, address, floor)
            VALUES (:name, :address, :floor)
            RETURNING *
        """), values)

        await session.commit()
        libraries = [dict(row._mapping) for row in result.fetchall()]
        return {"libraries": libraries}
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.post("/books/bulk", status_code=status.HTTP_201_CREATED, tags=[tags["book_tag"]])
async def bulk_import_books(payload: List[BookCreateRequest], session: AsyncSession = Depends(get_db_session)):
    try:
        values = [dict(
            title=item.title,
            subtitle=item.subtitle,
            author=item.author,
            binding=item.binding,
            cover_image=item.cover_image,
            reader_id=item.reader_id,
            publisher=item.publisher,
            published=item.published,
            isbn=item.isbn,
            borrower_id=item.borrower_id,
            library_id=item.library_id,
            interval_value=item.interval_value
        ) for item in payload]

        result = await session.execute(text("""
            INSERT INTO books (
                title, subtitle, author, binding, cover_image,
                reader_id, publisher, published, isbn,
                borrower_id, library_id, interval_value
            )
            VALUES (
                :title, :subtitle, :author, :binding, :cover_image,
                :reader_id, :publisher, :published, :isbn,
                :borrower_id, :library_id, :interval_value
            )
            RETURNING *
        """), values)

        await session.commit()
        books = [dict(row._mapping) for row in result.fetchall()]
        return {"books": books}
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
