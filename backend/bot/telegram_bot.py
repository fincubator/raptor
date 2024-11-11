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
    messages_lang = MESSAGES.get(lang, MESSAGES['en'])
    text = messages_lang.get(key)
    if not text:
        logger.warning(f"Message key '{key}' not found for language '{lang}'. Falling back to English.")
        text = MESSAGES['en'].get(key, f"Message key '{key}' not found.")
    return text.format(**kwargs)


async def generate_unique_link(user_id: str, ref_id: str):
    unique_id = str(uuid.uuid4())
    link = f"{website_link}?link_id={unique_id}&r_id={encode_id(ref_id)}&u_id={encode_id(user_id)}"
    return link, unique_id


async def send_new_link_to_user(user_id: str):
    try:
        user = await Users.get_or_none(telegram_id=user_id)
        if user:
            lang = user.language or 'en'
            link, unique_id = await generate_unique_link(str(user_id), user.ref_id)
            user.used_unique_links[unique_id] = False
            try:
                await user.save()
                await bot.send_message(chat_id=user_id, text=get_message("new_one_time_link", lang, link=link))
                logger.info(f"Sent new link to user {user_id}")
            except Exception as e:
                logger.error(
                    f"Error with telegram_id {user_id} in send_new_link_to_user; user.save() with new link: {e}")
        else:
            logger.error(f"User with telegram_id {user_id} not found.")
    except Exception as e:
        logger.error(f"Error sending new link to user {user_id}: {e}")


@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = str(message.from_user.id)
    username = str(message.from_user.username)
    firstname = str(message.from_user.first_name)
    args = message.text.split()
    ref_arg = args[1] if len(args) > 1 else None

    user = await Users.get_or_none(telegram_id=user_id)

    if user:
        if user.ref_id != "None":
            lang = user.language or 'en'
            link, unique_id = await generate_unique_link(user_id, user.ref_id)
            user.used_unique_links[unique_id] = False
            try:
                await user.save()
                await message.answer(get_message('your_one_time_link', lang, link=link))
                ref_link = f"{tg_bot_link}?start={user_id}"
                await message.answer(get_message('your_referral_link', lang, ref_link=ref_link))
            except Exception as e:
                logger.error(
                    f"Error with telegram_id {user_id} in cmd_start; user.save() with new link after new start: {e}")
        else:
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
    else:
        user_data = {
            "telegram_id": user_id,
            "username": username if username else None,
            "firstname": firstname if firstname else None,
            "ref_id": ref_arg if ref_arg else "None",
            "ref_type": "None",
            "ref_level": 0,
            "used_unique_links": {},
            "language": None
        }
        try:
            user = await Users.create(**user_data)
            logger.info(f"Created new user with telegram_id {user_id} and ref_id {user.ref_id}")
        except Exception as e:
            logger.error(f"Error creating user with telegram_id {user_id}: {e}")
            await message.answer("An error occurred while registering. Please try again later.")
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
    user_id = str(callback_query.from_user.id)
    ref_arg = callback_data.ref_arg
    username = callback_query.from_user.username
    firstname = callback_query.from_user.first_name

    user = await Users.get_or_none(telegram_id=user_id)
    if not user:
        await callback_query.message.answer("User not found. Please start the bot again.")
        return

    if user.language:
        await callback_query.answer(get_message("language_already_set", lang_code))
        return

    if ref_arg:
        if ref_arg == user_id:
            await callback_query.message.answer(get_message("cannot_use_own_referral", lang_code))
            return

        try:
            dev_codes_list = await Developers.all().values_list("referral_dev_code", flat=True)

            if ref_arg in dev_codes_list:
                ref_level = 1
                ref_type = "developer"
                await bot.send_message(
                    chat_id=user_id,
                    text=get_message("dev_referral", lang_code, ref_arg=ref_arg)
                )
            else:
                referrer_user = await Users.get_or_none(telegram_id=ref_arg)
                if referrer_user:
                    ref_level = referrer_user.ref_level + 1
                    ref_type = "user"
                    if referrer_user.username:
                        await bot.send_message(
                            chat_id=user_id,
                            text=get_message('user_referral', lang_code, referrer_name=referrer_user.username,
                                             name=username if username else firstname)
                        )
                    else:
                        await bot.send_message(
                            chat_id=user_id,
                            text=get_message('user_referral', lang_code, referrer_name=referrer_user.firstname,
                                             name=username if username else firstname)
                        )
                else:
                    await callback_query.message.answer(get_message("access_denied_incorrect_referral", lang_code))
                    return
        except Exception as e:
            logger.error(f"Error in checking ref_arg in Developers or Users: {e}")
    else:
        await callback_query.message.answer(get_message("access_denied_no_referral", lang_code))
        return

    link, unique_id = await generate_unique_link(user_id, ref_arg)
    user.ref_id = ref_arg
    user.ref_type = ref_type
    user.ref_level = ref_level
    user.used_unique_links[unique_id] = False
    user.language = lang_code
    try:
        await user.save()
        logger.info(f"Updated user {user_id} with ref_id {ref_arg} and language {lang_code}")
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        await callback_query.message.answer("An error occurred while updating your profile. Please try again later.")
        return

    ref_link = f"{tg_bot_link}?start={user_id}"
    await bot.send_message(
        chat_id=user_id,
        text=get_message('your_referral_link', lang_code, ref_link=ref_link)
    )
    await bot.send_message(
        chat_id=user_id,
        text=get_message('your_one_time_link', lang_code, link=link)
    )

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
        logger.info(f"Added new developer referral code: {referral_code}")
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
            await message.answer(f"Existing developer referral codes:\n{codes_list}")
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
