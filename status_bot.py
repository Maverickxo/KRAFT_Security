from config import API_TOKEN
from aiogram import Bot

bot = Bot(token=API_TOKEN)


async def on_startup(dispatcher):  # Отправка сообщения при запуске бота
    import datetime
    dt = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    await bot.send_message(chat_id=5869013585, text=f"Бот запущен! {dt}")
