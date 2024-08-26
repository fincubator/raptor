import os
import json
from aiogram import Bot
from tortoise import Tortoise, run_async
from models import Influencer
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv('TG_BOT_TOKEN'))

async def init():
    await Tortoise.init(
        db_url=os.getenv('DB_URL'),
        modules={'models': ['models']}
    )
    await Tortoise.generate_schemas()

async def fetch_usernames():
    await init()
    influencers = await Influencer.all()
    id_nickname_map = {}

    for influencer in influencers:
        user_id = influencer.telegram_id
        try:
            user = await bot.get_chat(user_id)
            id_nickname_map[user_id] = user.username if user.username else "No username"
        except Exception as e:
            print(f"Failed to fetch username for ID {user_id}: {e}")
            id_nickname_map[user_id] = "Failed to fetch"

    with open('influencers_usernames.json', 'w') as f:
        json.dump(id_nickname_map, f, ensure_ascii=False, indent=4)

    await Tortoise.close_connections()

if __name__ == "__main__":
    run_async(fetch_usernames())
