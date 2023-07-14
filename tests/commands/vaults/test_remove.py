import pytest

from cli.client.keyvault_client import KeyVaultClient
from cli.client.keyvault_clients import KeyVaultClients
from cli.commands.vaults.remove import remove


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


def test_remove_with_vault_url(mocker, mock_kv_clients):
    inquirer_confirm_mock = mocker.patch("cli.commands.vaults.login.inquirer.confirm")
    inquirer_confirm_mock.return_value.execute.return_value = True

    remove(mock_kv_clients, vault_url="https://test.vault.azure.net")

    mock_kv_clients.remove_client.assert_called_once_with(
        mock_kv_clients.clients["https://test.vault.azure.net"]
    )


def test_remove_without_vault_url(mocker, mock_kv_client, mock_kv_clients):
    inquirer_select_mock = mocker.patch("cli.commands.vaults.login.inquirer.select")
    inquirer_select_mock.return_value.execute.return_value = "https://test.vault.azure.net"
    inquirer_confirm_mock = mocker.patch("cli.commands.vaults.login.inquirer.confirm")
    inquirer_confirm_mock.return_value.execute.return_value = True

    remove(mock_kv_clients)

    mock_kv_clients.remove_client.assert_called_once_with(mock_kv_client)


def test_remove_with_negative_confirmation(mocker, mock_kv_client, mock_kv_clients):
    inquirer_select_mock = mocker.patch("cli.commands.vaults.login.inquirer.select")
    inquirer_select_mock.return_value.execute.return_value = "https://test.vault.azure.net"
    inquirer_confirm_mock = mocker.patch("cli.commands.vaults.login.inquirer.confirm")
    inquirer_confirm_mock.return_value.execute.return_value = False

    remove(mock_kv_clients)

    mock_kv_clients.remove_client.assert_not_called()


def test_remove_with_not_existing_vault_url(mock_kv_clients):
    with pytest.raises(KeyError):
        remove(mock_kv_clients, vault_url="invalid-vault-url")
