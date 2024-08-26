import base64
import logging
import asyncio
import os
from fastapi import FastAPI, Form, HTTPException, Query
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from contextlib import asynccontextmanager
from models import Developer, Influencer, User
from tortoise.contrib.fastapi import register_tortoise
from telegram_bot import start_telegram_bot
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

env = Environment(loader=FileSystemLoader("templates"))
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Telegram bot...")
    asyncio.create_task(start_telegram_bot())
    yield
    logger.info("Shutting down Telegram bot...")

app = FastAPI(lifespan=lifespan)

register_tortoise(
    app,
    db_url=os.getenv('DB_URL'),
    modules={'models': ['models']},
    generate_schemas=True,
    add_exception_handlers=True,
)


async def render_page(referral_code: str, id: str, page_name: str):
    referral_code = decode_referral_code(referral_code)
    id = decode_referral_code(id)
    user = await User.get_or_none(telegram_id=id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.referral_inf_code != referral_code:
        raise HTTPException(status_code=403, detail="Invalid referral code")

    logger.info(f"User {user.telegram_id} accessed {page_name.upper()} page")
    template = env.get_template(f"{page_name}_page.html")
    return template.render(referral_code=referral_code, user_id=id)


@app.get("/tia", response_class=HTMLResponse)
async def tia_page(referral_code: str = Query(...), id: str = Query(...)):
    return await render_page(referral_code, id, "tia")


@app.get("/fet", response_class=HTMLResponse)
async def fet_page(referral_code: str = Query(...), id: str = Query(...)):
    return await render_page(referral_code, id, "fet")


@app.get("/both", response_class=HTMLResponse)
async def both_page(referral_code: str = Query(...), id: str = Query(...)):
    return await render_page(referral_code, id, "both")


@app.post("/tia", response_class=HTMLResponse)
async def submit_tia(user_id: str = Form(...), address: str = Form(...), amount: float = Form(...)):
    return await submit_data(user_id, address, amount, "tia")


@app.post("/fet", response_class=HTMLResponse)
async def submit_fet(user_id: str = Form(...), address: str = Form(...), amount: float = Form(...)):
    return await submit_data(user_id, address, amount, "fet")


@app.post("/both", response_class=HTMLResponse)
async def submit_both(user_id: str = Form(...), tia_address: str = Form(...), tia_amount: float = Form(...),
                      fet_address: str = Form(...), fet_amount: float = Form(...)):
    await submit_data(user_id, tia_address, tia_amount, "tia")
    return await submit_data(user_id, fet_address, fet_amount, "fet")


async def submit_data(user_id: str, address: str, amount: float, page_name: str):
    user = await User.get_or_none(telegram_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if page_name == "tia":
        user.tia_address = address
        user.tia_amount = amount
    elif page_name == "fet":
        user.fet_address = address
        user.fet_amount = amount

    await user.save()

    logger.info(
        f"User {user.telegram_id} submitted data for {page_name.upper()}: Address: {address}, Amount: {amount}")

    return f"<h1>{page_name.upper()} Submission: user_id: {user.telegram_id}, Address tia: {user.tia_address}, Value tia: {user.tia_amount}, Address fet: {user.fet_address}, Value fet: {user.fet_amount}, Ref: {user.referral_inf_code}</h1>"


def encode_user_id(user_id: str) -> str:
    return base64.urlsafe_b64encode(str(user_id).encode()).decode()


def decode_referral_code(referral_code: str) -> str:
    try:
        return str(base64.urlsafe_b64decode(referral_code).decode())
    except Exception as e:
        logger.error(
            f"Failed to decode referral code: {referral_code}. Error: {e}")
        return None
