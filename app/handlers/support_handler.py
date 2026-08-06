from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from sqlalchemy.future import select
from app.database.session import AsyncSessionLocal
from app.models.all_models import User, SupportTicket, TicketStatus
from app.services.openai_service import OpenAIService
from app.handlers.keyboards import get_back_home_keyboard

WAIT_SUPPORT_QUERY = 1


async def start_ai_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🤖 **AI Support Agent**\nHow can I help you today? Reply with your inquiry:")
    return WAIT_SUPPORT_QUERY


async def process_support_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    tg_id = update.effective_user.id

    ai_response = await OpenAIService.answer_support_query(user_msg)

    if "CANNOT_ANSWER" in ai_response or len(ai_response.strip()) == 0:
        async with AsyncSessionLocal() as db:
            user_res = await db.execute(select(User).filter(User.telegram_id == tg_id))
            user = user_res.scalars().first()

            ticket = SupportTicket(
                user_id=user.id,
                subject=f"Auto Ticket from query: {user_msg[:30]}...",
                description=user_msg,
                status=TicketStatus.OPEN
            )
            db.add(ticket)
            await db.commit()

        await update.message.reply_text(
            "🎧 I couldn't fully process your inquiry. "
            "A **Live Support Ticket** has been automatically created for you. An admin will follow up shortly!",
            reply_markup=get_back_home_keyboard()
        )
    else:
        await update.message.reply_text(
            f"🤖 **AI Response:**\n\n{ai_response}",
            reply_markup=get_back_home_keyboard()
        )

    return ConversationHandler.END


support_conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_ai_support, pattern="^menu_ai_support$")],
    states={
        WAIT_SUPPORT_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_support_query)]
    },
    fallbacks=[CallbackQueryHandler(start_ai_support, pattern="^menu_home$")]
)
