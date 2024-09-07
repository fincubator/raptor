from fastapi import HTTPException
from models.models import User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def save_user_delegation_tia(telegram_id: str, referral_inf_code: str, address: str, tx: str) -> str:
    try:
        user = await get_user(telegram_id, referral_inf_code, address, tx)
        user.tia_address = address
        user.tia_tx = tx
        await user.save()
        return [user.telegram_id, user.referral_inf_code, user.tia_address, user.tia_tx]
    
    except HTTPException as e:
        logger.error(f"HTTP Exception: {e.detail}")
        raise e
    
    except Exception as e:
        logger.error(f"Error saving TIA delegation: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while saving TIA delegation.")


async def save_user_delegation_fet(telegram_id: str, referral_inf_code: str, address: str, tx: str):
    try:
        user = await get_user(telegram_id, referral_inf_code, address, tx)
        user.fet_address = address
        user.fet_tx = tx
        await user.save()
        return [user.telegram_id, user.referral_inf_code, user.fet_address, user.fet_tx]
    
    except HTTPException as e:
        logger.error(f"HTTP Exception: {e.detail}")
        raise e
    
    except Exception as e:
        logger.error(f"Error saving FET delegation: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while saving FET delegation.")


async def get_user(telegram_id: str, referral_inf_code: str, address: str, tx: str):
    user = await User.get_or_none(telegram_id=telegram_id)
    
    if not user:
        logger.error(f"User {telegram_id} not found.")
        raise HTTPException(
            status_code=403, detail=f"User {telegram_id} not found.")
    
    if user.referral_inf_code != referral_inf_code:
        logger.error(f"Invalid referral code: {referral_inf_code} for user {telegram_id}.")
        raise HTTPException(
            status_code=400, detail=f"Invalid referral code {referral_inf_code}.")
    
    if not address or not tx:
        raise HTTPException(
            status_code=400, detail="Address or tx cannot be empty.")
    
    return user
