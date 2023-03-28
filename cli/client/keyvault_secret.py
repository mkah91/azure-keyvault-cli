from datetime import datetime, timedelta, timezone
from typing import Optional

from azure.keyvault.secrets import SecretProperties


class Secret:
    def __init__(self, properties: SecretProperties, value: Optional[str] = None):
        self.name = properties.name
        self.expires_on = properties.expires_on
        self.value = None
        if value:
            self.value = value
        self.__days_before_expiration = 15

    def is_expired(self) -> bool:
        if not self.expires_on:
            return False
        return self.expires_on < datetime.now(timezone.utc)

    def is_soon_expired(self) -> bool:
        if not self.expires_on or (self.expires_on < datetime.now(timezone.utc)):
            return False
        return self.expires_on < (datetime.now(timezone.utc) + timedelta(days=self.__days_before_expiration))
