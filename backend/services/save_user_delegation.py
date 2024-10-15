from fastapi import HTTPException
from models.models import Users
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def save_user_delegation_tia(telegram_id: str, address: str, tx: str, tx_error) -> str:
    try:
        user = await get_user(telegram_id)
        if tx:
            user.tia_address = address
            user.tia_tx = tx
        else:
            user.tia_address = address
            user.tia_tx_error = tx_error
        await user.save()
        user = await Users.get_or_none(telegram_id=telegram_id)
        return [user.telegram_id, user.tia_address, user.tia_tx, user.tia_tx_error]

    except HTTPException as e:
        logger.error(f"HTTP Exception: {e.detail}")
        raise e

    except Exception as e:
        logger.error(f"Error saving TIA delegation: {e}")
        raise HTTPException(
            status_code=500, detail="An error occurred while saving TIA delegation.")


async def save_user_delegation_fet(telegram_id: str, address: str, tx: str, tx_error):
    try:
        user = await get_user(telegram_id)
        if tx:
            user.fet_address = address
            user.fet_tx = tx
        else:
            user.fet_address = address
            user.fet_tx_error = tx_error
        await user.save()
        user = await Users.get_or_none(telegram_id=telegram_id)
        return [user.telegram_id, user.fet_address, user.fet_tx, user.fet_tx_error]

    except HTTPException as e:
        logger.error(f"HTTP Exception: {e.detail}")
        raise e

    except Exception as e:
        logger.error(f"Error saving FET delegation: {e}")
        raise HTTPException(
            status_code=500, detail="An error occurred while saving FET delegation.")


async def get_user(telegram_id: str):
    user = await Users.get_or_none(telegram_id=telegram_id)

    if not user:
        logger.error(f"User {telegram_id} not found.")
        raise HTTPException(
            status_code=403, detail=f"User {telegram_id} not found.")

    return user
