import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Получаем токены из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BUSINESS_CHAT_ID = int(os.getenv("BUSINESS_CHAT_ID"))

# Настройка Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# Системный промпт JARVIS (можно вставить любой)
SYSTEM_PROMPT = """Ты — JARVIS, голосовой помощник манки пона. Ты саркастичный, остроумный и всегда вежливый. Обращайся к пользователю как "сэр". Помогай думать, а не просто давай ответы. Отвечай кратко и по делу."""

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверяем, что сообщение от бизнес-чата
    if update.message.chat_id == BUSINESS_CHAT_ID:
        user_message = update.message.text
        if not user_message:
            return
        
        # Добавляем системный промпт
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_message}\nJARVIS:"
        
        # Отправляем запрос в Gemini
        try:
            response = model.generate_content(full_prompt)
            reply = response.text.strip()
        except Exception as e:
            logging.error(f"Gemini error: {e}")
            reply = "Произошла ошибка, сэр. Попробуйте еще раз."
        
        # Отправляем ответ
        await update.message.reply_text(reply)

def main():
    # Создаем приложение
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчик всех текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    logging.info("Bot is polling...")
    app.run_polling()

if __name__ == "__main__":
    main()