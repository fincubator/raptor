from tortoise import fields
from tortoise.models import Model

class Developer(Model):
    id = fields.IntField(pk=True)
    referral_dev_code = fields.CharField(max_length=255, unique=True, index=True)

class Influencer(Model):
    id = fields.IntField(pk=True)
    telegram_id = fields.CharField(max_length=255, unique=True, index=True) # = ref cod for User
    referral_dev_code = fields.CharField(max_length=255, index=True)

class User(Model):
    id = fields.IntField(pk=True)
    telegram_id = fields.CharField(max_length=255, unique=True, index=True)
    referral_inf_code = fields.CharField(max_length=255, index=True)
    tia_address = fields.CharField(max_length=255, null=True)
    fet_address = fields.CharField(max_length=255, null=True)
    tia_tx = fields.CharField(max_length=255, null=True)
    fet_tx = fields.CharField(max_length=255, null=True)
    
    