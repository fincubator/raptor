import logging
import os
import uuid
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from models.models import Developers, Users
from services.encode_decode_id import encode_id
from aiogram.dispatcher.router import Router
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=os.getenv('TG_BOT_TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

allowed_user_id = os.getenv('ALLOWED_USER_ID')
tg_bot_link = os.getenv('TG_BOT_LINK')
website_link = os.getenv('WEBSITE_LINK')


async def generate_unique_link(user_id: str, ref_id: str):
    """Generate a one-time website link.

    Args:
        user_id (str): current tg user_id
        ref_id (str): ref_id for current user
    """
    unique_id = str(uuid.uuid4())
    link = f"{website_link}?link_id={unique_id}&r_id={encode_id(ref_id)}&u_id={encode_id(user_id)}"
    return link, unique_id


async def register_user(message: Message, user_id: str, ref_arg: str, ref_level: int, ref_type: str):
    """Register a new user or generate a one-time link for an existing user.

    Args:
        message (Message): tg message (start)
        user_id (str): current tg user_id
        ref_arg (str): ref_arg = referrer argument from tg message
        ref_level (int): referral level of user
        ref_type (str): devs or users
    """
    ref_level = int(ref_level)
    link, unique_id = await generate_unique_link(user_id, ref_arg)

    # This is not a mistake, it is done intentionally to eliminate race conditions and possible scaling errors:
    user = await Users.get_or_none(telegram_id=user_id)
    if user is None:
        user_data = {
            "telegram_id": user_id,
            "ref_id": ref_arg,
            "ref_type": ref_type,
            "ref_level": ref_level,
            "used_unique_links": {unique_id: False},
        }
        user = await Users.create(**user_data)
    else:
        user.used_unique_links[unique_id] = False
        await user.save()

    ref_link = f"{tg_bot_link}?start={user_id}"
    await message.answer(f"Your referral link to the bot: {ref_link}")
    await message.answer(f"Your one-time website link: {link}")


async def send_new_link_to_user(user_id: str):
    try:
        user = await Users.get_or_none(telegram_id=user_id)
        if user:
            link, unique_id = await generate_unique_link(str(user_id), user.ref_id)
            user.used_unique_links[unique_id] = False
            await user.save()
            await bot.send_message(chat_id=user_id, text=f"Your new one-time website link: {link}")
            logger.info(f"Sent new link to user {user_id}")
        else:
            logger.error(f"User with telegram_id {user_id} not found.")
    except Exception as e:
        logger.error(f"Error sending new link to user {user_id}: {e}")


@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = str(message.from_user.id)
    args = message.text.split()
    ref_arg = args[1] if len(args) > 1 else None

    user = await Users.get_or_none(telegram_id=user_id)

    if user:
        link, unique_id = await generate_unique_link(user_id, user.ref_id)
        user.used_unique_links[unique_id] = False
        await user.save()
        await message.answer(f"Your new one-time website link: {link}")
        return

    if ref_arg:
        if ref_arg == user_id:
            await message.answer("You cannot use your own referral link.")
            return

        dev_codes_list = await Developers.all().values_list('referral_dev_code', flat=True)

        if ref_arg in dev_codes_list:
            ref_level = 1
            ref_type = "developer"
            await register_user(message, user_id, ref_arg, ref_level, ref_type)
        else:
            referrer_user = await Users.get_or_none(telegram_id=ref_arg)
            if referrer_user:
                ref_level = referrer_user.ref_level + 1
                ref_type = "user"
                await register_user(message, user_id, ref_arg, ref_level, ref_type)
            else:
                await message.answer("Access denied. Incorrect referral link.")
                return
    else:
        await message.answer("Access denied. No referral link provided.")
        return


@router.message(Command("add_dev_code"))
async def add_referral_command(message: Message):
    if str(message.from_user.id) != allowed_user_id:
        await message.answer("Access denied. No referral link provided.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Please enter the referral code after the command. Example: /add_dev_code ABC123")
        return

    referral_code = parts[1].strip()

    if not referral_code:
        await message.answer("The referral code cannot be blank. Please try again.")
        return

    try:
        existing_code = await Developers.get_or_none(referral_dev_code=referral_code)
        if existing_code:
            await message.answer("This referral code already exists in the database.")
            return

        await Developers.create(referral_dev_code=referral_code)
        await message.answer(f"Referral code '{referral_code}' successfully added.")
    except Exception as e:
        logger.error(f"Error when adding a referral code: {e}")
        await message.answer(f"Error when adding a referral code: {e}")


@router.message(Command("show_dev_codes"))
async def show_developer_codes_command(message: Message):
    if str(message.from_user.id) != allowed_user_id:
        await message.answer("Access denied. No referral link provided.")
        return
    try:
        existing_codes = await Developers.all()
        if existing_codes:
            codes_list = "\n".join(
                [dev.referral_dev_code for dev in existing_codes])
            await message.answer(f"Existing devs referral codes:\n{codes_list}")
        else:
            await message.answer("There are no existing developer referral codes.")
    except Exception as e:
        logger.error(f"Error in displaying developer referral codes: {e}")
        await message.answer(f"Error in displaying developer referral codes: {e}")

dp.include_router(router)


async def start_telegram_bot():
    try:
        logger.info("Starting the bot...")
        await dp.start_polling(bot)
        logger.info("Bot has stopped.")
    except Exception as e:
        logger.error(f"Error in starting the bot: {e}")
