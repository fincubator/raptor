from pydantic import BaseModel

class TxData(BaseModel):
    u_id: str
    address: str
    tx: str
    tx_error: str
    

class LinkData(BaseModel):
    u_id: str
    r_id: str
    link_id: str