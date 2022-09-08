from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from config import BOT_TOKEN, DIARY_URL
from funcs import check_authorization, register_user
from keyboards import kb_base, login_kb, creation_kb
import requests

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)


class FSMLogin(StatesGroup):
    not_login = State()
    login = State()
    password = State()


async def start(_):
    print('Bot is online')


@dp.message_handler(commands=['start'])
async def greet_new_user(message: types.Message):
    await FSMLogin.not_login.set()
    sticker = open('static/hello.webp', 'rb')
    await bot.send_sticker(chat_id=message.chat.id, sticker=sticker)
    await message.reply(f'Hello <b>{message.from_user.username}</b>!\n'
                        f'This bot is made for <b>Diary</b> web application, please choose your problem',
                        parse_mode='html', reply_markup=kb_base)


@dp.message_handler(content_types=['text'], state=FSMLogin.not_login)
async def base_handler(message: types.Message):
    chat_id = message.chat.id
    if message.text == 'Admin panel':
        await message.reply('Checking authorization')
        if not check_authorization(chat_id=chat_id):
            await message.answer('Access denied, no authorization to admin account\n'
                                 'Want to login?', reply_markup=login_kb)
        else:
            await message.reply('Choose model to create', reply_markup=creation_kb)
    elif message.text == 'Get chat ID':
        await message.reply(f'Your chat ID is: `{chat_id}`, press it to copy', parse_mode='markdown')
    else:
        await message.reply('Unknown command')


@dp.callback_query_handler(state=FSMLogin.not_login)
async def answer_callback(call: types.CallbackQuery):
    if call.data == 'login_yes':
        await call.message.answer('Login:')
        await FSMLogin.login.set()
    elif call.data == 'login_no':
        await call.message.answer('Choose option', reply_markup=kb_base)
    elif call.data == 'create_school':
        await call.message.answer('creating school')
        await call.message.delete_reply_markup()
    elif call.data == 'create_admin':
        await call.message.answer('creating admin')
        await call.message.delete_reply_markup()


@dp.message_handler(content_types=['text'], state=FSMLogin.login)
async def get_login(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['login'] = message.text
    await FSMLogin.next()
    await message.answer('Password:')


@dp.message_handler(content_types=['text'], state=FSMLogin.password)
async def submit_login(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        login = data['login']
        password = message.text
        await message.answer(f'{login} {password}')
        chat_id = message.chat.id
        await message.delete()
        headers = {
            'accept': 'application/json',
        }

        data = {
            'username': login,
            'password': password,
            'client_id': 'admin',
        }

        response = requests.post(f'{DIARY_URL}/token', headers=headers, data=data)

        if response.ok:
            if not register_user(chat_id):
                await bot.send_message(chat_id=chat_id, text='sorry, server error happened')
            await bot.send_message(chat_id=chat_id, text='Valid credentials')
            await FSMLogin.not_login.set()
            await bot.send_message(chat_id=chat_id, text='Choose model to create', reply_markup=creation_kb)

        else:
            await bot.send_message(chat_id=chat_id, text='Wrong credentials, try again', reply_markup=login_kb)
            await FSMLogin.not_login.set()


executor.start_polling(dp, skip_updates=True, on_startup=start)
