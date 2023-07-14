from InquirerPy import inquirer
from InquirerPy.base.control import Choice


def login(clients, vault_url=None):
    if not vault_url:
        choices = []
        for client in clients.clients.values():
            choices.append(Choice(value=client.vault_url, enabled=True))
        vault_url = inquirer.select(
            message="Select vault to login:",
            choices=choices,
            validate=lambda v: len(v) >= 1,
            invalid_message="At least one vault must be selected",
        ).execute()
    try:
        clients.clients[vault_url].login(force_reauth=True)
        clients.save()
    except KeyError:
        raise KeyError(f"Vault {vault_url} not found")
