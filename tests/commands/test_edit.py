import click
import pytest

from cli.client.keyvault_client import (
    ClientNotInitializedError,
    KeyVaultClient,
    Secret,
    SecretNotFoundError,
    SecretRequestError,
)
from cli.client.keyvault_clients import KeyVaultClients
from cli.commands.edit import edit_list, edit_secret


@pytest.fixture
def mock_kv_client(mocker):
    mock_client = mocker.MagicMock(spec=KeyVaultClient)
    mock_client.get_secret.return_value = Secret(
        name="test_secret", value="test_value", expires_on=None
    )
    return mock_client


@pytest.fixture
def mock_kv_clients(mocker, mock_kv_client):
    mock_clients = mocker.MagicMock(spec=KeyVaultClients)
    mock_clients.clients = {"https://test.vault.azure.net": mock_kv_client}
    return mock_clients


def test_edit_secret_with_existing_secret(mocker, mock_kv_client):
    # Arrange
    click_secho_spy = mocker.spy(click, "secho")
    mocker.patch("click.edit", return_value="new_value")
    mock_kv_client.set_secret.return_value = None

    # Act
    edit_secret(mock_kv_client, "test_secret")

    # Assert
    mock_kv_client.get_secret.assert_called_once_with("test_secret")
    mock_kv_client.set_secret.assert_called_once_with(
        Secret(name="test_secret", value="new_value", expires_on=None)
    )
    click_secho_spy.assert_called_with("new_value", fg="blue")


def test_edit_secret_with_nonexistent_secret(mocker, mock_kv_client):
    # Arrange
    click_secho_spy = mocker.spy(click, "secho")
    mock_kv_client.get_secret.side_effect = SecretNotFoundError("Secret not found")

    # Act
    with pytest.raises(SystemExit):
        edit_secret(mock_kv_client, "nonexistent_secret")

    # Assert
    mock_kv_client.get_secret.assert_called_once_with("nonexistent_secret")
    click_secho_spy.assert_called_with("Secret does not exist!", fg="bright_red", err=True)


def test_edit_secret_with_request_error(mocker, mock_kv_client):
    # Arrange
    click_secho_spy = mocker.spy(click, "secho")
    mock_kv_client.get_secret.side_effect = SecretRequestError("Error getting secret")

    # Act
    with pytest.raises(SystemExit):
        edit_secret(mock_kv_client, "test_secret")

    # Assert
    mock_kv_client.get_secret.assert_called_once_with("test_secret")
    click_secho_spy.assert_has_calls(
        [
            mocker.call("Error getting the secret!", fg="bright_red", err=True),
            mocker.call("Error was:\nError getting secret", fg="red", err=True),
        ]
    )


def test_edit_secret_with_client_not_initialized_error(mocker, mock_kv_client):
    # Arrange
    click_secho_spy = mocker.spy(click, "secho")
    mock_kv_client.get_secret.side_effect = ClientNotInitializedError("Client not initialized")

    # Act
    with pytest.raises(SystemExit):
        edit_secret(mock_kv_client, "test_secret")

    # Assert
    mock_kv_client.get_secret.assert_called_once_with("test_secret")
    click_secho_spy.assert_called_with("Client not initialized!", fg="bright_red", err=True)


def test_edit_list_with_existing_secret(mocker, mock_kv_clients):
    # Arrange
    mocker.patch(
        "cli.commands.edit.secret_selection",
        return_value=("https://test.vault.azure.net", "test_secret"),
    )
    mocker.patch("click.edit", return_value="new_value")
    click_secho_spy = mocker.spy(click, "secho")

    # Act
    edit_list(mock_kv_clients)

    # Assert
    mock_kv_clients.clients["https://test.vault.azure.net"].get_secret.assert_called_once_with(
        "test_secret"
    )
    mock_kv_clients.clients["https://test.vault.azure.net"].set_secret.assert_called_once_with(
        Secret(name="test_secret", value="new_value", expires_on=None)
    )
    click_secho_spy.assert_has_calls(
        [
            mocker.call("New value:", fg="bright_blue"),
            mocker.call("new_value", fg="blue"),
        ]
    )
