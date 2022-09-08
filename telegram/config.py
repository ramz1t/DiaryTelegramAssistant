from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv('TELEGRAM_BOT_KEY')
DIARY_URL = 'http://127.0.0.1:8000'
