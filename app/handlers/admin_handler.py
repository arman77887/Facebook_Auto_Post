from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.future import select
from app.database.session import AsyncSessionLocal
from app.models.all_models import User, Post, SupportTicket, TicketStatus
from app.handlers.keyboards import get_back_home_keyboard
from app.config import settings


async def admin_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != settings.ADMIN_TELEGRAM_ID:
        await query.edit_message_text("❌ Unauthorized access.", reply_markup=get_back_home_keyboard())
        return

    async with AsyncSessionLocal() as db:
        users_count = len((await db.execute(select(User))).scalars().all())
        posts_count = len((await db.execute(select(Post))).scalars().all())
        open_tickets = len((await db.execute(select(SupportTicket).filter(SupportTicket.status == TicketStatus.OPEN))).scalars().all())

    msg = (
        "👑 **Admin Dashboard**\n\n"
        f"👥 Total Users: `{users_count}`\n"
        f"📝 Total Posts Processed: `{posts_count}`\n"
        f"🎧 Open Support Tickets: `{open_tickets}`\n\n"
        "Send command `/broadcast <message>` to notify all users."
    )
    await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=get_back_home_keyboard())
