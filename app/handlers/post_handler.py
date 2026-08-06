import pytz
import datetime
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from sqlalchemy.future import select
from app.database.session import AsyncSessionLocal
from app.models.all_models import User, FacebookPage, Post, PostType, PostStatus
from app.handlers.keyboards import get_home_keyboard, get_back_home_keyboard
from app.scheduler.publisher import execute_post_publish

SELECT_PAGE, SELECT_TYPE, ENTER_CONTENT, ENTER_MEDIA, ENTER_SCHEDULE = range(5)


async def start_create_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    telegram_id = update.effective_user.id

    async with AsyncSessionLocal() as db:
        user_res = await db.execute(select(User).filter(User.telegram_id == telegram_id))
        user = user_res.scalars().first()
        if not user:
            await query.edit_message_text("User record missing.", reply_markup=get_back_home_keyboard())
            return ConversationHandler.END

        pages_res = await db.execute(
            select(FacebookPage)
            .join(FacebookPage.account)
            .filter(FacebookPage.account.has(user_id=user.id))
        )
        pages = pages_res.scalars().all()

        if not pages:
            await query.edit_message_text(
                "❌ No connected Facebook pages found.\nPlease link a page in Settings first.",
                reply_markup=get_back_home_keyboard()
            )
            return ConversationHandler.END

        keyboard = [
            [InlineKeyboardButton(p.name, callback_data=f"select_page_{p.id}")] for p in pages
        ]
        keyboard.append([InlineKeyboardButton(" Cancel", callback_data="cancel_post")])

        await query.edit_message_text(
            "📝 **Create Post - Step 1/5**\nSelect target Facebook Page:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return SELECT_PAGE


async def page_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page_id = int(query.data.replace("select_page_", ""))
    context.user_data["post_page_id"] = page_id

    keyboard = [
        [InlineKeyboardButton("📝 Text Only", callback_data="type_TEXT")],
        [InlineKeyboardButton("🖼 Photo", callback_data="type_PHOTO")],
        [InlineKeyboardButton("🎥 Video", callback_data="type_VIDEO")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_post")]
    ]

    await query.edit_message_text(
        "📝 **Create Post - Step 2/5**\nSelect Post Type:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return SELECT_TYPE


async def type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    post_type = query.data.replace("type_", "")
    context.user_data["post_type"] = post_type

    await query.edit_message_text(
        "📝 **Create Post - Step 3/5**\nPlease reply with the text caption/message for your post:"
    )
    return ENTER_CONTENT


async def content_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["post_message"] = update.message.text
    post_type = context.user_data["post_type"]

    if post_type in ["PHOTO", "VIDEO"]:
        await update.message.reply_text(
            f"📝 **Create Post - Step 4/5**\nPlease send a public direct URL for your {post_type.lower()}:"
        )
        return ENTER_MEDIA
    else:
        context.user_data["post_media_url"] = None
        return await ask_schedule(update, context)


async def media_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["post_media_url"] = update.message.text.strip()
    return await ask_schedule(update, context)


async def ask_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚡ Publish Now", callback_data="sched_NOW")],
        [InlineKeyboardButton("⏰ Schedule for Later", callback_data="sched_LATER")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_post")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    msg = "📝 **Create Post - Step 5/5**\nWhen would you like to publish this post?"

    if update.callback_query:
        await update.callback_query.edit_message_text(msg, parse_mode="Markdown", reply_markup=markup)
    else:
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=markup)
    return ENTER_SCHEDULE


async def schedule_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data

    if choice == "sched_NOW":
        return await finalize_post(update, context, publish_now=True)
    elif choice == "sched_LATER":
        await query.edit_message_text(
            "⏰ Enter schedule date/time in format: `YYYY-MM-DD HH:MM`\nExample: `2026-08-10 15:30`",
            parse_mode="Markdown"
        )
        return ENTER_SCHEDULE


async def schedule_time_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time_str = update.message.text.strip()
    telegram_id = update.effective_user.id

    async with AsyncSessionLocal() as db:
        user_res = await db.execute(select(User).filter(User.telegram_id == telegram_id))
        user = user_res.scalars().first()
        tz_str = user.timezone if user else "UTC"

    try:
        user_tz = pytz.timezone(tz_str)
        naive_dt = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        local_dt = user_tz.localize(naive_dt)
        utc_dt = local_dt.astimezone(pytz.UTC).replace(tzinfo=None)

        context.user_data["scheduled_at_utc"] = utc_dt
        return await finalize_post(update, context, publish_now=False)
    except Exception:
        await update.message.reply_text("❌ Invalid format. Please use `YYYY-MM-DD HH:MM`:")
        return ENTER_SCHEDULE


async def finalize_post(update: Update, context: ContextTypes.DEFAULT_TYPE, publish_now: bool):
    telegram_id = update.effective_user.id
    data = context.user_data

    async with AsyncSessionLocal() as db:
        user_res = await db.execute(select(User).filter(User.telegram_id == telegram_id))
        user = user_res.scalars().first()

        new_post = Post(
            user_id=user.id,
            facebook_page_id=data["post_page_id"],
            post_type=PostType[data["post_type"]],
            message=data.get("post_message"),
            media_url=data.get("post_media_url"),
            status=PostStatus.DRAFT if not publish_now else PostStatus.SCHEDULED,
            scheduled_at=datetime.datetime.utcnow() if publish_now else data.get("scheduled_at_utc")
        )
        db.add(new_post)
        await db.commit()
        await db.refresh(new_post)

        if publish_now:
            success = await execute_post_publish(db, new_post)
            msg = "✅ **Post published successfully!**" if success else "❌ **Failed to publish post.** Check Facebook permissions."
        else:
            new_post.status = PostStatus.SCHEDULED
            await db.commit()
            msg = f"⏰ **Post successfully scheduled** for `{data.get('scheduled_at_utc')} UTC`!"

    if update.callback_query:
        await update.callback_query.edit_message_text(msg, parse_mode="Markdown", reply_markup=get_back_home_keyboard())
    else:
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_back_home_keyboard())

    context.user_data.clear()
    return ConversationHandler.END


async def cancel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text("❌ Post creation canceled.", reply_markup=get_back_home_keyboard())
    context.user_data.clear()
    return ConversationHandler.END


post_conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_create_post, pattern="^menu_create_post$")],
    states={
        SELECT_PAGE: [CallbackQueryHandler(page_selected, pattern="^select_page_")],
        SELECT_TYPE: [CallbackQueryHandler(type_selected, pattern="^type_")],
        ENTER_CONTENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, content_entered)],
        ENTER_MEDIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, media_entered)],
        ENTER_SCHEDULE: [
            CallbackQueryHandler(schedule_decision, pattern="^sched_"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, schedule_time_entered)
        ]
    },
    fallbacks=[CallbackQueryHandler(cancel_post, pattern="^cancel_post$")]
)
