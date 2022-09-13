from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv('TELEGRAM_BOT_KEY')
