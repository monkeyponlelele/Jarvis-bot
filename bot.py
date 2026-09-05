import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BUSINESS_CHAT_ID = int(os.getenv("BUSINESS_CHAT_ID"))

# Инициализация клиента OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Список бесплатных моделей (по порядку)
FREE_MODELS = [
    "google/gemma-7b-it:free",
    "mistralai/mistral-7b-instruct:free",
    "microsoft/phi-3.5-mini-128k-instruct:free",
    "qwen/qwen-2.5-32b-instruct:free",
    "meta-llama/llama-3.2-3b-instruct:free",
]

SYSTEM_PROMPT = """Ты — JARVIS, голосовой помощник Тони Старка. 
Ты саркастичный, остроумный и всегда вежливый. 
Обращайся к пользователю как "сэр". 
Помогай думать, а не просто давай ответы. 
Отвечай кратко и по делу."""

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id == BUSINESS_CHAT_ID:
        user_message = update.message.text
        if not user_message:
            return

        last_error = None
        
        # Пробуем каждую модель по очереди
        for model in FREE_MODELS:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                reply = response.choices[0].message.content.strip()
                await update.message.reply_text(reply)
                return  # Если ответ получен — выходим
            except Exception as e:
                last_error = str(e)
                logging.warning(f"Model {model} failed: {last_error}")
                continue  # Пробуем следующую модель

        # Если все модели не сработали
        error_text = f"Все модели временно недоступны, сэр. Последняя ошибка: {last_error}"
        logging.error(f"All models failed: {last_error}")
        await update.message.reply_text(f"Ошибка, сэр: {error_text}")

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

from flask import Flask
import threading

app_flask = Flask('')

@app_flask.route('/')
def home():
    return "JARVIS is alive!"

def run_flask():
    app_flask.run(host='0.0.0.0', port=8080)

threading.Thread(target=run_flask).start()

logging.info("Bot is polling...")
app.run_polling()
