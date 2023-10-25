from typing import List

from app.secret_view import SecretView
from app.start_view import StartView
from textual.app import App

from cli.client.keyvault_clients import KeyVaultClients
from cli.client.keyvault_secret import Secret

# TODO: Error Handling for Firewall Issue
# TODO: refactor to reuse components
# TODO: make vaults selection work
# TODO: Make it look good (include information like expires into the view, make it colored)
# TODO: Add Buttons to go back and copy secret
# TODO: make search possible


class AzkvApp(App):
    CSS_PATH = "../app/app.tcss"

    SCREENS = {
        "start_view": StartView,
        "secret_view": SecretView,
    }

    vaults: KeyVaultClients
    secrets: List[Secret]

    def on_mount(self):
        self.vaults = KeyVaultClients()
        self.vaults.load()
        for vault in self.vaults.clients.values():
            vault.login()
        self.vaults.save()
        self.push_screen("start_view")
