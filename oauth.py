import secrets
import requests

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse

from config import Config

from facebook import (
    exchange_long_token,
    get_me,
    get_pages,
    encrypt_token,
)

from database import SessionLocal

from models import (
    User,
    FacebookAccount,
    FacebookPage,
)

app = FastAPI()

STATE = {}
@app.get("/login/{telegram_id}")

async def login(telegram_id: int):

    state = secrets.token_hex(16)

    STATE[state] = telegram_id

    url = (

        "https://www.facebook.com/v23.0/dialog/oauth"

        f"?client_id={Config.APP_ID}"

        f"&redirect_uri={Config.OAUTH_REDIRECT_URI}"

        f"&state={state}"

        "&scope="

        "pages_show_list,"

        "pages_manage_posts,"

        "pages_read_engagement,"

        "pages_manage_metadata"

    )

    return RedirectResponse(url)
  @app.get("/callback")

async def callback(

    code: str,

    state: str,

):

    if state not in STATE:

        return HTMLResponse(

            "<h2>Invalid State</h2>",

            status_code=400

        )

    telegram_id = STATE.pop(state)
      token_response = requests.get(

        "https://graph.facebook.com/v23.0/oauth/access_token",

        params={

            "client_id": Config.APP_ID,

            "client_secret": Config.APP_SECRET,

            "redirect_uri": Config.OAUTH_REDIRECT_URI,

            "code": code

        },

        timeout=120

    )

    token_response.raise_for_status()

    short_token = token_response.json()["access_token"]

    long_token = exchange_long_token(short_token)
    me = get_me(long_token)

    pages = get_pages(long_token)
    db = SessionLocal()

    try:
            user = (

            db.query(User)

            .filter(

                User.telegram_id == str(telegram_id)

            )

            .first()

        )


        if not user:

            user = User(

                telegram_id=str(telegram_id),

                full_name=me.get("name"),

            )

            db.add(user)

            db.commit()

            db.refresh(user)
        account = (

            db.query(FacebookAccount)

            .filter(

                FacebookAccount.facebook_id == me["id"]

            )

            .first()

        )


        if not account:

            account = FacebookAccount(

                user_id=user.id,

                facebook_id=me["id"],

                name=me["name"],

                access_token=encrypt_token(long_token)

            )

            db.add(account)

        else:

            account.access_token = encrypt_token(long_token)

            account.name = me["name"]
                 for page in pages:

            db_page = (

                db.query(FacebookPage)

                .filter(

                    FacebookPage.page_id == page["id"]

                )

                .first()

            )


            if db_page:

                db_page.page_name = page["name"]

                db_page.category = page.get(

                    "category",

                    ""

                )

                db_page.access_token = encrypt_token(

                    page["access_token"]

                )

                db_page.connected = True

            else:

                db.add(

                    FacebookPage(

                        user_id=user.id,

                        page_id=page["id"],

                        page_name=page["name"],

                        category=page.get(

                            "category",

                            ""

                        ),

                        access_token=encrypt_token(

                            page["access_token"]

                        ),

                        connected=True

                    )

                )
