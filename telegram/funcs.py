import psycopg2
from contextlib import closing
import uuid

from telegram_db import DB_NAME, USERNAME, DB_PASS, DB_HOST


def check_authorization(chat_id: int):
    with closing(psycopg2.connect(dbname=DB_NAME, user=USERNAME,
                                  password=DB_PASS, host=DB_HOST)) as conn:
        with conn.cursor() as cursor:
            cursor.execute(f'SELECT * FROM telegram_authorizations WHERE chat_id = {chat_id}')
            auth = cursor.fetchone()
            return auth is not None


def register_user(chat_id: int):
    with closing(psycopg2.connect(dbname=DB_NAME, user=USERNAME,
                                  password=DB_PASS, host=DB_HOST)) as conn:
        with conn.cursor() as cursor:
            db_uuid = 11
            cursor.execute(f'INSERT INTO telegram_authorizations (id, chat_id) VALUES ({db_uuid}, {chat_id})')
            conn.commit()
            return True
