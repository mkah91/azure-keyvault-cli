from InquirerPy import inquirer

from cli.client.keyvault_clients import KeyVaultClients


def azkv(ctx, reset=False):
    vaults = KeyVaultClients()
    vaults.load()
    ctx.obj = vaults
    if reset:
        proceed = inquirer.confirm(
            message="Are you sure you want to reset all settings?", default=False
        ).execute()
        if proceed:
            vaults.reset()
