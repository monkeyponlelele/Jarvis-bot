import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
BUSINESS_CHAT_ID = int(os.getenv("BUSINESS_CHAT_ID"))

# Клиент Cerebras (полностью совместим с OpenAI)
client = OpenAI(
    api_key=CEREBRAS_API_KEY,
    base_url="https://api.cerebras.ai/v1",
)

SYSTEM_PROMPT = """Ты — JARVIS, голосовой помощник Тони Старка. 
Ты саркастичный, остроумный и всегда вежливый. 
Обращайся к пользователю как "сэр". 
Отвечай кратко и по делу."""

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id == BUSINESS_CHAT_ID:
        user_message = update.message.text
        if not user_message:
            return

        try:
            response = client.chat.completions.create(
                model="gpt-oss-120b",  # Бесплатная мощная модель Cerebras
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            reply = response.choices[0].message.content.strip()
            await update.message.reply_text(reply)
        except Exception as e:
            error_text = str(e)
            logging.error(f"Cerebras error: {error_text}")
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
