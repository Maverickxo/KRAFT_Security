import asyncio
from aiogram import Bot, types
from config import API_TOKEN

bot = Bot(token=API_TOKEN)


async def mesg_del_time(message: types.Message, delay: int):
    try:
        await asyncio.sleep(delay)
        await message.delete()
    except:
        print("Сообщение уже было удалено!")


async def process_delete_photo(chat_id, text, image_file, delay):
    reply_msg = await bot.send_photo(
        chat_id,
        photo=image_file,
        caption=text,
        parse_mode='markdown'
    )
    if reply_msg is not None:
        _ = asyncio.create_task(mesg_del_time(reply_msg, delay))


async def process_reply_msg_delete(message, text, delay):
    reply_msg = await message.reply(text, parse_mode='markdown')
    if reply_msg is not None:
        _ = asyncio.create_task(mesg_del_time(reply_msg, delay))
