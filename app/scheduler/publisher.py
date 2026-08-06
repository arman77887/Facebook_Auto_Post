import datetime
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.session import AsyncSessionLocal
from app.models.all_models import Post, PostStatus, PublishedPost, FacebookPage, PostType
from app.services.facebook_service import FacebookService
from app.utils.security import decrypt_token

logger = structlog.get_logger()


async def process_scheduled_posts():
    async with AsyncSessionLocal() as db:
        now = datetime.datetime.utcnow()
        result = await db.execute(
            select(Post)
            .filter(Post.status == PostStatus.SCHEDULED, Post.scheduled_at <= now)
        )
        posts_to_publish = result.scalars().all()

        for post in posts_to_publish:
            await execute_post_publish(db, post)


async def execute_post_publish(db: AsyncSession, post: Post) -> bool:
    page_result = await db.execute(select(FacebookPage).filter(FacebookPage.id == post.facebook_page_id))
    page = page_result.scalars().first()
    if not page:
        post.status = PostStatus.FAILED
        pub_err = PublishedPost(post_id=post.id, error_message="Associated Facebook Page not found.")
        db.add(pub_err)
        await db.commit()
        return False

    decrypted_page_token = decrypt_token(page.encrypted_access_token)
    res = {}
    try:
        if post.post_type == PostType.TEXT:
            res = await FacebookService.post_text(decrypted_page_token, page.page_id, post.message or "")
        elif post.post_type == PostType.PHOTO:
            res = await FacebookService.post_photo(decrypted_page_token, page.page_id, post.media_url or "", post.message or "")
        elif post.post_type == PostType.VIDEO:
            res = await FacebookService.post_video(decrypted_page_token, page.page_id, post.media_url or "", post.message or "")

        if "id" in res:
            post.status = PostStatus.PUBLISHED
            pub_record = PublishedPost(post_id=post.id, fb_post_id=res["id"])
            db.add(pub_record)
            await db.commit()
            return True
        else:
            err_msg = res.get("error", {}).get("message", "Unknown Facebook API error")
            post.status = PostStatus.FAILED
            pub_record = PublishedPost(post_id=post.id, error_message=err_msg)
            db.add(pub_record)
            await db.commit()
            return False
    except Exception as e:
        logger.error("Publishing error", post_id=post.id, error=str(e))
        post.status = PostStatus.FAILED
        pub_record = PublishedPost(post_id=post.id, error_message=str(e))
        db.add(pub_record)
        await db.commit()
        return False
