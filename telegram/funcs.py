import psycopg2
from contextlib import closing

import requests
from passlib.context import CryptContext

from config import DIARY_URL
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
            cursor.execute(f'INSERT INTO telegram_authorizations (chat_id) VALUES ({chat_id})')
            conn.commit()
            return True


def check_login(login: str, password: str, usertype: str):
    headers = {
        'accept': 'application/json',
    }

    data = {
        'username': login,
        'password': password,
        'client_id': usertype,
    }

    return requests.post(f'{DIARY_URL}/token', headers=headers, data=data)


def find_student(login: str, password: str):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    with closing(psycopg2.connect(dbname=DB_NAME, user=USERNAME,
                                  password=DB_PASS, host=DB_HOST)) as conn:
        with conn.cursor() as cursor:
            cursor.execute(f'SELECT * FROM users WHERE login = %s', (login,))
            user = cursor.fetchone()
            if user is None:
                return False
            elif not pwd_context.verify(password, user[2]):
                return False
    return user[3]


def link_student(diary_id, chat_id):
    with closing(psycopg2.connect(dbname=DB_NAME, user=USERNAME,
                                  password=DB_PASS, host=DB_HOST)) as conn:
        with conn.cursor() as cursor:
            cursor.execute(f'update users set telegram_chat_id = %s where diary_id = %s', (chat_id, diary_id))
            conn.commit()
    return True
