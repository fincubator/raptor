import logging
import asyncio
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from services.encode_decode_id import decode_id
from services.save_user_delegation import save_user_delegation_tia, save_user_delegation_fet
from bot.telegram_bot import start_telegram_bot
from tortoise.contrib.fastapi import register_tortoise
from dotenv import load_dotenv
from schemas import Data


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    modules={'models': ['models.models']},
    generate_schemas=True,
    add_exception_handlers=True,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api_tia")
async def handle_broadcast_request_tia(data: Data):
    logger.info(f"request:{data}")
    try:
        telegram_id, referral_inf_code, address, tx = get_data(data)
        result = await save_user_delegation_tia(
            telegram_id, referral_inf_code, address, tx)
        logger.info(result)
        return result
    except HTTPException as e:
        logger.error(f"Error processing TIA request: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error processing TIA request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.post("/api_fet")
async def handle_broadcast_request_fet(data: Data):
    logger.info(f"request:{data}")
    try:
        telegram_id, referral_inf_code, address, tx = get_data(data)
        result = await save_user_delegation_fet(
            telegram_id, referral_inf_code, address, tx)
        logger.info(result)
        return result
    except HTTPException as e:
        logger.error(f"Error processing FET request: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error processing FET request: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


def get_data(data):
    telegram_id = data.telegram_id
    referral_inf_code = data.referral_inf_code
    address = data.address
    tx = data.tx
    
    if not telegram_id or not referral_inf_code:
        raise HTTPException(
            status_code=400, detail="Invalid data: telegram_id and referral_inf_code cannot be empty.")
    
    try:
        telegram_id = decode_id(telegram_id)
        referral_inf_code = decode_id(referral_inf_code)
    except Exception as e:
        logger.error(f"Error decoding IDs: {e}")
        raise HTTPException(status_code=400, detail="Invalid ID format.")
    
    return [telegram_id, referral_inf_code, address, tx]
