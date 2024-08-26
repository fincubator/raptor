import os
import json
from aiogram import Bot
from tortoise import Tortoise, run_async
from models import Influencer
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Инициализация бота
bot = Bot(token=os.getenv('TG_BOT_TOKEN'))

# Настройка соединения с базой данных
async def init():
    await Tortoise.init(
        db_url='postgres://myuser:12345@localhost/raptor',
        modules={'models': ['models']}
    )
    await Tortoise.generate_schemas()

# Функция для получения ников и сохранения их в JSON
async def fetch_usernames():
    await init()
    influencers = await Influencer.all()
    id_nickname_map = {}

    for influencer in influencers:
        user_id = influencer.telegram_id
        try:
            # Получаем информацию о пользователе по его ID
            user = await bot.get_chat(user_id)
            id_nickname_map[user_id] = user.username if user.username else "No username"
        except Exception as e:
            print(f"Failed to fetch username for ID {user_id}: {e}")
            id_nickname_map[user_id] = "Failed to fetch"

    # Сохранение в JSON
    with open('influencers_usernames.json', 'w') as f:
        json.dump(id_nickname_map, f, ensure_ascii=False, indent=4)

    await Tortoise.close_connections()

# Запуск скрипта
if __name__ == "__main__":
    run_async(fetch_usernames())
