import pytest

from cli.client.keyvault_client import KeyVaultClient
from cli.client.keyvault_clients import KeyVaultClients
from cli.commands.vaults.add import add, is_valid_url


@pytest.fixture
def mock_kv_client(mocker):
    return mocker.MagicMock(spec=KeyVaultClient)


@pytest.fixture
def mock_kv_clients(mocker, mock_kv_client):
    mock_clients = mocker.MagicMock(spec=KeyVaultClients)
    mock_clients.clients = {"https://test.vault.azure.net": mock_kv_client}
    return mock_clients


def test_add_with_vault_url(mocker, mock_kv_clients):
    mock_kv = mocker.patch("cli.commands.vaults.add.KeyVaultClient", autospec=True)

    add(mock_kv_clients, vault_url="https://example.com")

    mock_kv.assert_called_once_with("https://example.com")
    mock_kv_clients.add_client.assert_called_once()


def test_add_without_vault_url(mocker, mock_kv_clients):
    mock_kv = mocker.patch("cli.commands.vaults.add.KeyVaultClient", autospec=True)
    inquirer_text_mock = mocker.patch("cli.commands.vaults.add.inquirer.text")
    inquirer_text_mock.return_value.execute.return_value = "https://example.com"

    add(mock_kv_clients)

    mock_kv.assert_called_once_with("https://example.com")
    mock_kv_clients.add_client.assert_called_once()


def test_is_valid_url():
    assert is_valid_url("https://example.com") is True
    assert is_valid_url("http://example.com") is True
    assert is_valid_url("ftp://example.") is False
    assert is_valid_url("example.com") is False
