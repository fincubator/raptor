import logging
import asyncio
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from services.encode_decode_id import decode_id
from services.save_user_delegation import save_user_delegation_tia, save_user_delegation_fet
from services.validate_user_link import validate_user_link
from bot.telegram_bot import start_telegram_bot
from tortoise.contrib.fastapi import register_tortoise
from dotenv import load_dotenv
from schemas import TxData, LinkData


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
    db_url=os.getenv('DATABASE_URL'),
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


@app.post("/api/check_link")
async def check_link(data: LinkData):
    logger.info(f"Check link request: {data}")
    try:
        user_id = data.user_id
        ref_id = data.ref_id
        link_id = data.link_id
        
        if not user_id or not ref_id or not link_id:
            raise HTTPException(
                status_code=400, detail="Invalid data: user_id, ref_id, and link_id are required."
            )
        try:
            decoded_user_id = decode_id(user_id)
            decoded_ref_id = decode_id(ref_id)
        except Exception as e:
            logger.error(f"Error decoding IDs: {e}")
            raise HTTPException(status_code=400, detail="Invalid ID format.")
        result = await validate_user_link(decoded_user_id, decoded_ref_id, link_id)
        logger.info(result)
        return result     
    except HTTPException as e:
        logger.error(f"HTTPException in /api/check_link: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in /api/check_link: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")


@app.post("/api/tia")
async def handle_broadcast_request_tia(data: TxData):
    logger.info(f"request:{data}")
    try:
        telegram_id, address, tx, tx_error = get_data(data)
        result = await save_user_delegation_tia(
            telegram_id, address, tx, tx_error)
        logger.info(f"result {result}")
        return result
    except HTTPException as e:
        logger.error(f"Error processing TIA request: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error processing TIA request: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}")


@app.post("/api/fet")
async def handle_broadcast_request_fet(data: TxData):
    logger.info(f"request:{data}")
    try:
        telegram_id, address, tx, tx_error = get_data(data)
        result = await save_user_delegation_fet(
            telegram_id, address, tx, tx_error)
        logger.info(f"result {result}")
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
    address = data.address
    tx = data.tx
    tx_error = data.tx_error

    if not telegram_id:
        raise HTTPException(
            status_code=400, detail="Invalid data: telegram_id and ref_id cannot be empty.")

    try:
        telegram_id = decode_id(telegram_id)
    except Exception as e:
        logger.error(f"Error decoding IDs: {e}")
        raise HTTPException(status_code=400, detail="Invalid ID format.")

    return [telegram_id, address, tx, tx_error]
