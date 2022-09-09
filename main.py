import uvicorn as uvicorn
from fastapi import FastAPI

from DiaryTelegramBot.telegram.bot import bot

app = FastAPI()


@app.get('/send_data')
async def send_message(user_id: int, message: str):
    await bot.send_message(chat_id=user_id, text=message)


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=5000)