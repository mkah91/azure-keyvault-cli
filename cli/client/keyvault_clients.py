import dataclasses
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from cli.client.keyvault_client import KeyVaultClient


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


class KeyVaultClients:
    def __init__(self):
        self.clients: dict[str, KeyVaultClient] = {}
        self._location = Path.home() / ".azkv" / "settings.json"
        self._location.parent.mkdir(parents=True, exist_ok=True)
        self._location.touch(exist_ok=True)
        self._valid_settings_hours = 24

    @property
    def location(self):
        return self._location

    def add_client(self, client: KeyVaultClient):
        if client.vault_url in self.clients:
            raise ValueError("Client already exists")
        self.clients[client.vault_url] = client  # type: ignore
        self.save()

    def remove_client(self, client: KeyVaultClient):
        try:
            del self.clients[client.vault_url]  # type: ignore
        except KeyError:
            pass
        self.save()

    def login(self):
        for client in self.clients.values():
            if not self._is_valid():
                client.login(force_reauth=True)
            else:
                client.login()
        self.save()

    def save(self):
        with open(self._location, "w") as f:
            f.write(json.dumps(self.clients, cls=CustomJSONEncoder))

    def load(self):
        if self._location.stat().st_size == 0:
            return
        with open(self._location, "r") as f:
            settings = json.load(f)
        if not settings:
            return
        try:
            for key, setting in settings.items():
                self.clients[key] = KeyVaultClient(**setting)
        except TypeError:
            self.reset()
            raise ValueError("Settings file is not valid")

    def reset(self):
        self.clients = {}
        self.save()

    def _is_valid(self) -> bool:
        return self._exists() and self._mtime() > (
            datetime.now() - timedelta(hours=self._valid_settings_hours)
        )

    def _mtime(self) -> datetime:
        return datetime.fromtimestamp(self._location.stat().st_mtime)

    def _exists(self) -> bool:
        return self._location.exists()

    def run_command(self, command: str, args: list[Any] = None) -> dict[str, Any]:
        if command not in dir(KeyVaultClient):
            raise ValueError(f"Command {command} does not exist")
        if not args:
            args = []
        result = {}
        for k, kv in self.clients.items():
            if kv.is_active:
                result[k] = eval(f"kv.{command}(*args)")
        return result
