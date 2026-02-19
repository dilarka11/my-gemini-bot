import asyncio
from aiohttp import web
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import google.generativeai as genai
import os
import signal
import sys

# Токены из переменных окружения (их мы зададим на Render)
TELEGRAM_TOKEN = os.environ.get('7649686053:AAF0thTEPVcR510PYeL8wG_UpGAHV50rjng')
GEMINI_API_KEY = os.environ.get('AIzaSyAoz_ILK1t9rZT9C4ciObCADkERmxG8fsM')
PORT = int(os.environ.get('PORT', 10000))  # Render сам даст порт

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    print("Ошибка: Не установлены переменные окружения TELEGRAM_TOKEN или GEMINI_API_KEY")
    sys.exit(1)

# Настраиваем Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Обработчик сообщений Telegram (точно такой же, как был)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        response = model.generate_content(user_message)
        bot_reply = response.text
    except Exception as e:
        bot_reply = f"Ошибка: {e}"
    await update.message.reply_text(bot_reply)

# HTTP обработчик – он просто отвечает "Bot is running"
async def handle_http(request):
    return web.Response(text="Bot is running")

async def main():
    # Запускаем Telegram бота
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем HTTP сервер, который будет слушать порт (нужен для Render)
    app_web = web.Application()
    app_web.router.add_get('/', handle_http)
    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"HTTP server started on port {PORT}")

    # Запускаем бота (polling)
    print("Бот запущен и готов к работе!")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())