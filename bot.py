import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")
BUSINESS_CHAT_ID = int(os.getenv("BUSINESS_CHAT_ID"))

# Модель для диалогов (бесплатная и хорошая)
MODEL = "microsoft/DialoGPT-medium"

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
            # Запрос к Hugging Face API
            headers = {"Authorization": f"Bearer {HF_API_KEY}"}
            payload = {
                "inputs": f"{SYSTEM_PROMPT}\n\nUser: {user_message}\nJARVIS:",
                "parameters": {"max_new_tokens": 150}
            }
            
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{MODEL}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # У разных моделей разный формат ответа
                if isinstance(result, list) and len(result) > 0:
                    reply = result[0].get("generated_text", "Ошибка, сэр.").strip()
                else:
                    reply = str(result)
            else:
                reply = f"Ошибка API: {response.status_code} - {response.text}"

        except Exception as e:
            error_text = str(e)
            logging.error(f"Hugging Face error: {error_text}")
            reply = f"Ошибка, сэр: {error_text}"

        await update.message.reply_text(reply)

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
