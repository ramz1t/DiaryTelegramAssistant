import os

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.utils.executor import start_webhook

from config import BOT_TOKEN
from funcs import check_authorization, register_user, check_login, find_student, link_student
from keyboards import kb_base, login_kb, creation_kb, connect_kb, try_again_kb

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)


class FSMLogin(StatesGroup):
    not_login = State()
    login = State()
    password = State()


class FSMStudentLogin(StatesGroup):
    not_login = State()
    student_login = State()
    student_password = State()


async def start(_):
    print('Bot is online')


@dp.message_handler(commands=['start'])
async def greet_new_user(message: types.Message):
    await FSMStudentLogin.not_login.set()
    # path = os.getcwd() + '/static/hello.webp'
    # sticker = open(path, 'rb')
    # await bot.send_sticker(chat_id=message.chat.id, sticker=sticker)
    await message.reply(f'Hello <b>{message.from_user.username}</b>!\n'
                        f'This bot is made for <b>Diary</b> web application, please choose your problem',
                        parse_mode='html', reply_markup=kb_base)


@dp.message_handler(content_types=['text'], state=FSMStudentLogin.not_login)
async def base_handler(message: types.Message):
    chat_id = message.chat.id
    if message.text == 'Admin panel':
        await message.reply('Checking authorization')
        if not check_authorization(chat_id=chat_id):
            await message.answer('Access denied, no authorization to admin account\n'
                                 'Want to login?', reply_markup=login_kb)
        else:
            await message.reply('Choose model to create', reply_markup=creation_kb)
    elif message.text == 'Connect for notifications':
        await message.reply(f'If you want to connect your Diary account to this Telegram, click *proceed*',
                            parse_mode='markdown', reply_markup=connect_kb)
    else:
        await message.reply('Unknown command')


@dp.callback_query_handler(state=FSMStudentLogin.not_login)
async def answer_callback(call: types.CallbackQuery):
    if call.data == 'login_yes':
        await call.message.answer('Login:')
        await FSMLogin.login.set()
    elif call.data == 'login_no':
        await call.message.answer('Choose option', reply_markup=kb_base)
    elif call.data == 'create_school':
        await call.message.answer('creating school, TBD')
        await call.message.delete_reply_markup()
    elif call.data == 'create_admin':
        await call.message.answer('creating admin, TBD')
        await call.message.delete_reply_markup()
    elif call.data == 'proceed':
        await call.message.answer('Login:')
        await FSMStudentLogin.student_login.set()
    elif call.data == 'no':
        await call.message.answer('Thank you for using DiaryBot')


@dp.message_handler(content_types=['text'], state=FSMLogin.login)
async def get_admin_login(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['login'] = message.text
    await FSMLogin.next()
    await message.answer('Password:')


@dp.message_handler(content_types=['text'], state=FSMStudentLogin.student_login)
async def get_student_login(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['login'] = message.text
    await FSMStudentLogin.next()
    await message.answer('Password:')


@dp.message_handler(content_types=['text'], state=FSMStudentLogin.student_password)
async def login_student(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        login = data['login']
        password = message.text
        chat_id = message.chat.id
        await message.answer('Checking auth data')
        await message.delete()
        id = find_student(login, password)
        if not find_student(login, password):
            await bot.send_message(chat_id, 'Wrong credentials. Do you want to try again?', reply_markup=try_again_kb)
            await FSMStudentLogin.not_login.set()
        else:
            link_student(id, chat_id)
            await bot.send_message(chat_id, f'Connected ✅\nTelegram ChatID: <b>{chat_id}</b>\nDiary ID: <b>{id}</b>',
                                   parse_mode='html')
            await FSMStudentLogin.not_login.set()


@dp.message_handler(content_types=['text'], state=FSMLogin.password)
async def login_admin(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        login = data['login']
        password = message.text
        chat_id = message.chat.id
        await message.delete()
        response = check_login(login, password, 'admin')

        if response.ok:
            if not register_user(chat_id):
                await bot.send_message(chat_id=chat_id, text='sorry, server error happened')
            await bot.send_message(chat_id=chat_id, text='Valid credentials')
            await FSMLogin.login.set()
            await bot.send_message(chat_id=chat_id, text='Choose model to create', reply_markup=creation_kb)

        else:
            await bot.send_message(chat_id=chat_id, text='Wrong credentials, try again', reply_markup=login_kb)
            await FSMLogin.login.set()


async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dispatcher):
    await bot.delete_webhook()


WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT', default=8000)
WEBHOOK_HOST = 'https://diary-telegram.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{BOT_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )

# executor.start_polling(dp, skip_updates=True, on_startup=start)
