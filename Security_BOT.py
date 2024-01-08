import asyncio
import random
import logging
import os

from aiogram import Bot, Dispatcher, types, executor

from create_img import create_image

from config import API_TOKEN, time_kick

from clear_msg import process_reply_msg_delete, process_delete_photo

from datetime import datetime, timedelta

from user_chat_info import new_chat_users, lv_chat_users

from anti_flod import clear_old_messages, anti_flood

from status_bot import on_startup

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)
tasks = {}


@dp.message_handler(commands=['mute'], is_chat_admin=True)
async def mute(message: types.message):
    print(message.chat.type)
    adm_name = message.from_user.full_name

    if not message.reply_to_message:
        await process_reply_msg_delete(message, "Эта команда должна быть ответом на сообщение!", 5)
        await message.delete()
        return

    try:
        muteint = int(message.text.split()[1])
        mutetype = message.text.split()[2]
        comment = " ".join(message.text.split()[3:])
    except IndexError:
        # await message.answer('Не хватает аргументов!\nПример:\n`/mute 1 ч причина`',parse_mode='markdown')
        await message.delete()
        return

    dt = None
    if mutetype in ["ч", "часов", "час"]:
        dt = datetime.now() + timedelta(hours=muteint)

    elif mutetype in ["м", "минут", "минуты"]:
        dt = datetime.now() + timedelta(minutes=muteint)

    elif mutetype in ["д", "дней", "день"]:
        dt = datetime.now() + timedelta(days=muteint)

    else:
        await process_reply_msg_delete(message, 'Неизвестный тип времени (допустимые значения: ч, м, д)', 5)
        await message.delete()
        return

    timestamp = dt.timestamp()
    await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id,
                                   types.ChatPermissions(can_send_messages=False), until_date=timestamp)

    get_user_name = message.reply_to_message.from_user.full_name
    get_user_id = message.reply_to_message.from_user.id
    reply_text = (
        f"•*Решение принято: {adm_name}*\n"
        f"•*Нарушитель:* [{get_user_name}](tg://user?id={get_user_id})\n"
        f'•*Срок наказания: {muteint} {mutetype}*\n'
        f'•*Причина: {comment}*'
    )

    await process_reply_msg_delete(message, reply_text, 30)
    await message.delete()


async def left_member(user_id, full_name, chat_id):
    print(f"Участник покинул чат: {full_name} (ID: {user_id})")
    lv_chat_users(user_id)  # Вызов функции для обработки выхода участника
    with open('video_2023-09-16_01-42-43.mp4', 'rb') as image_file:
        tmg = await bot.send_video(chat_id, image_file, caption=f'Чат покинул: {full_name}')

        async def left_clear():
            try:
                await asyncio.sleep(20)
                await tmg.delete()
            except Exception as e:
                print(f"Ошибка при удалении сообщения: {e}")

        _ = asyncio.create_task(left_clear())


async def new_member(user_id, full_name, chat_id):
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    answer = num1 + num2
    tasks[user_id] = {'answer': answer,
                      'asked_by': user_id}  # Сохраняем ответ и идентификатор пользователя, кому задали задачу

    image_path = await create_image(num1, num2)
    try:
        with open(image_path, 'rb') as image_file:
            await process_delete_photo(chat_id,
                                       f"*Привет!* [{full_name}](tg://user?id={user_id})\n\n"
                                       f"Для продолжения решите задачу\n\n"
                                       f"У вас {time_kick} секунд, вы будете исключены из чата!",
                                       image_file, 60)
    finally:
        os.remove(image_path)  # Удаление изображения после отправки
        new_chat_users(user_id, full_name)

    async def kick_user(user):
        await asyncio.sleep(time_kick)
        if user in tasks and tasks[user][
            'asked_by'] == user_id:  # Проверяем, существует ли пользователь в словаре и ответил ли тот, кому была задача
            del tasks[user]
            msg = await bot.send_message(chat_id, f"{full_name}\nВремя истекло. Вы исключены из чата.")
            await asyncio.sleep(5)
            await bot.kick_chat_member(chat_id, user_id)
            await msg.delete()

    _ = asyncio.create_task(kick_user(user_id))


@dp.message_handler(lambda message: message.text.isdigit())
async def solve_task(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    if user_id in tasks and int(message.text) == tasks[user_id]['answer']:

        del tasks[user_id]  # Удаляем задачу из словаря после правильного ответа

        await process_reply_msg_delete(message,
                                       f"Правильно! Вы решили задачу.\n"
                                       f"Добро пожаловать! "
                                       f"[{user_name}](tg://user?id={user_id})", 20)

    elif user_id in tasks:
        await process_reply_msg_delete(message, f"*Неправильный ответ!* "
                                                f"[{user_name}](tg://user?id={user_id})\n"
                                                "Попробуйте еще раз или будете исключены из чата.", 5)


@dp.message_handler()
async def anti_flood_fun(message: types.Message):
    await anti_flood(message)


@dp.chat_member_handler()
async def some_handler(chat_member: types.ChatMemberUpdated):
    user_id = chat_member.new_chat_member.user.id
    full_name = chat_member.new_chat_member.user.full_name
    chat_id = chat_member.chat.id

    if chat_member.new_chat_member.status == "member":
        await new_member(user_id, full_name, chat_id)

        user_id = chat_member.new_chat_member.user.id
        print(f"ChatMemberUpdated: Пользователь {user_id} вошел в чат")

    elif chat_member.new_chat_member.status == "left":
        await left_member(user_id, full_name, chat_id)
        user_id = chat_member.old_chat_member.user.id
        print(f"ChatMemberUpdated: Пользователь {user_id} покинул чат")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(clear_old_messages())  # Запускаем функцию очистки старых сообщений
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
