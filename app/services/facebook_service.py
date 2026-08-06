from typing import List, Dict, Any, Optional
import httpx
from app.config import settings
from app.utils.security import decrypt_token


class FacebookService:
    BASE_URL = f"https://graph.facebook.com/{settings.FACEBOOK_GRAPH_VERSION}"

    @classmethod
    async def get_long_lived_user_token(cls, short_lived_token: str) -> Optional[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            params = {
                "grant_type": "fb_exchange_token",
                "client_id": settings.FACEBOOK_APP_ID,
                "client_secret": settings.FACEBOOK_APP_SECRET,
                "fb_exchange_token": short_lived_token
            }
            res = await client.get(f"{cls.BASE_URL}/oauth/access_token", params=params)
            if res.status_code == 200:
                return res.json()
            return None

    @classmethod
    async def get_user_profile(cls, access_token: str) -> Optional[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            params = {"fields": "id,name", "access_token": access_token}
            res = await client.get(f"{cls.BASE_URL}/me", params=params)
            if res.status_code == 200:
                return res.json()
            return None

    @classmethod
    async def get_user_pages(cls, access_token: str) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            params = {"fields": "id,name,category,access_token", "access_token": access_token}
            res = await client.get(f"{cls.BASE_URL}/me/accounts", params=params)
            if res.status_code == 200:
                data = res.json()
                return data.get("data", [])
            return []

    @classmethod
    async def post_text(cls, page_access_token: str, page_id: str, message: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            payload = {"message": message, "access_token": page_access_token}
            res = await client.post(f"{cls.BASE_URL}/{page_id}/feed", data=payload)
            return res.json()

    @classmethod
    async def post_photo(cls, page_access_token: str, page_id: str, image_url: str, caption: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            payload = {"url": image_url, "caption": caption, "access_token": page_access_token}
            res = await client.post(f"{cls.BASE_URL}/{page_id}/photos", data=payload)
            return res.json()

    @classmethod
    async def post_video(cls, page_access_token: str, page_id: str, video_url: str, description: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            payload = {"file_url": video_url, "description": description, "access_token": page_access_token}
            res = await client.post(f"{cls.BASE_URL}/{page_id}/videos", data=payload)
            return res.json()

    @classmethod
    async def reply_comment(cls, page_access_token: str, comment_id: str, message: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            payload = {"message": message, "access_token": page_access_token}
            res = await client.post(f"{cls.BASE_URL}/{comment_id}/comments", data=payload)
            return res.json()

    @classmethod
    async def like_comment(cls, page_access_token: str, comment_id: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            payload = {"access_token": page_access_token}
            res = await client.post(f"{cls.BASE_URL}/{comment_id}/likes", data=payload)
            return res.json()
