import pytest

from cli.client.keyvault_client import KeyVaultClient
from cli.client.keyvault_clients import KeyVaultClients
from cli.commands.vaults.select import VaultsNotFoundError, select


@pytest.fixture
def mock_kv_client(mocker):
    mock_client = mocker.MagicMock(spec=KeyVaultClient)
    mock_client.vault_url = "https://test.vault.azure.net"
    mock_client.is_active = False
    return mock_client


@pytest.fixture
def mock_kv_clients(mocker, mock_kv_client):
    mock_clients = mocker.MagicMock(spec=KeyVaultClients)
    mock_clients.clients = {
        "https://test.vault.azure.net": mock_kv_client,
        "https://test.vault2.azure.net": mock_kv_client,
    }
    return mock_clients


def test_select(mocker, mock_kv_clients):
    vaults_blade_mock = mocker.patch("cli.commands.vaults.select.vaults_blade")
    select(mock_kv_clients)

    vaults_blade_mock.assert_called_once()


def test_select_with_no_clients(mock_kv_clients):
    mock_kv_clients.clients = {}
    with pytest.raises(VaultsNotFoundError):
        select(mock_kv_clients)
