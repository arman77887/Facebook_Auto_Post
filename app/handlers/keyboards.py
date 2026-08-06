from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_home_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("📝 Create Post", callback_data="menu_create_post"),
            InlineKeyboardButton("📅 Scheduled Posts", callback_data="menu_scheduled_posts")
        ],
        [
            InlineKeyboardButton("📄 My Pages", callback_data="menu_pages"),
            InlineKeyboardButton("👤 Profile", callback_data="menu_profile")
        ],
        [
            InlineKeyboardButton("💬 Auto Reply", callback_data="menu_auto_reply"),
            InlineKeyboardButton("🌍 Timezone", callback_data="menu_timezone")
        ],
        [
            InlineKeyboardButton("🤖 AI Support", callback_data="menu_ai_support"),
            InlineKeyboardButton("🎧 Live Support", callback_data="menu_live_support")
        ],
        [
            InlineKeyboardButton("💎 Premium", callback_data="menu_premium"),
            InlineKeyboardButton("⚙ Settings", callback_data="menu_settings")
        ]
    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton("👑 Admin Panel", callback_data="menu_admin")])

    return InlineKeyboardMarkup(keyboard)


def get_settings_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("🔗 Connect Facebook", callback_data="connect_facebook"),
            InlineKeyboardButton("❌ Disconnect Facebook", callback_data="disconnect_facebook")
        ],
        [
            InlineKeyboardButton("➕ Add Page", callback_data="add_page"),
            InlineKeyboardButton("🗑 Remove Page", callback_data="remove_page")
        ],
        [
            InlineKeyboardButton("🔄 Refresh Pages", callback_data="refresh_pages")
        ],
        [
            InlineKeyboardButton("🏠 Main Menu", callback_data="menu_home")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_post_type_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("📝 Text Only", callback_data="post_type_TEXT"),
            InlineKeyboardButton("🖼 Photo Post", callback_data="post_type_PHOTO")
        ],
        [
            InlineKeyboardButton("🎥 Video Post", callback_data="post_type_VIDEO")
        ],
        [
            InlineKeyboardButton("🏠 Cancel & Return Home", callback_data="menu_home")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_home_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Main Menu", callback_data="menu_home")]
    ])
