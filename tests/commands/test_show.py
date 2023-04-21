import click
import pyperclip  # type: ignore
import pytest

from cli.client.keyvault_client import (
    ClientNotInitializedError,
    KeyVaultClient,
    SecretNotFoundError,
    SecretRequestError,
)
from cli.client.keyvault_clients import KeyVaultClients
from cli.commands.show import show_list, show_secret


@pytest.fixture
def mock_secret(mocker):
    secret = mocker.MagicMock()
    secret.value = "my_secret_value"
    secret.expires_on = "2024-01-01T00:00:00Z"
    secret.is_expired.return_value = False
    secret.is_soon_expired.return_value = False
    return secret


@pytest.fixture
def mock_kv_client(mocker, mock_secret):
    mock_client = mocker.MagicMock(spec=KeyVaultClient)
    mock_client.get_secret.return_value = mock_secret
    return mock_client


@pytest.fixture
def mock_kv_clients(mocker, mock_kv_client):
    mock_clients = mocker.MagicMock(spec=KeyVaultClients)
    mock_clients.clients = {"https://test.vault.azure.net": mock_kv_client}
    return mock_clients


def test_show_list_with_secrets(mocker, mock_kv_clients):
    # Arrange
    mocker.patch(
        "cli.commands.show.secret_selection",
        return_value=("https://test.vault.azure.net", "test_secret"),
    )
    click_secho_spy = mocker.spy(click, "secho")
    mocker.patch("pyperclip.copy")

    # Act
    show_list(mock_kv_clients)

    # Assert
    mock_kv_clients.clients["https://test.vault.azure.net"].get_secret.assert_called_once_with(
        "test_secret"
    )
    click_secho_spy.assert_has_calls(
        [
            mocker.call("Expires: 2024-01-01T00:00:00Z", fg="bright_white"),
            mocker.call("my_secret_value", fg="bright_white"),
            mocker.call("Secret copied to clipboard!", fg=(97, 175, 239)),
        ]
    )


@pytest.mark.parametrize(
    "expired,soon_expired,expected",
    [
        (False, False, "bright_white"),
        (True, False, "red"),
        (False, True, "yellow"),
    ],
)
def test_show_secret(mocker, mock_secret, mock_kv_client, expired, soon_expired, expected):
    # Arrange
    mock_secret.is_expired.return_value = expired
    mock_secret.is_soon_expired.return_value = soon_expired
    pyperclip_copy_mock = mocker.patch("pyperclip.copy")
    click_secho_spy = mocker.spy(click, "secho")

    # Act
    show_secret(mock_kv_client, "secret")

    # Assert
    pyperclip_copy_mock.assert_called_once_with("my_secret_value")
    click_secho_spy.assert_has_calls(
        [
            mocker.call("Expires: 2024-01-01T00:00:00Z", fg=expected),
            mocker.call("my_secret_value", fg="bright_white"),
            mocker.call("Secret copied to clipboard!", fg=(97, 175, 239)),
        ]
    )


@pytest.mark.parametrize(
    "error,expected",
    [
        (SecretRequestError, "Error getting the secret!\nError was:\nTest error"),
        (ClientNotInitializedError, "Client not initialized!"),
        (SecretNotFoundError, "Secret does not exist!"),
    ],
)
def test_show_secret_with_error(mocker, mock_kv_client, capsys, error, expected):
    # Arrange
    mock_kv_client.get_secret.side_effect = error("Test error")
    mocker.patch("pyperclip.copy")

    # Act
    with pytest.raises(SystemExit):
        show_secret(mock_kv_client, "secret")

    # Assert
    captured = capsys.readouterr()
    assert captured.out.strip() == ""
    assert captured.err.strip() == expected


def test_show_secret_with_pyperclip_error(mocker, mock_kv_client):
    # Arrange
    mocker.patch("pyperclip.copy", side_effect=pyperclip.PyperclipException("Test error"))

    try:
        # Act
        show_secret(mock_kv_client, "secret")
    except pyperclip.PyperclipException:
        # Assert
        assert False, "pyperclip copy should not raise an exception"
