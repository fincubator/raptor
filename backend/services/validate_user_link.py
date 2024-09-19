from fastapi import HTTPException
from models.models import Users
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def validate_user_link(user_id: str, ref_id: str, link_id: str):
    user = await Users.get_or_none(telegram_id=user_id)
    if not user:
        logger.error("User not found.")
        raise HTTPException(status_code=404, detail="User not found.")

    if ref_id not in user.ref_id:
        logger.error("Invalid ref_id.")
        raise HTTPException(status_code=400, detail="Invalid ref_id.")

    if link_id not in user.used_unique_links:
        raise HTTPException(status_code=400, detail="Invalid link_id.")

    if user.used_unique_links[link_id]:
        return {"valid": False, "message": "This referral link has already been used."}
    else:
        user.used_unique_links[link_id] = True
        await user.save()
        return {"valid": True, "message": "Referral link is valid and has been used successfully."}