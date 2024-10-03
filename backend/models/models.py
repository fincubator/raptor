from tortoise import fields
from tortoise.models import Model


class Developers(Model):
    id = fields.IntField(pk=True)
    referral_dev_code = fields.CharField(
        max_length=255, unique=True, index=True)

    class Meta:
        table = "developers"

    def __str__(self):
        return f"Developer(referral_dev_code={self.referral_dev_code})"


class Users(Model):
    id = fields.IntField(pk=True)
    telegram_id = fields.CharField(max_length=255, unique=True, index=True)
    ref_id = fields.CharField(max_length=255)
    ref_type = fields.CharField(max_length=10)
    ref_level = fields.IntField()
    used_unique_links = fields.JSONField(default=dict)
    tia_address = fields.CharField(max_length=255, null=True)
    tia_tx = fields.CharField(max_length=255, null=True)
    tia_tx_error = fields.CharField(max_length=255, null=True)
    fet_address = fields.CharField(max_length=255, null=True)
    fet_tx = fields.CharField(max_length=255, null=True)
    fet_tx_error = fields.CharField(max_length=255, null=True)
    language = fields.CharField(max_length=5, default='en')

    class Meta:
        table = "users"

    def __str__(self):
        return f"User(telegram_id={self.telegram_id})"
