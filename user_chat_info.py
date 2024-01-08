from connect_bd import DatabaseConnection
import datetime


def new_chat_users(user_id, full_name):
    try:
        # Установка соединения с базой данных и создание курсора с помощью контекстного менеджера
        with DatabaseConnection() as cursor:
            data_time_new_chat = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute('SELECT user_id FROM new_users_chat WHERE user_id  = %s', (user_id,))
            user_exst = cursor.fetchone()
            if user_exst:
                print('Юзер существует ')
                cursor.execute(
                    'UPDATE new_users_chat SET data_time_new_chat = %s WHERE user_id = %s',
                    (data_time_new_chat, user_id,))
                print('Время вступления чата обновлено для пользователя')
            else:
                cursor.execute(
                    'INSERT INTO new_users_chat (user_id, full_name, data_time_new_chat) VALUES (%s, %s, %s)',
                    (user_id, full_name, data_time_new_chat,))
                print('Юзер добавлен')
    except Exception as e:
        print(f"Произошла ошибка: {e}")


def lv_chat_users(user_id):
    try:
        # Установка соединения с базой данных и создание курсора с помощью контекстного менеджера
        with DatabaseConnection() as cursor:
            data_time_left_chat = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute('SELECT user_id FROM new_users_chat WHERE user_id = %s', (user_id,))
            user_exists = cursor.fetchone()

            if user_exists:
                print('Юзер exit')
                cursor.execute(
                    'UPDATE new_users_chat SET data_time_left_chat = %s WHERE user_id = %s',
                    (data_time_left_chat, user_id))
                print('Время покидания чата обновлено для пользователя')

    except Exception as e:
        print(f"Произошла ошибка: {e}")
