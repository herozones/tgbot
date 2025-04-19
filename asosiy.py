from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext
import logging
import os

ADMIN_ID = 6746664012
TOKEN = '7768722784:AAFlo8fqLqYOek5iTxMqcFJrQjoKH7zAWIQ'
CARD_NUMBER = '8600 1234 5678 9012'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("To'lov qilish", callback_data='payment')],
        [InlineKeyboardButton("Mening balansim", callback_data='balance')],
        [InlineKeyboardButton("Transaksiyalar tarixi", callback_data='history')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Salom! To\'lov botiga xush kelibsiz. Iltimos, menyudan birini tanlang.', reply_markup=reply_markup)

async def handle_button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    if query.data == 'payment':
        await query.edit_message_text('Iltimos, to\'lov miqdorini kiriting.')

async def handle_payment(update: Update, context: CallbackContext):
    user_message = update.message.text
    user_id = update.message.from_user.id

    await context.bot.send_message(
        ADMIN_ID,
        f"Yangi to'lov so'rovi:\nFoydalanuvchi: {update.message.from_user.full_name} ({user_id})\nMiqdor: {user_message}"
    )

    await update.message.reply_text(
        f"To'lov miqdori: {user_message} so'm.\n\n"
        "Iltimos, quyidagi karta raqamiga to'lovni amalga oshiring:\n\n"
        f"*{CARD_NUMBER}*\n\n"
        "To'lovni amalga oshirgach, iltimos, chek (skrinshot) ni yuboring.",
        parse_mode='Markdown'
    )

async def handle_card_and_receipt(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        os.makedirs("downloads", exist_ok=True)
        file_path = f"downloads/{photo_file.file_id}.jpg"
        await photo_file.download_to_drive(file_path)

        await context.bot.send_message(
            ADMIN_ID,
            f"To'lov skrinsoti:\nFoydalanuvchi: {update.message.from_user.full_name} ({user_id})"
        )
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=open(file_path, 'rb'))
    else:
        text = update.message.text
        await context.bot.send_message(
            ADMIN_ID,
            f"Karta ma'lumoti:\nFoydalanuvchi: {update.message.from_user.full_name} ({user_id})\nMatn: {text}"
        )

    await update.message.reply_text('Malumot yuborildi. Admin tomonidan ko‘rib chiqiladi.')

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_payment))
    app.add_handler(MessageHandler(filters.PHOTO, handle_card_and_receipt))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_card_and_receipt))
    app.run_polling()

if __name__ == '__main__':
    main()
