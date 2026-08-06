from fastapi import APIRouter, Request, Response, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.session import get_db
from app.models.all_models import FacebookPage, CommentReply
from app.services.facebook_service import FacebookService
from app.services.openai_service import OpenAIService
from app.utils.security import decrypt_token
from app.config import settings

router = APIRouter(prefix="/webhooks/facebook", tags=["Facebook Webhook"])


@router.get("")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    if hub_mode == "subscribe" and hub_verify_token == settings.FACEBOOK_VERIFY_TOKEN:
        return Response(content=hub_challenge, media_type="text/plain")
    return Response(content="Verification failed", status_code=403)


@router.post("")
async def handle_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            page_id = entry.get("id")
            page_res = await db.execute(select(FacebookPage).filter(FacebookPage.page_id == page_id))
            page = page_res.scalars().first()

            if not page or not page.auto_reply_enabled:
                continue

            for change in entry.get("changes", []):
                val = change.get("value", {})
                if val.get("item") == "comment" and val.get("verb") == "add":
                    comment_id = val.get("comment_id")
                    comment_text = val.get("message")
                    post_id = val.get("post_id")

                    existing = await db.execute(select(CommentReply).filter(CommentReply.comment_id == comment_id))
                    if existing.scalars().first():
                        continue

                    page_token = decrypt_token(page.encrypted_access_token)

                    if page.auto_like_enabled:
                        await FacebookService.like_comment(page_token, comment_id)

                    reply_text = await OpenAIService.generate_comment_reply(comment_text, page.name)
                    await FacebookService.reply_comment(page_token, comment_id, reply_text)

                    record = CommentReply(
                        page_id=page.id,
                        comment_id=comment_id,
                        post_id=post_id,
                        user_message=comment_text,
                        ai_reply=reply_text,
                        liked=page.auto_like_enabled
                    )
                    db.add(record)
                    await db.commit()

    return {"status": "EVENT_RECEIVED"}
