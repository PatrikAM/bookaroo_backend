from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from schemas.BookarooLog import BookarooLog, Base
from schemas.PostBookarooLog import PostBookarooLog

import uuid


class Database:
    # engine = create_engine(
    #     "postgresql://postgres:postgres@localhost/review"
    # )
    #
    # __session__ = sessionmaker(
    #     autocommit=False,
    #     autoflush=False,
    #     bind=engine
    # )

    @staticmethod
    def get_db():
        db = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=create_engine(
                "postgresql://example:example@localhost/boookaroo_logs"
            )
        )
        try:
            yield db
        finally:
            db.close()


    @staticmethod
    def insert_log(db: Session, log: PostBookarooLog):
        # db2 = sessionmaker(
        #     autocommit=False,
        #     autoflush=False,
        #     bind=create_engine(
        #         "postgresql://example:example@localhost/boookaroo_logs"
        #     )
        # )
        # db_logs = BookarooLog(id=uuid.uuid4, **log.__dict__)
        # db2.add(db_logs)
        # db2.commit()
        # db2.refresh(db_logs)
        # db2.close()
        # return db_review

        # try:
            engine = create_engine(
                'postgresql://example:example@localhost:5432/bookaroo_logs')
            Base.metadata.create_all(engine)
            session = Session(engine)
            l = BookarooLog(id=uuid.uuid4(), **log.__dict__)
            session.add(l)

            session.commit()
            session.refresh(l)
            session.close()
        # except Exception as e:
        #     print('Unable to access postgresql database', repr(e))
