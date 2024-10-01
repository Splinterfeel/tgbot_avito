import os
from telegram import ReplyKeyboardRemove, Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, CommandHandler, ConversationHandler, filters
from avito_lib import AvitoAPIClient
import db


CHOOSE_ACTION, ENTERING_KEY = range(2)

temp_client_id = None
temp_client_secret = None

api_token = os.getenv('TGBOT_TOKEN')
if not api_token:
    raise ValueError("No API token in TGBOT_TOKEN!")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply_keyboard = [["Указать CLIENT_ID и CLIENT_SECRET", "Запустить парсинг"]]
    await update.message.reply_text(
        "Выберите действие\n\n",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Действие"
        ),
    )
    return CHOOSE_ACTION


async def start_parsing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_data = db.get_client_info(update.message.chat.username)
    if not user_data:
        await update.message.reply_text('Укажите client_id и client_secret через пробел')
        return ENTERING_KEY
    api_client: AvitoAPIClient = AvitoAPIClient(user_data['client_id'], user_data['client_secret'])
    await api_client.auth()
    await api_client.get_advertisments()
    await api_client.gather_advertisments_stats()
    report = api_client.form_report_file()
    await context.bot.send_document(update.message.chat_id, report, 'Отчет', filename='report.xlsx')
    return ConversationHandler.END


async def enter_keys(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Укажите через пробел client_id и client_secret из ЛК Авито")
    return ENTERING_KEY


async def entered_keys(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg_splitted = update.message.text.split()
    if not len(msg_splitted) == 2:
        await update.message.reply_text('Ошибка чтения. Ожидается 2 значения через пробел. Попробуйте снова')
        return ENTERING_KEY
    client_id = msg_splitted[0]
    client_secret = msg_splitted[1]
    db.add_client_info(update.message.chat.username, client_id, client_secret)
    await update.message.reply_text("Ключ принят")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Пока!", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


if __name__ == '__main__':
    db.init()
    app = ApplicationBuilder().token(api_token).build()
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(None, start),
        ],
        states={
            CHOOSE_ACTION: [
                MessageHandler(filters.Regex("Указать CLIENT_ID и CLIENT_SECRET"), enter_keys),
                MessageHandler(filters.Regex("Запустить парсинг"), start_parsing),
                MessageHandler(None, start),
            ],
            ENTERING_KEY: [MessageHandler(None, entered_keys)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv_handler)
    app.run_polling()
