import pytest

from cli.client.keyvault_client import (ClientNotInitializedError,
                                        KeyVaultClient, SecretRequestError)
from cli.commands.check import check


@pytest.fixture
def kv_client_mock(mocker):
    return mocker.MagicMock(spec=KeyVaultClient)


@pytest.mark.parametrize(
    "expired,soon_expired,expected",
    [
        (False, False, "No expired secrets found!"),
        (True, False, "Expired secrets:\n  secret1\n  secret2"),
        (False, True, "Soon to expire secrets:\n  secret1\n  secret2"),
    ],
)
def test_check_with_secrets(
    mocker, kv_client_mock, capsys, expired, soon_expired, expected
):
    secret1 = mocker.MagicMock(is_expired=lambda: expired, is_soon_expired=lambda: soon_expired)
    secret1.name = "secret1"
    secret2 = mocker.MagicMock(is_expired=lambda: expired, is_soon_expired=lambda: soon_expired)
    secret2.name = "secret2"
    no_expired_secrets = [secret1, secret2]
    kv_client_mock.get_secrets.return_value = no_expired_secrets

    check(kv_client_mock)

    captured = capsys.readouterr()
    assert captured.out.strip() == expected
    assert captured.err == ""


@pytest.mark.parametrize(
    "error,expected",
    [
        (SecretRequestError, "Error listing the secrets!\nError was:\nTest error\n"),
        (ClientNotInitializedError, "Client not initialized!\n"),
    ],
)
def test_check_with_error(kv_client_mock, capsys, error, expected):
    kv_client_mock.get_secrets.side_effect = error("Test error")

    with pytest.raises(SystemExit):
        check(kv_client_mock)

    captured = capsys.readouterr()
    assert captured.err == expected
