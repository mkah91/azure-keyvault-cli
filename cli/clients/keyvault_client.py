import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Optional

from azure.identity import (
    AuthenticationRecord,
    InteractiveBrowserCredential,
    TokenCachePersistenceOptions,
)
from azure.keyvault.secrets import SecretClient, SecretProperties


class ClientNotInitializedError(Exception):
    pass


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
        if not self.expires_on:
            return False
        return self.expires_on < (datetime.now(timezone.utc) + timedelta(days=self.__days_before_expiration))


class KeyVaultClientSettings:
    def __init__(self):
        self.vault_url = None
        self.auth_record = None
        self.last_login_time = None
        self._location = Path.home() / ".azkv" / "settings.json"
        self._location.parent.mkdir(parents=True, exist_ok=True)
        self.__valid_settings_hours = 24

    def save(self):
        settings_dict = {
            "vault_url": self.vault_url,
            "auth_record": self.auth_record,
            "last_login_time": self.last_login_time.isoformat() if self.last_login_time else None,
        }
        with open(self._location, "w") as f:
            f.write(json.dumps(settings_dict))

    def load(self):
        if self._location.stat().st_size == 0:
            return
        with open(self._location, "r") as f:
            settings_dict = json.load(f)
        self.vault_url = settings_dict["vault_url"]
        self.auth_record = settings_dict["auth_record"]
        self.last_login_time = (
            datetime.fromisoformat(settings_dict["last_login_time"]) if settings_dict["last_login_time"] else None
        )

    def is_valid(self) -> bool:
        return self._exists() and self._mtime() > (datetime.now() - timedelta(hours=self.__valid_settings_hours))

    def _mtime(self) -> datetime:
        return datetime.fromtimestamp(self._location.stat().st_mtime)

    def _exists(self) -> bool:
        return self._location.exists()


class KeyVaultClient:
    def __init__(self, settings: KeyVaultClientSettings):
        self.client: Optional[SecretClient] = None
        self.settings = settings
        self.__valid_login_hours = 6

    def _set_client(self, record: AuthenticationRecord):
        credential = InteractiveBrowserCredential(
            cache_persistence_options=TokenCachePersistenceOptions(),
            authentication_record=record,
        )
        self.client = SecretClient(vault_url=self.settings.vault_url, credential=credential)

    def _should_reauth(self) -> bool:
        if not self.settings.is_valid():
            return True
        if not self.settings.auth_record or not self.settings.last_login_time:
            return True
        if self.settings.last_login_time < (datetime.now(timezone.utc) - timedelta(hours=self.__valid_login_hours)):
            return True
        return False

    def _auth(self) -> AuthenticationRecord:
        init_credential = InteractiveBrowserCredential(cache_persistence_options=TokenCachePersistenceOptions())
        record = init_credential.authenticate()
        record_json = record.serialize()
        self.settings.auth_record = record_json
        self.settings.last_login_time = datetime.now(timezone.utc)
        self.settings.save()
        return record

    def _reuse_auth(self) -> AuthenticationRecord:
        self.settings.load()
        record = AuthenticationRecord.deserialize(self.settings.auth_record)
        return record

    def login(self):
        if self._should_reauth():
            record = self._auth()
        else:
            record = self._reuse_auth()
        self._set_client(record)

    def get_secret(self, name: str) -> Secret:
        if not self.client:
            raise ClientNotInitializedError("Client not initialized")
        s = self.client.get_secret(name)
        return Secret(s.properties, s.value)

    def get_secrets(self) -> list[Secret]:
        if not self.client:
            raise ClientNotInitializedError("Client not initialized")
        secrets = self.client.list_properties_of_secrets()
        return [Secret(s) for s in secrets]
