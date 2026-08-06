import datetime
from sqlalchemy import (
    Column, BigInteger, String, Boolean, DateTime, ForeignKey, Text, Enum, Integer
)
from sqlalchemy.orm import relationship
import enum
from app.database.session import Base


class PostStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"


class PostType(str, enum.Enum):
    TEXT = "TEXT"
    PHOTO = "PHOTO"
    VIDEO = "VIDEO"


class TicketStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    timezone = Column(String(100), default="UTC")
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    facebook_accounts = relationship("FacebookAccount", back_populates="user", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    support_tickets = relationship("SupportTicket", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    logs = relationship("Log", back_populates="user", cascade="all, delete-orphan")


class FacebookAccount(Base):
    __tablename__ = "facebook_accounts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    facebook_user_id = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    encrypted_access_token = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="facebook_accounts")
    pages = relationship("FacebookPage", back_populates="account", cascade="all, delete-orphan")


class FacebookPage(Base):
    __tablename__ = "facebook_pages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    facebook_account_id = Column(BigInteger, ForeignKey("facebook_accounts.id", ondelete="CASCADE"), nullable=False)
    page_id = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(255), nullable=True)
    encrypted_access_token = Column(Text, nullable=False)
    auto_reply_enabled = Column(Boolean, default=False)
    auto_like_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    account = relationship("FacebookAccount", back_populates="pages")
    posts = relationship("Post", back_populates="page", cascade="all, delete-orphan")
    comment_replies = relationship("CommentReply", back_populates="page", cascade="all, delete-orphan")


class Post(Base):
    __tablename__ = "posts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    facebook_page_id = Column(BigInteger, ForeignKey("facebook_pages.id", ondelete="CASCADE"), nullable=False)
    post_type = Column(Enum(PostType), nullable=False)
    message = Column(Text, nullable=True)
    media_url = Column(Text, nullable=True)
    status = Column(Enum(PostStatus), default=PostStatus.DRAFT)
    scheduled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="posts")
    page = relationship("FacebookPage", back_populates="posts")
    published_record = relationship("PublishedPost", back_populates="post", uselist=False, cascade="all, delete-orphan")


class PublishedPost(Base):
    __tablename__ = "published_posts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    post_id = Column(BigInteger, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    fb_post_id = Column(String(255), nullable=True)
    error_message = Column(Text, nullable=True)
    published_at = Column(DateTime, default=datetime.datetime.utcnow)

    post = relationship("Post", back_populates="published_record")


class CommentReply(Base):
    __tablename__ = "comment_replies"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    page_id = Column(BigInteger, ForeignKey("facebook_pages.id", ondelete="CASCADE"), nullable=False)
    comment_id = Column(String(255), nullable=False, unique=True)
    post_id = Column(String(255), nullable=False)
    user_message = Column(Text, nullable=False)
    ai_reply = Column(Text, nullable=False)
    liked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    page = relationship("FacebookPage", back_populates="comment_replies")


class PremiumPlan(Base):
    __tablename__ = "premium_plans"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)
    duration_days = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)

    subscriptions = relationship("Subscription", back_populates="plan", cascade="all, delete-orphan")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(BigInteger, ForeignKey("premium_plans.id", ondelete="CASCADE"), nullable=False)
    start_date = Column(DateTime, default=datetime.datetime.utcnow)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="subscriptions")
    plan = relationship("PremiumPlan", back_populates="subscriptions")


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN)
    admin_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="support_tickets")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="notifications")


class Log(Base):
    __tablename__ = "logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    level = Column(String(50), nullable=False)
    action = Column(String(255), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="logs")
