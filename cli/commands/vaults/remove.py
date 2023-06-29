from InquirerPy import inquirer
from InquirerPy.base.control import Choice


def remove(clients, vault_url=None):
    if not vault_url:
        choices = []
        for client in clients.clients.values():
            choices.append(Choice(value=client.vault_url, enabled=True))
        vault_url = inquirer.select(
            message="Select vault to remove:",
            choices=choices,
            validate=lambda v: len(v) >= 1,
            invalid_message="You must select a vault to remove",
        ).execute()
    else:
        if vault_url not in clients.clients:
            raise KeyError(f"Vault {vault_url} not found")
    proceed = inquirer.confirm(
        message="Are you sure you want to remove this vault?", default=False
    ).execute()
    if proceed:
        clients.remove_client(clients.clients[vault_url])
