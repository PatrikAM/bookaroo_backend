from sqlalchemy import Column, UUID, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BookarooLog(Base):
    __tablename__ = "bookaroo_logs"

    id = Column(UUID, primary_key=True, index=True)
    datetime = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(String)
    ip = Column(String)
    endpoint = Column(String)
    method = Column(String)
