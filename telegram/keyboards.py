from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove
ReplyKeyboardRemove()
'''Main keyboard'''
student = KeyboardButton('Connect for notifications')

kb_base = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_base.add(student)

'''Ask for login keyboard'''
login_yes = InlineKeyboardButton(text='Yes', callback_data='login_yes')
login_no = InlineKeyboardButton(text='No', callback_data='login_no')

login_kb = InlineKeyboardMarkup(row_width=2)
login_kb.add(login_yes, login_no)

'''Create model keyboard'''
create_admin = InlineKeyboardButton(text='Admin', callback_data='create_admin')
create_school = InlineKeyboardButton(text='School', callback_data='create_school')

creation_kb = InlineKeyboardMarkup(row_width=2)
creation_kb.add(create_school, create_admin)

'''Connect account keyboard'''
proceed = InlineKeyboardButton(text='Proceed', callback_data='proceed')

connect_kb = InlineKeyboardMarkup()
connect_kb.add(proceed)

'''Student try again keyboard'''
yes = InlineKeyboardButton(text='Yes', callback_data='proceed')
no = InlineKeyboardButton(text='No', callback_data='no')

try_again_kb = InlineKeyboardMarkup(row_width=2)
try_again_kb.add(yes, no)
