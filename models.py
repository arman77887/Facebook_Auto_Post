from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
)

from sqlalchemy.orm import relationship

from database import Base


# ==========================
# USER
# ==========================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True
    )

    telegram_id = Column(
        String(50),
        unique=True,
        nullable=False
    )

    full_name = Column(
        String(255)
    )

    username = Column(
        String(255)
    )

    timezone = Column(
        String(100),
        default="UTC"
    )

    is_premium = Column(
        Boolean,
        default=False
    )

    is_admin = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    accounts = relationship(
        "FacebookAccount",
        back_populates="user",
        cascade="all, delete"
    )

    pages = relationship(
        "FacebookPage",
        back_populates="user",
        cascade="all, delete"
    )

    scheduled_posts = relationship(
        "ScheduledPost",
        back_populates="user",
        cascade="all, delete"
    )

    published_posts = relationship(
        "PublishedPost",
        back_populates="user",
        cascade="all, delete"
    )

# ==========================
# FACEBOOK ACCOUNT
# ==========================

class FacebookAccount(Base):

    __tablename__ = "facebook_accounts"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    facebook_id = Column(
        String(100)
    )

    name = Column(
        String(255)
    )

    access_token = Column(
        Text
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="accounts"
    )

# ==========================
# FACEBOOK PAGE
# ==========================

class FacebookPage(Base):

    __tablename__ = "facebook_pages"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    page_id = Column(
        String(100)
    )

    page_name = Column(
        String(255)
    )

    access_token = Column(
        Text
    )

    category = Column(
        String(255)
    )

    connected = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="pages"
    )
