from copy import deepcopy

import pytest
from InquirerPy.base.control import Choice

from cli.client.keyvault_client import KeyVaultClient
from cli.client.keyvault_clients import KeyVaultClients
from cli.commands.common import secret_selection, secrets_blade, vaults_blade


@pytest.fixture
def mock_secret(mocker):
    secret = mocker.MagicMock()
    secret.name = "test_secret"
    secret.value = "test_value"
    return secret


@pytest.fixture
def mock_kv_client(mocker):
    mock_client = mocker.MagicMock(spec=KeyVaultClient)
    mock_client.is_active = False
    mock_client.get_secret.return_value = mock_secret
    return mock_client


@pytest.fixture
def mock_kv_clients(mocker, mock_kv_client):
    mock_clients = mocker.MagicMock(spec=KeyVaultClients)
    mock_kv_client1 = deepcopy(mock_kv_client)
    mock_kv_client1.vault_url = "https://test.vault.azure.net"
    mock_kv_client2 = deepcopy(mock_kv_client)
    mock_kv_client2.vault_url = "https://test2.vault.azure.net"
    mock_clients.clients = {
        mock_kv_client1.vault_url: mock_kv_client1,
        mock_kv_client2.vault_url: mock_kv_client2,
    }
    return mock_clients


def test_secret_selection(mocker, mock_kv_clients):
    # Arrange
    secrets_blade_mock = mocker.patch("cli.commands.common.secrets_blade")
    vaults_blade_mock = mocker.patch("cli.commands.common.vaults_blade")
    secrets_blade_mock.side_effect = [None, "test_secret"]

    # Act
    choice = secret_selection(mock_kv_clients, "test_secret")

    # Assert
    secrets_blade_mock.assert_has_calls(
        [mocker.call(mock_kv_clients, "test_secret"), mocker.call(mock_kv_clients, "test_secret")]
    )
    vaults_blade_mock.assert_called_once()
    assert choice == "test_secret"


def test_secret_selection_does_not_remove_previous_print_when_not_switching_vaults(
    mocker, mock_kv_clients
):
    # Arrange
    print_mock = mocker.patch("builtins.print")
    secrets_blade_mock = mocker.patch("cli.commands.common.secrets_blade")
    mocker.patch("cli.commands.common.vaults_blade")
    secrets_blade_mock.side_effect = ["test_secret"]

    # Act
    secret_selection(mock_kv_clients)

    # Assert
    print_mock.assert_not_called()


def test_secret_selection_remove_previous_print_when_switching_blades(mocker, mock_kv_clients):
    # Arrange
    print_mock = mocker.patch("builtins.print")
    secrets_blade_mock = mocker.patch("cli.commands.common.secrets_blade")
    mocker.patch("cli.commands.common.vaults_blade")
    secrets_blade_mock.side_effect = [None, "test_secret"]

    # Act
    secret_selection(mock_kv_clients)

    # Assert
    print_mock.assert_called_with("\x1b[1A\x1b[2K", end="")
    assert print_mock.call_count == 2


def test_secrets_blade(mocker, mock_kv_clients, mock_secret):
    # Arrange
    inquirer_fuzzy_mock = mocker.patch("cli.commands.common.inquirer.fuzzy")
    mock_kv_clients.run_command.return_value = {"https://test.vault.azure.net": [mock_secret]}
    inquirer_fuzzy_mock.return_value.execute.return_value = (mock_kv_clients, "test_secret")
    secret_names = [
        {"name": "[test] test_secret", "value": ("https://test.vault.azure.net", "test_secret")}
    ]

    # Act
    secrets_blade(mock_kv_clients, "test_secret")

    # Assert
    inquirer_fuzzy_mock.assert_called_once_with(
        message=mocker.ANY,
        choices=secret_names,
        default="test_secret",
        keybindings={"skip": [{"key": "right"}]},
        mandatory=mocker.ANY,
        instruction=mocker.ANY,
    )


def test_vaults_blade(mocker, mock_kv_clients, mock_secret):
    # Arrange
    inquirer_checkbox_mock = mocker.patch("cli.commands.common.inquirer.checkbox")
    inquirer_checkbox_mock.return_value.execute.return_value = ["https://test.vault.azure.net"]

    # Act
    vaults_blade(mock_kv_clients)

    # Arrange
    choices = [
        Choice(value="https://test.vault.azure.net", enabled=False),
        Choice(value="https://test2.vault.azure.net", enabled=False),
    ]
    inquirer_checkbox_mock.assert_called_once_with(
        message=mocker.ANY,
        choices=choices,
        validate=mocker.ANY,
        invalid_message=mocker.ANY,
        instruction=mocker.ANY,
        keybindings=None,
        mandatory=True,
    )
    assert mock_kv_clients.clients["https://test.vault.azure.net"].is_active is True
    assert mock_kv_clients.clients["https://test2.vault.azure.net"].is_active is False
    # kvs = KeyVaultClients({})
    # with patch("cli.commands.secret.inquirer.checkbox") as mock_checkbox:
    #     mock_checkbox.return_value.execute.return_value = ["vault_url"]
    #     vaults_blade(kvs)
    #     mock_checkbox.assert_called_once_with(
    #         message="Select active vaults:",
    #         choices=[],
    #         validate=Mock(),
    #         invalid_message="At least one vault must be selected",
    #         instruction="",
    #         keybindings=None,
    #         mandatory=True,
    #     )#         )
    #     )#         )
