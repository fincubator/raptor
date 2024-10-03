import logging
import os
import uuid
import json
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.dispatcher.router import Router
from aiogram.filters.callback_data import CallbackData

from models.models import Developers, Users
from services.encode_decode_id import encode_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=os.getenv('TG_BOT_TOKEN'))
dp = Dispatcher()
router = Router()

allowed_user_id = os.getenv('ALLOWED_USER_ID')
tg_bot_link = os.getenv('TG_BOT_LINK')
website_link = os.getenv('WEBSITE_LINK')

with open('local/locales.json', 'r', encoding='utf-8') as f:
    MESSAGES = json.load(f)


class LanguageCallback(CallbackData, prefix="set_lang"):
    lang_code: str
    ref_arg: str


def get_message(key: str, lang: str, **kwargs):
    text = MESSAGES.get(lang, MESSAGES['en']).get(key, MESSAGES['en'][key])
    return text.format(**kwargs)


async def generate_unique_link(user_id: str, ref_id: str):
    unique_id = str(uuid.uuid4())
    link = f"{website_link}?link_id={unique_id}&r_id={encode_id(ref_id)}&u_id={encode_id(user_id)}"
    return link, unique_id


async def register_user(user_id: str, ref_arg: str, ref_level: int, ref_type: str, lang_code: str):
    user_data = {
        "telegram_id": user_id,
        "ref_id": ref_arg,
        "ref_type": ref_type,
        "ref_level": ref_level,
        "used_unique_links": {},
        "language": lang_code
    }

    user = await Users.create(**user_data)

    link, unique_id = await generate_unique_link(user_id, user.ref_id)
    user.used_unique_links[unique_id] = False
    await user.save()

    ref_link = f"{tg_bot_link}?start={user_id}"
    await bot.send_message(
        chat_id=user_id,
        text=get_message('your_referral_link', lang_code, ref_link=ref_link)
    )
    await bot.send_message(
        chat_id=user_id,
        text=get_message('your_one_time_link', lang_code, link=link)
    )


async def send_new_link_to_user(user_id: str):
    try:
        user = await Users.get_or_none(telegram_id=user_id)
        if user:
            lang = user.language or 'en'
            link, unique_id = await generate_unique_link(str(user_id), user.ref_id)
            user.used_unique_links[unique_id] = False
            await user.save()
            await bot.send_message(chat_id=user_id, text=get_message('new_one_time_link', lang, link=link))
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
        lang = user.language or 'en'
        link, unique_id = await generate_unique_link(user_id, user.ref_id)
        user.used_unique_links[unique_id] = False
        await user.save()
        await message.answer(get_message('new_one_time_link', lang, link=link))
    else:
        if ref_arg:
            if ref_arg == user_id:
                await message.answer("You cannot use your own referral link.")
                return

            dev_codes_list = await Developers.all().values_list('referral_dev_code', flat=True)

            if ref_arg in dev_codes_list or await Users.get_or_none(telegram_id=ref_arg):
                pass
            else:
                await message.answer("Access denied. Incorrect referral link.")
                return
        else:
            await message.answer("Access denied. No referral link provided.")
            return

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="English",
                    callback_data=LanguageCallback(lang_code='en', ref_arg=ref_arg or '').pack()
                ),
                InlineKeyboardButton(
                    text="Русский",
                    callback_data=LanguageCallback(lang_code='ru', ref_arg=ref_arg or '').pack()
                )
            ]
        ])
        await message.answer(
            "Please choose your language / Пожалуйста, выберите ваш язык",
            reply_markup=keyboard
        )


@router.callback_query(LanguageCallback.filter())
async def language_selected(callback_query: CallbackQuery, callback_data: LanguageCallback):
    lang_code = callback_data.lang_code
    ref_arg = callback_data.ref_arg or None
    user_id = str(callback_query.from_user.id)

    user = await Users.get_or_none(telegram_id=user_id)
    if user:
        await callback_query.answer("You have already selected your language.")
        return

    if ref_arg:
        if ref_arg == user_id:
            await callback_query.message.answer("You cannot use your own referral link.")
            return

        dev_codes_list = await Developers.all().values_list('referral_dev_code', flat=True)

        if ref_arg in dev_codes_list:
            ref_level = 1
            ref_type = "developer"
        else:
            referrer_user = await Users.get_or_none(telegram_id=ref_arg)
            if referrer_user:
                ref_level = referrer_user.ref_level + 1
                ref_type = "user"
            else:
                await callback_query.message.answer("Access denied. Incorrect referral link.")
                return
    else:
        await callback_query.message.answer("Access denied. No referral link provided.")
        return

    await register_user(user_id, ref_arg, ref_level, ref_type, lang_code)

    await callback_query.answer(get_message('language_set', lang_code), show_alert=False)
    await callback_query.message.delete()


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

