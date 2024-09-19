from pydantic import BaseModel, validator, Field

class TxData(BaseModel):
    telegram_id: str
    address: str
    tx: str
    tx_error: str
    

class LinkData(BaseModel):
    user_id: str
    ref_id: str
    link_id: str