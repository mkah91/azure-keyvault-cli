import json
from pathlib import Path
from datetime import datetime, timedelta

from azure.identity import (
    AuthenticationRecord,
    InteractiveBrowserCredential,
    TokenCachePersistenceOptions,
)
from azure.keyvault.secrets import SecretClient


class KeyvaultClientSettings:
    def __init__(self):
        self.vault_url = None
        self.auth_record = None
        self._location = Path.home() / ".azkv" / "settings.json"
        self._location.parent.mkdir(parents=True, exist_ok=True)

    def save(self):
        settings_dict = {
            "vault_url": self.vault_url,
            "auth_record": self.auth_record,
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

    def is_valid(self):
        return self._exists() and self._mtime() > (datetime.now() - timedelta(hours=4))

    def _mtime(self):
        return datetime.fromtimestamp(self._location.stat().st_mtime)

    def _exists(self):
        return self._location.exists()


class KeyvaultClient:
    def __init__(self, settings):
        self.client = None
        self.settings = settings
    
    def _set_client(self, record):
        credential = InteractiveBrowserCredential(
            cache_persistence_options=TokenCachePersistenceOptions(),
            authentication_record=record,
        )
        self.client = SecretClient(vault_url=self.settings.vault_url, credential=credential)

    def login(self):
        init_credential = InteractiveBrowserCredential(
            cache_persistence_options=TokenCachePersistenceOptions()
        )
        record = init_credential.authenticate()
        self._set_client(record)
        record_json = record.serialize()
        self.settings.auth_record = record_json
        self.settings.save()
        

    def reuse_login(self):
        self.settings.load()
        record = AuthenticationRecord.deserialize(self.settings.auth_record)
        self._set_client(record)
