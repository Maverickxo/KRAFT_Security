import datetime
from collections import defaultdict
import time
from aiogram import Bot, types
import asyncio
from config import API_TOKEN
from clear_msg import process_reply_msg_delete

bot = Bot(token=API_TOKEN)

dt = None
warning_threshold = 3  # Предупреждение после сообщений
mute_threshold = 3  # Порог для наложения мута

last_messages = defaultdict(lambda: {'user_name': '', 'count': 0, 'timestamp': 0, 'mute_count': mute_threshold, })


async def clear_old_messages():
    while True:
        await asyncio.sleep(5)

        current_time = time.time()
        keys_to_remove = []  # Список для удаления ключей из словаря
        for user_id, data in last_messages.items():
            if current_time - data['timestamp'] > 10:
                keys_to_remove.append(user_id)  # Добавляем ключ для удаления в список

        # Удаляем ключи из словаря
        for key in keys_to_remove:
            del last_messages[key]
        print('*', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        for data in last_messages.values():
            print(f"Пользователь: {data['user_name']} | Сообщений: {data['count']} | До мута: {data['mute_count']}")


async def anti_flood(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    last_messages[user_id]['user_name'] = user_name
    last_messages[user_id]['count'] += 1

    if last_messages[user_id]['timestamp'] != 0:
        if time.time() - last_messages[user_id]['timestamp'] < 10:

            # Параметры для предупреждения и мута
            if last_messages[user_id]['count'] >= warning_threshold:
                if last_messages[user_id]['mute_count'] <= warning_threshold:
                    await process_reply_msg_delete(message,
                                                   f"Вы отправляете сообщения слишком часто!\n"
                                                   f"Пожалуйста, уменьшите частоту.\n"
                                                   f"До мута осталось {last_messages[user_id]['mute_count']}"
                                                   f" предупреждений.", 5)

                if last_messages[user_id]['mute_count'] <= 0:
                    await process_reply_msg_delete(message, "Вы отправили слишком много сообщений.\n"
                                                            "Вам будет наложен бан в боевой версии .", 10)

                    # dt = datetime.now() + timedelta(minutes=1)
                    # timestamp = dt.timestamp()
                    # await bot.restrict_chat_member(message.chat.id, message.from_user.id,
                    #                                types.ChatPermissions(can_send_messages=False), until_date=timestamp)

                    last_messages[user_id] = {'count': 0, 'timestamp': 0,
                                              'mute_count': mute_threshold}
                    return

                last_messages[user_id]['mute_count'] -= 1

    last_messages[user_id]['timestamp'] = time.time()
