from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from app.config import settings
from app.handlers.bot_menu import start_command, menu_callback_handler
from app.handlers.post_handler import post_conversation_handler
from app.handlers.support_handler import support_conversation_handler
from app.handlers.admin_handler import admin_menu_callback


def build_telegram_application() -> Application:
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(post_conversation_handler)
    app.add_handler(support_conversation_handler)
    app.add_handler(CallbackQueryHandler(admin_menu_callback, pattern="^menu_admin$"))
    app.add_handler(CallbackQueryHandler(menu_callback_handler))

    return app
