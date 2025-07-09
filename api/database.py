import datetime

from sqlalchemy import Column, DateTime, Integer, String, create_engine

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, DeclarativeBase
from typing import Any

DATABASE_URL = "sqlite:///./rank.db"

engine = create_engine(DATABASE_URL)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base: Any = declarative_base()
Base.query = db_session.query_property()


class Rank(Base):
    __tablename__ = "ranks"
    id = Column(Integer, primary_key=True)
    player_name = Column(String(50), nullable=False)
    score = Column(Integer, nullable=False)
    level = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, player_name, score, level):
        self.player_name = player_name
        self.score = score
        self.level = level

    def __repr__(self):
        return f"<Rank {self.player_name} - {self.score} ({self.level})>"


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.
    # Otherwise, you will have to import them first before calling init_db()
    Base.metadata.create_all(bind=engine)
