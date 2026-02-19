import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import google.generativeai as genai
import os
import signal
import sys

# ===== ТВОИ ДАННЫЕ =====
# Токен теперь берётся из переменных окружения (это безопасно для сервера)
TELEGRAM_TOKEN = os.environ.get('7649686053:AAF0thTEPVcR510PYeL8wG_UpGAHV50rjng')
GEMINI_API_KEY = os.environ.get('AIzaSyAoz_ILK1t9rZT9C4ciObCADkERmxG8fsM')
# ========================

# Проверка, что ключи загружены
if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    print("Ошибка: Не установлены переменные окружения TELEGRAM_TOKEN или GEMINI_API_KEY")
    sys.exit(1)

# Настраиваем Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Обработчик сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        response = model.generate_content(user_message)
        bot_reply = response.text
    except Exception as e:
        bot_reply = f"Ошибка: {e}"
    await update.message.reply_text(bot_reply)

def main():
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Обработка сигнала остановки, чтобы бот выключился gracefully
    def signal_handler(sig, frame):
        print("Остановка бота...")
        application.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("Бот запущен и готов к работе!")
    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()