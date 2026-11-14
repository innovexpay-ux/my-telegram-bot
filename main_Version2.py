import logging
import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 3800


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(
            "Send me a text message and I’ll submit it anonymously to the group."
        )


async def submit_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    message = update.message
    if not message or not message.text:
        return

    if len(message.text) > MAX_MESSAGE_LENGTH:
        await message.reply_text(
            f"That message is too long. Please keep it under "
            f"{MAX_MESSAGE_LENGTH} characters."
        )
        return

    group_id = context.application.bot_data["group_id"]
    await context.bot.send_message(
        chat_id=group_id,
        text=f"📩 Anonymous message:\n\n{message.text}",
    )
    await message.reply_text("Your message was submitted.")


def main() -> None:
    token = os.environ.get("BOT_TOKEN")
    group_id = os.environ.get("GROUP_ID")

    if not token or not group_id:
        raise RuntimeError("Set both BOT_TOKEN and GROUP_ID environment variables.")

    application = Application.builder().token(token).build()
    application.bot_data["group_id"] = group_id

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, submit_message)
    )

    logger.info("Starting bot")
    application.run_polling()


if __name__ == "__main__":
    main()