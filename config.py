import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    BOT_TOKEN = os.getenv("BOT_TOKEN")

    APP_ID = os.getenv("FB_APP_ID")
    APP_SECRET = os.getenv("FB_APP_SECRET")

    BASE_URL = os.getenv("BASE_URL")
    OAUTH_REDIRECT_URI = f"{BASE_URL}/callback"

    DATABASE_URL = os.getenv("DATABASE_URL")

    SECRET_KEY = os.getenv("SECRET_KEY")

    ENCRYPTION_KEY = os.getenv("FB_PAGE_ACCESS_TOKEN_ENCRYPTION_KEY")

    ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    DEFAULT_TIMEZONE = "UTC"

    @classmethod
    def validate(cls):

        required = [
            "BOT_TOKEN",
            "APP_ID",
            "APP_SECRET",
            "BASE_URL",
            "DATABASE_URL",
            "SECRET_KEY",
            "ENCRYPTION_KEY",
        ]

        missing = []

        for item in required:
            if getattr(cls, item) in [None, ""]:
                missing.append(item)

        if missing:
            raise RuntimeError(
                f"Missing environment variables: {', '.join(missing)}"
            )
