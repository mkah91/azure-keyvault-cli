from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.identity import (
    AuthenticationRecord,
    InteractiveBrowserCredential,
    TokenCachePersistenceOptions,
)
from azure.keyvault.secrets import SecretClient
from pydantic import validate_arguments

from cli.client.keyvault_secret import Secret


class ClientNotInitializedError(Exception):
    pass


class SecretRequestError(Exception):
    pass


class SecretNotFoundError(Exception):
    pass


@validate_arguments
@dataclass
class KeyVaultClient:
    vault_url: Optional[str] = None
    auth_record: Optional[str] = None
    last_login_time: Optional[datetime] = None
    is_active: bool = True

    def __post_init__(self):
        self._client: Optional[SecretClient] = None
        self._valid_login_hours = 6

    def _set_client(self, record: AuthenticationRecord):
        if not self.vault_url:
            raise ClientNotInitializedError("Vault URL not set")
        credential = InteractiveBrowserCredential(
            cache_persistence_options=TokenCachePersistenceOptions(allow_unencrypted_storage=True),
            authentication_record=record,
        )
        self._client = SecretClient(vault_url=self.vault_url, credential=credential)

    def _should_reauth(self) -> bool:
        if not self.auth_record or not self.last_login_time:
            return True
        if self.last_login_time < (
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
        self.auth_record = record_json
        self.last_login_time = datetime.now(timezone.utc)
        return record

    def _reuse_auth(self) -> AuthenticationRecord:
        if not self.auth_record:
            raise ClientNotInitializedError("Auth record not set")
        record = AuthenticationRecord.deserialize(self.auth_record)
        return record

    def login(self, force_reauth: bool = False):
        if force_reauth or self._should_reauth():
            record = self._auth()
        else:
            record = self._reuse_auth()
        self._set_client(record)

    def get_secret(self, name: str) -> Secret:
        if not self._client:
            raise ClientNotInitializedError("Client not initialized")
        try:
            s = self._client.get_secret(name)
        except ResourceNotFoundError as e:
            raise SecretNotFoundError(e)
        except HttpResponseError as e:
            raise SecretRequestError(e)
        return Secret(s.properties.name, s.properties.expires_on, s.value)

    def get_secrets(self) -> list[Secret]:
        if not self._client:
            raise ClientNotInitializedError("Client not initialized")
        try:
            secrets = self._client.list_properties_of_secrets()
        except HttpResponseError as e:
            raise SecretRequestError(e)

        return [Secret(s.name, s.expires_on) for s in secrets]

    def set_secret(self, secret: Secret):
        if not self._client:
            raise ClientNotInitializedError("Client not initialized")
        if not secret.name:
            raise ValueError("Secret name cannot be empty")
        if not secret.value:
            raise ValueError("Secret value cannot be empty")
        try:
            self._client.set_secret(secret.name, secret.value)
        except HttpResponseError as e:
            raise SecretRequestError(e)
