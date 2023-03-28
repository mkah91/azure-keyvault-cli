from datetime import datetime, timedelta
import json
from pathlib import Path


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
