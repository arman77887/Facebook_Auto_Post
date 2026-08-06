from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from config import Config

engine = create_engine(
    Config.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

Base = declarative_base()


def init_db():
    from models import (
        User,
        FacebookAccount,
        FacebookPage,
        ScheduledPost,
        PublishedPost,
        PremiumUser,
        SupportTicket,
        CommentReply,
    )

    Base.metadata.create_all(bind=engine)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
