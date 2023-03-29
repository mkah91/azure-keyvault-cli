from datetime import datetime, timedelta, timezone
from typing import Optional

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.identity import (
    AuthenticationRecord,
    InteractiveBrowserCredential,
    TokenCachePersistenceOptions,
)
from azure.keyvault.secrets import SecretClient

from cli.client.keyvault_client_settings import KeyVaultClientSettings
from cli.client.keyvault_secret import Secret


class ClientNotInitializedError(Exception):
    pass


class SecretRequestError(Exception):
    pass


class SecretNotFoundError(Exception):
    pass


class KeyVaultClient:
    def __init__(self, settings: KeyVaultClientSettings):
        self.client: Optional[SecretClient] = None
        self.settings = settings
        self._valid_login_hours = 6

    def _set_client(self, record: AuthenticationRecord):
        if not self.settings.vault_url:
            raise ClientNotInitializedError("Vault URL not set")
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
        if self.settings.last_login_time < (
            datetime.now(timezone.utc) - timedelta(hours=self._valid_login_hours)
        ):
            return True
        return False

    def _auth(self) -> AuthenticationRecord:
        init_credential = InteractiveBrowserCredential(
            cache_persistence_options=TokenCachePersistenceOptions()
        )
        record = init_credential.authenticate()
        record_json = record.serialize()
        self.settings.auth_record = record_json
        self.settings.last_login_time = datetime.now(timezone.utc)
        self.settings.save()
        return record

    def _reuse_auth(self) -> AuthenticationRecord:
        if not self.settings.auth_record:
            raise ClientNotInitializedError("Auth record not set")
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
        try:
            s = self.client.get_secret(name)
        except ResourceNotFoundError as e:
            raise SecretNotFoundError(e)
        except HttpResponseError as e:
            raise SecretRequestError(e)
        return Secret(s.properties.name, s.properties.expires_on, s.value)

    def get_secrets(self) -> list[Secret]:
        if not self.client:
            raise ClientNotInitializedError("Client not initialized")
        try:
            secrets = self.client.list_properties_of_secrets()
        except HttpResponseError as e:
            raise SecretRequestError(e)

        return [Secret(s.name, s.expires_on) for s in secrets]
