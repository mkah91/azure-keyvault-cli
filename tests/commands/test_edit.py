import pytest

from cli.client.keyvault_client import (
    ClientNotInitializedError,
    KeyVaultClient,
    SecretNotFoundError,
    SecretRequestError,
)
from cli.client.keyvault_secret import Secret
from cli.commands.edit import edit_list, edit_secret


@pytest.fixture
def kv_client_mock(mocker):
    return mocker.MagicMock(spec=KeyVaultClient)


def test_edit_list_with_secrets(mocker, kv_client_mock):
    secret_mock_1 = mocker.MagicMock()
    secret_mock_1.name = "secret1"
    secret_mock_1.value = "value1"
    secret_mock_2 = mocker.MagicMock()
    secret_mock_2.name = "secret2"
    secret_mock_2.value = "value2"
    kv_client_mock.get_secrets.return_value = [secret_mock_1, secret_mock_2]
    inquirer_mock = mocker.patch("InquirerPy.inquirer.fuzzy")
    inquirer_mock.return_value.execute.return_value = "secret1"
    edit_secret_mock = mocker.patch("cli.commands.edit.edit_secret")

    edit_list(kv_client_mock)

    inquirer_mock.assert_called_with(
        message="Select a secret to edit:", choices=["secret1", "secret2"], default=None
    )

    inquirer_mock.return_value.execute.assert_called_once()
    edit_secret_mock.assert_called_once_with(kv_client_mock, "secret1")


def test_edit_list_with_no_secrets(mocker, kv_client_mock, capsys):
    kv_client_mock.get_secrets.return_value = []

    with pytest.raises(SystemExit):
        edit_list(kv_client_mock)

    captured = capsys.readouterr()
    assert captured.out.strip() == "No secrets found."
    assert captured.err == ""


def test_edit_list_with_matching_secret(mocker, kv_client_mock):
    secret_mock_1 = mocker.MagicMock()
    secret_mock_1.name = "secret1"
    secret_mock_1.value = "value1"
    secret_mock_2 = mocker.MagicMock()
    secret_mock_2.name = "secret2"
    secret_mock_2.value = "value2"
    kv_client_mock.get_secrets.return_value = [secret_mock_1, secret_mock_2]
    inquirer_mock = mocker.patch("InquirerPy.inquirer.fuzzy")
    edit_secret_mock = mocker.patch("cli.commands.edit.edit_secret")

    edit_list(kv_client_mock, "secret1")

    inquirer_mock.assert_not_called()
    edit_secret_mock.assert_called_with(kv_client_mock, "secret1")


@pytest.mark.parametrize(
    "error,expected",
    [
        (SecretRequestError, "Error listing the secrets!\nError was:\nTest error"),
        (ClientNotInitializedError, "Client not initialized!"),
    ],
)
def test_edit_list_with_errors(mocker, kv_client_mock, error, expected, capsys):
    kv_client_mock.get_secrets.side_effect = error("Test error")

    with pytest.raises(SystemExit):
        edit_list(kv_client_mock)

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.strip() == expected


def test_edit_secret(mocker, kv_client_mock):
    secret_mock = Secret(
        name="my_secret_name",
        expires_on=None,
        value="my_secret",
    )
    kv_client_mock.get_secret.return_value = secret_mock
    edit_mock = mocker.patch("click.edit")
    secho_mock = mocker.patch("click.secho")
    edit_mock.return_value = "new_value"

    edit_secret(kv_client_mock, "my_secret_name")

    edit_mock.assert_called_with(secret_mock.value)
    expected_secret = Secret(
        name="my_secret_name",
        expires_on=None,
        value="new_value",
    )
    kv_client_mock.set_secret.assert_called_with(expected_secret)
    secho_mock.assert_has_calls(
        [
            mocker.call(f"Editing secret '{secret_mock.name}':", fg="bright_blue"),
            mocker.call(f"Value: {secret_mock.value}", fg="bright_blue"),
            mocker.call("New value:", fg="bright_blue"),
            mocker.call("new_value", fg="blue"),
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
def test_edit_secret_with_errors(mocker, kv_client_mock, error, expected, capsys):
    kv_client_mock.get_secret.side_effect = error("Test error")

    with pytest.raises(SystemExit):
        edit_secret(kv_client_mock, "my_secret_name")

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.strip() == expected
