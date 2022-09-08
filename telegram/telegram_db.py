from dotenv import load_dotenv
import os

load_dotenv()

DB_NAME = os.getenv('DB')
USERNAME = os.getenv('USERNAME')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
