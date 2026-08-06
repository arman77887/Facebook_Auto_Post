import pytz
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from sqlalchemy.future import select
from app.database.session import AsyncSessionLocal
from app.models.all_models import User, FacebookPage, Post, PostStatus, SupportTicket, TicketStatus
from app.services.user_service import UserService
from app.handlers.keyboards import get_home_keyboard, get_settings_keyboard, get_back_home_keyboard
from app.config import settings


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_user = update.effective_user
    async with AsyncSessionLocal() as db:
        user = await UserService.get_or_create_user(
            db,
            telegram_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name
        )
        is_admin = user.is_admin

    welcome_text = (
        f"👋 **Welcome to {settings.APP_NAME}!**\n\n"
        "Manage your Facebook Pages, schedule rich posts, auto-reply to comments, "
        "and leverage AI automation seamlessly.\n\n"
        "Select an option below to proceed:"
    )

    if update.message:
        await update.message.reply_text(
            welcome_text,
            parse_mode="Markdown",
            reply_markup=get_home_keyboard(is_admin)
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            welcome_text,
            parse_mode="Markdown",
            reply_markup=get_home_keyboard(is_admin)
        )


async def menu_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    tg_user = update.effective_user

    async with AsyncSessionLocal() as db:
        user_res = await db.execute(select(User).filter(User.telegram_id == tg_user.id))
        user = user_res.scalars().first()

        if data == "menu_home":
            await start_command(update, context)

        elif data == "menu_settings":
            msg = "⚙ **Settings & Facebook Management**\nChoose an action below:"
            await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=get_settings_keyboard())

        elif data == "menu_profile":
            msg = (
                "👤 **User Profile**\n\n"
                f"• **Telegram ID:** `{user.telegram_id}`\n"
                f"• **Name:** {user.first_name or ''} {user.last_name or ''}\n"
                f"• **Timezone:** `{user.timezone}`\n"
                f"• **Admin:** {'Yes' if user.is_admin else 'No'}"
            )
            await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=get_back_home_keyboard())

        elif data == "menu_pages":
            pages_res = await db.execute(
                select(FacebookPage)
                .join(FacebookPage.account)
                .filter(FacebookPage.account.has(user_id=user.id))
            )
            pages = pages_res.scalars().all()
            if not pages:
                text = "📄 **Connected Pages**\n\nNo pages connected yet."
            else:
                text = "📄 **Connected Pages:**\n\n"
                for p in pages:
                    text += f"• **{p.name}** (ID: `{p.page_id}`)\n  Auto Reply: {'✅' if p.auto_reply_enabled else '❌'}\n"
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_home_keyboard())

        elif data == "menu_scheduled_posts":
            posts_res = await db.execute(
                select(Post)
                .filter(Post.user_id == user.id, Post.status == PostStatus.SCHEDULED)
            )
            posts = posts_res.scalars().all()
            if not posts:
                text = "📅 **Scheduled Posts**\n\nNo pending posts scheduled."
            else:
                text = "📅 **Scheduled Posts:**\n\n"
                for p in posts:
                    text += f"• `{p.post_type.value}` | Scheduled: `{p.scheduled_at}` UTC\n"
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_home_keyboard())

        elif data == "connect_facebook":
            login_url = f"{settings.BASE_URL}/auth/facebook/login?telegram_id={user.telegram_id}"
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("🌐 Login via Facebook", url=login_url)],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="menu_home")]
            ])
            await query.edit_message_text(
                "🔗 Click the button below to authorize Facebook access:",
                reply_markup=kb
            )

        elif data == "menu_timezone":
            common_tzs = ["UTC", "America/New_York", "Europe/London", "Asia/Dubai", "Asia/Singapore", "Australia/Sydney"]
            kb = [[InlineKeyboardButton(tz, callback_data=f"set_tz_{tz}")] for tz in common_tzs]
            kb.append([InlineKeyboardButton("🏠 Main Menu", callback_data="menu_home")])
            await query.edit_message_text("🌍 **Select your local timezone:**", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

        elif data.startswith("set_tz_"):
            new_tz = data.replace("set_tz_", "")
            await UserService.update_timezone(db, user.id, new_tz)
            await query.edit_message_text(f"✅ Timezone updated to `{new_tz}`", parse_mode="Markdown", reply_markup=get_back_home_keyboard())
