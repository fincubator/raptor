import logging
import base64
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from tortoise.exceptions import DoesNotExist
from models import Developer, Influencer, User
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


def encode_user_id(user_id: int) -> str:
    """Encode the Telegram user ID into a non-human-readable format."""
    return base64.urlsafe_b64encode(str(user_id).encode()).decode()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = str(message.from_user.id)

    """Check referal link"""
    args = message.text.split()
    if len(args) > 1:
        referral_arg = args[1]
    else:
        referral_arg = None
        await message.answer("Access denied. No referral link provided.")
        return

    try:
        dev_existing_codes = await Developer.all()
        dev_codes_list = [dev.referral_dev_code for dev in dev_existing_codes]

        """Check ref code or inf code"""
        if referral_arg in dev_codes_list:
            inf_link = f"{tg_bot_link}?start={user_id}"
            await Influencer.get_or_create(telegram_id=user_id, defaults={"referral_dev_code": referral_arg, "telegram_id": user_id})
            await message.answer(f"Welcome, Influencer! Here is your referral link: {inf_link}")
        else:
            influencer = await Influencer.get_or_none(telegram_id=referral_arg)
            if influencer:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="tia", callback_data=f"tia:{referral_arg}:{user_id}"),
                        InlineKeyboardButton(
                            text="fet", callback_data=f"fet:{referral_arg}:{user_id}"),
                        InlineKeyboardButton(
                            text="both", callback_data=f"both:{referral_arg}:{user_id}"),
                    ]
                ])
                await message.answer("Please choose the link you want to receive:", reply_markup=keyboard)
            else:
                await message.answer("Access denied. Invalid referral link.")
    except Exception as e:
        logger.error(e)
        await message.answer("Access denied. Invalid referral link.")


@router.callback_query()
async def handle_link_choice(callback_query: types.CallbackQuery):
    try:
        choice, referral_arg, user_id = callback_query.data.split(":")

        if choice == "tia":
            user_link = f"{website_link}/tia?referral_code={encode_user_id(referral_arg)}&id={encode_user_id(user_id)}"
        elif choice == "fet":
            user_link = f"{website_link}/fet?referral_code={encode_user_id(referral_arg)}&id={encode_user_id(user_id)}"
        elif choice == "both":
            user_link = f"{website_link}/both?referral_code={encode_user_id(referral_arg)}&id={encode_user_id(user_id)}"
        else:
            await callback_query.message.answer("Invalid choice. Please try again.")
            return

        await User.get_or_create(telegram_id=user_id, defaults={"referral_inf_code": referral_arg, "telegram_id": user_id})

        await callback_query.message.answer(f"Here is your link: {user_link}")

        await callback_query.answer()
    except Exception as e:
        logger.error(e)
        await callback_query.message.answer(f"Something went wrong. Please try again or connect to developers.")


@router.message(Command("add_referral"))
async def add_referral_command(message: Message):
    """Add devs ref code"""
    if str(message.from_user.id) != allowed_user_id:
        await message.answer("Access denied. Invalid referral link.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Please enter the referral code after the command.\nExample: /add_referral ABC123")
        return

    referral_code = parts[1].strip()

    if not referral_code:
        await message.answer("The referral code cannot be blank. Please try again.")
        return

    try:
        existing_code = await Developer.get_or_none(referral_dev_code=referral_code)
        if existing_code:
            await message.answer("This referral code already exists in the database.")
            return

        await Developer.create(referral_dev_code=referral_code)
        await message.answer(f"Referral code '{referral_code}' successfully added to the database.")
    except Exception as e:
        logger.error(e)
        await message.answer(f"Something went wrong.\n Error: {e}")


@router.message(Command("show_developer_codes"))
async def show_developer_codes_command(message: Message):
    """Show all devs refs codes"""
    if str(message.from_user.id) != allowed_user_id:
        await message.answer("Access denied. Invalid referral link.")
        return

    try:
        existing_codes = await Developer.all()
        if existing_codes:
            codes_list = "\n".join(
                [dev.referral_dev_code for dev in existing_codes])
            await message.answer(f"Existing developer referral codes:\n{codes_list}")
        else:
            await message.answer("No existing developer referral codes.")
    except Exception as e:
        logger.error(e)
        await message.answer(f"Something went wrong.\n Error: {e}")


@router.message(Command("show_influencer_codes"))
async def show_influencer_codes_command(message: Message):
    """Show all infls codes"""
    if str(message.from_user.id) != allowed_user_id:
        await message.answer("Access denied. Invalid referral link.")
        return
    try:
        existing_codes = await Influencer.all()
        if existing_codes:
            codes_list = "\n".join([inf.telegram_id for inf in existing_codes])
            await message.answer(f"Existing influencer referral codes:\n{codes_list}")
        else:
            await message.answer("No existing influencer referral codes.")
    except Exception as e:
        logger.error(e)
        await message.answer(f"Something went wrong.\n Error: {e}")


@router.message(Command("show_user_codes"))
async def show_user_codes_command(message: Message):
    """Show all user codes"""
    if str(message.from_user.id) != allowed_user_id:
        await message.answer("Access denied. Invalid referral link.")
        return
    try:
        existing_codes = await User.all()
        if existing_codes:
            codes_dict = {}
            for user in existing_codes:
                codes_dict.update({user.telegram_id: user.referral_inf_code})
            await message.answer(f"Existing user referral codes:\n{codes_dict}")
        else:
            await message.answer("No existing user referral codes.")
    except Exception as e:
        logger.error(e)
        await message.answer(f"Something went wrong.\n Error: {e}")


@router.message(Command("delete_developer_code"))
async def delete_developer_code_command(message: Message):
    """Delete dev ref code"""
    if str(message.from_user.id) != allowed_user_id:
        await message.answer("Access denied. Invalid referral link.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Please enter the referral code after the command.\nExample: /delete_developer_code ABC123")
        return

    referral_code = parts[1].strip()
    try:
        deleted_count = await Developer.filter(referral_dev_code=referral_code).delete()
        if deleted_count > 0:
            await message.answer(f"Referral code '{referral_code}' deleted.")
        else:
            await message.answer(f"Referral code '{referral_code}' not found.")
    except Exception as e:
        logger.error(e)
        await message.answer(f"Something went wrong.\n Error: {e}")


@router.message(Command("delete_influencer_code"))
async def delete_influencer_code_command(message: Message):
    """Delete inf ref code"""
    if str(message.from_user.id) != allowed_user_id:
        await message.answer("Access denied. Invalid referral link.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Please enter the influencer referral code after the command.\nExample: /delete_influencer_code ABC123")
        return

    referral_code = parts[1].strip()
    try:
        deleted_count = await Influencer.filter(telegram_id=referral_code).delete()
        if deleted_count > 0:
            await message.answer(f"Referral code '{referral_code}' deleted.")
        else:
            await message.answer(f"Referral code '{referral_code}' not found.")
    except Exception as e:
        logger.error(e)
        await message.answer(f"Something went wrong.\n Error: {e}")


dp.include_router(router)


async def start_telegram_bot():
    logger.info("Starting Telegram polling...")
    await dp.start_polling(bot)
    logger.info("Telegram polling stopped")
