import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from pb import decrypt_pb_file
from nm import decrypt_nm_file
from tnl import decrypt_tnl_file
from sks import decrypt_sks_file
from ziv import decrypt_ziv_file
import os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_USERS_FILE = 'allowuser.txt'

def load_allowed_users():
    allowed_users = set()
    if os.path.exists(ALLOWED_USERS_FILE):
        with open(ALLOWED_USERS_FILE, 'r') as f:
            allowed_users = set(line.strip() for line in f)
    return allowed_users

async def start_help_handler(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = str(user.id)
    user_name = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name

    allowed_users = load_allowed_users()
    status = "allowed" if user_id in allowed_users else "not allowed"
    
    logger.info(f"{user_name} - User ID: {user_id} - Command: /start - Status: {status}")

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Copy ID", callback_data=f"copy_id_{user_id}")]])
    help_message = (
        f"Hi {user_name}! Let's get you started:\n\n"

        "**Your Info**\n"
        f"* User ID: {user_id}\n"
        f"* Status: {status}\n\n"

        "**Compatible Files**\n"
        "* .nm (NetMod Syna)\n"
        "* .tnl (OpenTunnel)\n"
        "* .ziv (Zivpn Tunnel)\n"
        "* .pb (PB Tunnel)\n"
        "* .sks (SocksHTTP)\n\n"

        "**Important**\n"
        "Remember, only authorized users can use this bot. You'll get a confirmation if your ID is approved.\n\n"

        "**Available Commands**\n"
        "/check_status - Check if your ID is allowed or not"
    )
    await context.bot.send_message(chat_id=update.message.chat_id, text=help_message, reply_markup=keyboard)

async def check_status(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = str(user.id)
    user_name = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name

    allowed_users = load_allowed_users()
    status = "allowed" if user_id in allowed_users else "not allowed"
    
    logger.info(f"{user_name} - User ID: {user_id} - Command: /check_status - Status: {status}")

    status_message = f"Your user ID ({user_id}) is {status}."
    await context.bot.send_message(chat_id=update.message.chat_id, text=status_message)

async def document_handler(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = str(user.id)
    user_name = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name

    logger.info(f"{user_name} - User ID: {user_id} - Command: Document upload")

    allowed_users = load_allowed_users()
    if user_id not in allowed_users:
        message = f"Sorry, {user_name}, your ID ({user_id}) is not allowed. Please contact the admin."
        await context.bot.send_message(chat_id=update.message.chat_id, text=message)
        return

    document = update.message.document
    if document:
        file_name = document.file_name
        file_extension = file_name.split('.')[-1] if '.' in file_name else 'unknown'

        if file_extension not in ['nm', 'tnl', 'sks', 'ziv', 'pb']:
            logger.info(f"{user_name} - Unsupported file type: {file_extension}")
            await context.bot.send_message(chat_id=update.message.chat_id, text=f"Sorry, {user_name}, unsupported file type: {file_extension}")
            return

        file = await context.bot.get_file(document.file_id)
        file_content = await file.download_as_bytearray()
        if file_extension == 'nm':
            decrypted_content = decrypt_nm_file(file_content)
        elif file_extension == 'tnl':
            decrypted_content = decrypt_tnl_file(file_content)
        elif file_extension == 'ziv':
            decrypted_content = decrypt_ziv_file(file_content)
        elif file_extension == 'sks':
            decrypted_content = decrypt_sks_file(file_content)
        elif file_extension == 'pb':
            decrypted_content = decrypt_pb_file(file_content)            

        if decrypted_content:
            await context.bot.send_message(chat_id=update.message.chat_id, text=decrypted_content, reply_to_message_id=update.message.message_id)
            logger.info(f"{user_name} - {file_extension} Decrypted content sent successfully.")
        else:
            await context.bot.send_message(chat_id=update.message.chat_id, text="Decryption failed.", reply_to_message_id=update.message.message_id)
            logger.error(f"{user_name} - Failed to decrypt {file_extension} file.")

async def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.data.split("_")[-1]
    context.bot.send_message(chat_id=query.message.chat_id, text=f"Your User ID ({user_id}) has been copied successfully.")

def main():
    token = "6100263145:AAHp0wupqPLVPCJxx4p8qlmgPo8aqbkH4gc"
    app = ApplicationBuilder().token(token).build()
    
    app.add_handler(CommandHandler("start", start_help_handler))
    app.add_handler(CommandHandler("help", start_help_handler))
    app.add_handler(CommandHandler("check_status", check_status))
    app.add_handler(MessageHandler(filters.Document.ALL, document_handler))
    app.add_handler(CallbackQueryHandler(button_callback, pattern=r"^copy_id_\d+$"))

    logger.info("Bot is running now!")

    app.run_polling()

if __name__ == '__main__':
    main()
