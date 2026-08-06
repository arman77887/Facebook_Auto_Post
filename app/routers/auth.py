from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.session import get_db
from app.models.all_models import User, FacebookAccount, FacebookPage
from app.services.facebook_service import FacebookService
from app.utils.security import encrypt_token
from app.config import settings

router = APIRouter(prefix="/auth/facebook", tags=["Facebook OAuth"])


@router.get("/login")
async def facebook_login(telegram_id: int = Query(...)):
    redirect_uri = f"{settings.BASE_URL}/auth/facebook/callback"
    scope = "pages_show_list,pages_read_engagement,pages_manage_posts,pages_manage_engagement,public_profile"
    fb_url = (
        f"https://www.facebook.com/{settings.FACEBOOK_GRAPH_VERSION}/dialog/oauth?"
        f"client_id={settings.FACEBOOK_APP_ID}&redirect_uri={redirect_uri}"
        f"&state={telegram_id}&scope={scope}"
    )
    return RedirectResponse(url=fb_url)


@router.get("/callback")
async def facebook_callback(code: str = Query(...), state: str = Query(...), db: AsyncSession = Depends(get_db)):
    telegram_id = int(state)
    redirect_uri = f"{settings.BASE_URL}/auth/facebook/callback"

    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"https://graph.facebook.com/{settings.FACEBOOK_GRAPH_VERSION}/oauth/access_token",
            params={
                "client_id": settings.FACEBOOK_APP_ID,
                "client_secret": settings.FACEBOOK_APP_SECRET,
                "redirect_uri": redirect_uri,
                "code": code
            }
        )
        if res.status_code != 200:
            raise HTTPException(status_code=400, detail="OAuth verification failed")

        token_data = res.json()
        short_token = token_data.get("access_token")

    long_token_resp = await FacebookService.get_long_lived_user_token(short_token)
    long_token = long_token_resp.get("access_token") if long_token_resp else short_token

    profile = await FacebookService.get_user_profile(long_token)
    if not profile:
        raise HTTPException(status_code=400, detail="Failed to fetch profile")

    user_res = await db.execute(select(User).filter(User.telegram_id == telegram_id))
    user = user_res.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    enc_user_token = encrypt_token(long_token)
    fb_acc = FacebookAccount(
        user_id=user.id,
        facebook_user_id=profile["id"],
        name=profile["name"],
        encrypted_access_token=enc_user_token
    )
    db.add(fb_acc)
    await db.commit()
    await db.refresh(fb_acc)

    pages = await FacebookService.get_user_pages(long_token)
    for p in pages:
        enc_page_token = encrypt_token(p["access_token"])
        fb_page = FacebookPage(
            facebook_account_id=fb_acc.id,
            page_id=p["id"],
            name=p["name"],
            category=p.get("category"),
            encrypted_access_token=enc_page_token
        )
        db.add(fb_page)

    await db.commit()
    return {"status": "success", "message": "Facebook Account and Pages successfully connected! Return to Telegram."}
  
