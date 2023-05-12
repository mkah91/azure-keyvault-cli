from urllib.parse import urlparse

from InquirerPy import inquirer

from cli.client.keyvault_client import KeyVaultClient


def add(clients, vault_url=None):
    if not vault_url:
        vault_url = inquirer.text(
            message="Enter Vault URL:",
            validate=is_valid_url,
            invalid_message="Input must be a valid url",
            filter=lambda x: x.strip('"').strip("'").strip(),
        ).execute()
    kv = KeyVaultClient(vault_url)
    kv.login()
    clients.add_client(kv)


def is_valid_url(url):
    try:
        url = url.strip('"').strip("'").strip()
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False
