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

# ==========================
# SCHEDULED POST
# ==========================

class ScheduledPost(Base):

    __tablename__ = "scheduled_posts"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    page_id = Column(
        Integer,
        ForeignKey("facebook_pages.id")
    )

    post_type = Column(
        String(20)
    )

    caption = Column(
        Text
    )

    media_url = Column(
        Text
    )

    schedule_time = Column(
        DateTime
    )

    status = Column(
        String(20),
        default="PENDING"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="scheduled_posts"
    )

    page = relationship(
        "FacebookPage"
    )


# ==========================
# PUBLISHED POST
# ==========================

class PublishedPost(Base):

    __tablename__ = "published_posts"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    page_id = Column(
        Integer,
        ForeignKey("facebook_pages.id")
    )

    facebook_post_id = Column(
        String(255)
    )

    post_type = Column(
        String(20)
    )

    caption = Column(
        Text
    )

    published_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="published_posts"
    )

    page = relationship(
        "FacebookPage"
    )

# ==========================
# COMMENT AUTO REPLY
# ==========================

class CommentReply(Base):

    __tablename__ = "comment_replies"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    page_id = Column(
        Integer,
        ForeignKey("facebook_pages.id")
    )

    enabled = Column(
        Boolean,
        default=False
    )

    reply_message = Column(
        Text
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

# ==========================
# PREMIUM USER
# ==========================

class PremiumUser(Base):

    __tablename__ = "premium_users"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    expires_at = Column(
        DateTime
    )

    active = Column(
        Boolean,
        default=True
    )

# ==========================
# SUPPORT TICKET
# ==========================

class SupportTicket(Base):

    __tablename__ = "support_tickets"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    subject = Column(
        String(255)
    )

    message = Column(
        Text
    )

    status = Column(
        String(30),
        default="OPEN"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

# ==========================
# SETTINGS
# ==========================

class Setting(Base):

    __tablename__ = "settings"

    id = Column(
        Integer,
        primary_key=True
    )

    key = Column(
        String(100),
        unique=True
    )

    value = Column(
        Text
    )
