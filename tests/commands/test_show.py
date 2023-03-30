import pyperclip  # type: ignore
import pytest

from cli.client.keyvault_client import (ClientNotInitializedError,
                                        KeyVaultClient, SecretNotFoundError,
                                        SecretRequestError)
from cli.commands.show import show_list, show_secret


@pytest.fixture
def kv_client_mock(mocker):
    return mocker.MagicMock(spec=KeyVaultClient)

def test_show_list_with_secrets(mocker, kv_client_mock):
    secret_mock_1 = mocker.MagicMock()
    secret_mock_1.name = "secret1"
    secret_mock_2 = mocker.MagicMock()
    secret_mock_2.name = "secret2"
    kv_client_mock.get_secrets.return_value = [secret_mock_1, secret_mock_2]
    inquirer_mock = mocker.patch("InquirerPy.inquirer.fuzzy")
    inquirer_mock.return_value.execute.return_value = "secret1"
    show_secret_mock = mocker.patch("cli.commands.show.show_secret")

    show_list(kv_client_mock)

    inquirer_mock.assert_called_with(message='Select a secret to show:', choices=['secret1', 'secret2'], default=None)
    inquirer_mock.return_value.execute.assert_called_once()
    show_secret_mock.assert_called_once_with(kv_client_mock, "secret1")


def test_show_list_with_no_secrets(mocker, kv_client_mock, capsys):
    kv_client_mock.get_secrets.return_value = []

    with pytest.raises(SystemExit):
        show_list(kv_client_mock)

    captured = capsys.readouterr()
    assert captured.out.strip() == "No secrets found."
    assert captured.err == ""

@pytest.mark.parametrize(
    "error,expected",
    [
        (SecretRequestError, "Error listing the secrets!\nError was:\nTest error"),
        (ClientNotInitializedError, "Client not initialized!"),
    ],
)
def test_show_list_with_error(kv_client_mock, capsys, error, expected):
    kv_client_mock.get_secrets.side_effect = error("Test error")
    
    with pytest.raises(SystemExit):
        show_list(kv_client_mock)

    captured = capsys.readouterr()
    assert captured.out.strip() == ""
    assert captured.err.strip() == expected

@pytest.mark.parametrize(
    "expired,soon_expired,expected",
    [
        (False, False, "bright_white"),
        (True, False, "red"),
        (False, True, "yellow"),
    ],
)
def test_show_secret(mocker, kv_client_mock, expired, soon_expired, expected):
    secret_mock = mocker.MagicMock(value="my_secret", expires_on="someday", is_expired=lambda: expired, is_soon_expired=lambda: soon_expired)
    secret_mock.name = "secret"
    kv_client_mock.get_secret.return_value = secret_mock
    mocker.patch("pyperclip.copy")
    secho_mock = mocker.patch("click.secho")

    show_secret(kv_client_mock, "secret")

    pyperclip.copy.assert_called_once_with("my_secret")
    secho_mock.assert_has_calls([
        mocker.call("Expires: someday", fg=expected),
        mocker.call("my_secret", fg="bright_white"),
        mocker.call("Secret copied to clipboard!", fg="bright_blue")
    ])


@pytest.mark.parametrize(
    "error,expected",
    [
        (SecretRequestError, "Error getting the secret!\nError was:\nTest error"),
        (ClientNotInitializedError, "Client not initialized!"),
        (SecretNotFoundError, "Secret does not exist!"),
    ],
)
def test_show_secret_with_error(kv_client_mock, capsys, error, expected):
    kv_client_mock.get_secret.side_effect = error("Test error")

    with pytest.raises(SystemExit):
        show_secret(kv_client_mock, "secret")

    captured = capsys.readouterr()
    assert captured.out.strip() == ""
    assert captured.err.strip() == expected