from pydantic import BaseModel, validator, Field

class Data(BaseModel):
    telegram_id: str = Field(..., description="Encoded telegram ID")
    referral_inf_code: str = Field(..., description="Encoded referral information code")
    address: str = Field(..., description="Blockchain address")
    tx: str = Field(..., description="Transaction hash")

    @validator('*', pre=True)
    def check_not_empty(cls, value):
        if not value or value.strip() == "":
            raise ValueError("Value cannot be empty")
        return value
