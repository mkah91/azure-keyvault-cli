import pytest

from cli.client.keyvault_client import KeyVaultClient, ClientNotInitializedError, SecretRequestError
from cli.commands.check import check


@pytest.fixture
def mock_kv_client(mocker):
    return mocker.MagicMock(spec=KeyVaultClient)


@pytest.mark.parametrize(
    "expired,soon_expired,expected",
    [
        (False, False, "No expired secrets found!"),
        (True, False, "Expired secrets:\n  secret1\n  secret2"),
        (False, True, "Soon to expire secrets:\n  secret1\n  secret2"),
    ],
)
def test_check_no_expired_or_soon_to_expire_secrets(mocker, mock_kv_client, capsys, expired, soon_expired, expected):
    # Mock the return value of get_secrets to return a list of no expired or soon to expire secrets
    secret1 = mocker.MagicMock(is_expired=lambda: expired, is_soon_expired=lambda: soon_expired)
    secret1.name = "secret1"
    secret2 = mocker.MagicMock(is_expired=lambda: expired, is_soon_expired=lambda: soon_expired)
    secret2.name = "secret2"
    no_expired_secrets = [secret1, secret2]
    mock_kv_client.get_secrets.return_value = no_expired_secrets

    check(mock_kv_client)

    # Capture the output of the function using capsys
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
def test_check_http_response_error(mock_kv_client, capsys, error, expected):
    # Mock the get_secrets method to raise an HttpResponseError
    mock_kv_client.get_secrets.side_effect = error("Test error")

    with pytest.raises(SystemExit):
        check(mock_kv_client)

    # Capture the output of the function using capsys
    captured = capsys.readouterr()
    assert captured.err == expected
