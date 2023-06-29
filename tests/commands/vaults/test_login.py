import pytest

from cli.client.keyvault_client import KeyVaultClient
from cli.client.keyvault_clients import KeyVaultClients
from cli.commands.vaults.login import login


@pytest.fixture
def mock_kv_client(mocker):
    mock_client = mocker.MagicMock(spec=KeyVaultClient)
    mock_client.vault_url = "https://test.vault.azure.net"
    mock_client.login.return_value = "test"
    return mock_client


@pytest.fixture
def mock_kv_clients(mocker, mock_kv_client):
    mock_clients = mocker.MagicMock(spec=KeyVaultClients)
    mock_clients.clients = {"https://test.vault.azure.net": mock_kv_client}
    return mock_clients


def test_login_with_vault_url(mock_kv_client, mock_kv_clients):
    login(mock_kv_clients, vault_url="https://test.vault.azure.net")

    mock_kv_client.login.assert_called_once()
    mock_kv_clients.save.assert_called_once()


def test_login_without_vault_url(mocker, mock_kv_client, mock_kv_clients):
    inquirer_select_mock = mocker.patch("cli.commands.vaults.login.inquirer.select")
    inquirer_select_mock.return_value.execute.return_value = "https://test.vault.azure.net"

    login(mock_kv_clients)

    mock_kv_client.login.assert_called_once()
    mock_kv_clients.save.assert_called_once()


def test_login_with_no_clients(mock_kv_clients):
    mock_kv_clients.clients = {}
    with pytest.raises(KeyError):
        login(mock_kv_clients, vault_url="https://test.vault.azure.net")
    mock_kv_clients.save.assert_not_called()
