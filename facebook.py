import requests

from cryptography.fernet import Fernet

from config import Config


GRAPH = "https://graph.facebook.com/v23.0"


class FacebookAPI:

    def __init__(self, access_token):

        self.access_token = access_token

    # ==========================
    # GRAPH REQUEST
    # ==========================

    def get(self, endpoint, params=None):

        if params is None:
            params = {}

        params["access_token"] = self.access_token

        r = requests.get(
            f"{GRAPH}/{endpoint}",
            params=params,
            timeout=60
        )

        r.raise_for_status()

        return r.json()


    def post(self, endpoint, data=None):

        if data is None:
            data = {}

        data["access_token"] = self.access_token

        r = requests.post(
            f"{GRAPH}/{endpoint}",
            data=data,
            timeout=120
        )

        r.raise_for_status()

        return r.json()
cipher = Fernet(
    Config.ENCRYPTION_KEY.encode()
)


def encrypt_token(token):

    return cipher.encrypt(
        token.encode()
    ).decode()


def decrypt_token(token):

    return cipher.decrypt(
        token.encode()
    ).decode()
  def get_me(access_token):

    r = requests.get(

        f"{GRAPH}/me",

        params={

            "fields":"id,name",

            "access_token":access_token

        },

        timeout=60

    )

    r.raise_for_status()

    return r.json()
    
def exchange_long_token(short_token):

    r = requests.get(

        f"{GRAPH}/oauth/access_token",

        params={

            "grant_type":"fb_exchange_token",

            "client_id":Config.APP_ID,

            "client_secret":Config.APP_SECRET,

            "fb_exchange_token":short_token

        },

        timeout=60

    )

    r.raise_for_status()

    return r.json()["access_token"]
  def get_pages(access_token):

    r = requests.get(

        f"{GRAPH}/me/accounts",

        params={

            "access_token":access_token

        },

        timeout=60

    )

    r.raise_for_status()

    return r.json().get("data",[])
  import os
import requests

GRAPH = "https://graph.facebook.com/v23.0"


class FacebookAPI:

    def __init__(self, access_token):

        self.access_token = access_token

    # ==========================
    # TEXT POST
    # ==========================

    def publish_text_post(
        self,
        page_id,
        message,
    ):

        r = requests.post(

            f"{GRAPH}/{page_id}/feed",

            data={

                "message": message,

                "access_token": self.access_token

            },

            timeout=120

        )

        r.raise_for_status()

        return r.json()


    # ==========================
    # PHOTO POST
    # ==========================

    def publish_photo_post(
        self,
        page_id,
        photo_path,
        caption=None,
    ):

        with open(photo_path, "rb") as photo:

            r = requests.post(

                f"{GRAPH}/{page_id}/photos",

                data={

                    "caption": caption or "",

                    "access_token": self.access_token

                },

                files={

                    "source": photo

                },

                timeout=300

            )

        r.raise_for_status()

        return r.json()


    # ==========================
    # VIDEO POST
    # ==========================

    def publish_video_post(
        self,
        page_id,
        video_path,
        description=None,
    ):

        with open(video_path, "rb") as video:

            r = requests.post(

                f"{GRAPH}/{page_id}/videos",

                data={

                    "description": description or "",

                    "access_token": self.access_token

                },

                files={

                    "source": video

                },

                timeout=900

            )

        r.raise_for_status()

        return r.json()


    # ==========================
    # DELETE POST
    # ==========================

    def delete_post(
        self,
        post_id,
    ):

        r = requests.delete(

            f"{GRAPH}/{post_id}",

            params={

                "access_token": self.access_token

            },

            timeout=120

        )

        r.raise_for_status()

        return r.json()


    # ==========================
    # PAGE INFO
    # ==========================

    def get_page_info(
        self,
        page_id,
    ):

        r = requests.get(

            f"{GRAPH}/{page_id}",

            params={

                "fields": "id,name,fan_count,category",

                "access_token": self.access_token

            },

            timeout=120

        )

        r.raise_for_status()

        return r.json()


    # ==========================
    # PAGE POSTS
    # ==========================

    def get_posts(
        self,
        page_id,
    ):

        r = requests.get(

            f"{GRAPH}/{page_id}/posts",

            params={

                "access_token": self.access_token

            },

            timeout=120

        )

        r.raise_for_status()

        return r.json()


    # ==========================
    # REMOVE PAGE
    # ==========================

    def remove_page(
        self,
        page_id,
    ):

        return True


    # ==========================
    # DISCONNECT ACCOUNT
    # ==========================

    def disconnect_account(self):

        return True
 import logging
import requests

from config import Config

logger = logging.getLogger(__name__)

GRAPH = "https://graph.facebook.com/v23.0"


class FacebookAPI:

    def __init__(self, access_token):

        self.access_token = access_token

    # ==========================
    # VALIDATE TOKEN
    # ==========================

    def validate_token(self):

        try:

            r = requests.get(

                f"{GRAPH}/me",

                params={

                    "fields": "id,name",

                    "access_token": self.access_token

                },

                timeout=60

            )

            return r.status_code == 200

        except Exception:

            return False


    # ==========================
    # COMMENT REPLY
    # ==========================

    def reply_comment(

        self,

        comment_id,

        message,

    ):

        r = requests.post(

            f"{GRAPH}/{comment_id}/comments",

            data={

                "message": message,

                "access_token": self.access_token

            },

            timeout=120

        )

        r.raise_for_status()

        return r.json()


    # ==========================
    # GET COMMENTS
    # ==========================

    def get_comments(

        self,

        post_id,

    ):

        r = requests.get(

            f"{GRAPH}/{post_id}/comments",

            params={

                "access_token": self.access_token

            },

            timeout=120

        )

        r.raise_for_status()

        return r.json()

# ==========================
# WEBHOOK VERIFY
# ==========================

def verify_webhook(

    mode,

    token,

    challenge,

):

    if (

        mode == "subscribe"

        and

        token == Config.WEBHOOK_VERIFY_TOKEN

    ):

        return challenge

    return None

# ==========================
# PARSE WEBHOOK
# ==========================

def parse_webhook(data):

    try:

        return data.get(

            "entry",

            []

        )

    except Exception as e:

        logger.exception(e)

        return []

# ==========================
# FACEBOOK ERROR
# ==========================

def log_error(error):

    logger.exception(error)

import time


def retry_request(

    func,

    retries=3,

):

    for _ in range(retries):

        try:

            return func()

        except Exception:

            time.sleep(2)

    raise Exception("Facebook request failed")

