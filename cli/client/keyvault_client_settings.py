from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import Optional


@dataclass
class KeyVaultClientSettingsData:
    vault_url: Optional[str] = None
    auth_record: Optional[str] = None
    last_login_time: Optional[datetime] = None


class KeyVaultClientSettings(KeyVaultClientSettingsData):
    def __init__(
        self,
        vault_url: Optional[str] = None,
        auth_record: Optional[str] = None,
        last_login_time: Optional[datetime] = None,
    ):
        super().__init__(vault_url, auth_record, last_login_time)
        self._location = Path.home() / ".azkv" / "settings.json"
        self._valid_settings_hours = 24
        self._location.parent.mkdir(parents=True, exist_ok=True)

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
        return self._exists() and self._mtime() > (datetime.now() - timedelta(hours=self._valid_settings_hours))

    def _mtime(self) -> datetime:
        return datetime.fromtimestamp(self._location.stat().st_mtime)

    def _exists(self) -> bool:
        return self._location.exists()
