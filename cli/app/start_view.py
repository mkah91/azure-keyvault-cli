from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Checkbox,
    Footer,
    Label,
    ListItem,
    ListView,
    TabbedContent,
    TabPane,
)

from cli.client.keyvault_client import KeyVaultClient
from cli.client.keyvault_secret import Secret


class StartView(Screen):
    BINDINGS = [
        ("l", "show_tab('secrets')", "Secrets List"),
        ("v", "show_tab('vaults')", "Vaults Selection"),
    ]

    def compose(self) -> ComposeResult:
        yield Footer()
        with TabbedContent(name="tabs"):
            with TabPane("Secrets List", id="secrets"):
                yield SecretList()
            with TabPane("Vaults Selection", id="vaults"):
                for vault in self.app.vaults.clients.values():
                    yield Checkbox(vault.vault_url, vault.is_active, name=vault.vault_url)

    def action_show_tab(self, tab: str) -> None:
        self.get_child_by_type(TabbedContent).active = tab

    def on_tabbed_content_tab_activated(self, event):
        if event.tab.id == "secrets":
            secrets_list = self.query_one(ListView).focus()
            secrets_list.update_secrets()

    def on_list_view_selected(self, event: ListView.Selected):
        secrets = self.query(SecretItem).nodes
        secret = list(filter(lambda node: node.id == event.item.id, secrets))[0]
        self.app.push_screen("secret_view")
        secret_screen = self.app.children[0]
        secret_screen.update_secret_view_item(secret.secret, secret.vault)

    def on_checkbox_changed(self, event):
        vault_url = event.checkbox.name
        self.app.vaults.clients[vault_url].is_active = event.checkbox.value
        self.app.vaults.save()


class SecretList(ListView):
    def update_secrets(self):
        secrets_dict = self.app.vaults.run_command("get_secrets")
        # items = []
        self.clear()
        for vault_url, secrets in secrets_dict.items():
            for secret in secrets:
                self.append(SecretItem(secret, self.app.vaults.clients[vault_url]))
        # self.extend(*items)


class SecretItem(ListItem):
    def __init__(self, secret: Secret, vault: KeyVaultClient) -> None:
        super().__init__(id=secret.name)
        self.secret = secret
        self.vault = vault

    def compose(self) -> ComposeResult:
        yield Label(self.secret.name)
