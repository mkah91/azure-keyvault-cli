from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Footer,
    Markdown,
)


class SecretView(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def __init__(self) -> None:
        self._name = "secret_name"
        self._value = "secret_value"
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Footer()
        yield SecretViewItem()

    def update_secret_view_item(self, secret, vault):
        self._name = secret.name
        self._value = vault.get_secret(secret.name).value

    def _on_screen_resume(self) -> None:
        secret_view_item = self.query_one(SecretViewItem)
        secret_view_item.value = self._value
        secret_view_item.key = self._name
        secret_view_item.show()
        return super()._on_screen_resume()


SECRET_MARKDOWN = """\
# {key}

{value}

| Name            | Type   | Default | Description                        |
| --------------- | ------ | ------- | ---------------------------------- |
| `show_header`   | `bool` | `True`  | Show the table header              |
| `fixed_rows`    | `int`  | `0`     | Number of fixed rows               |
| `fixed_columns` | `int`  | `0`     | Number of fixed columns            |
| `zebra_stripes` | `bool` | `False` | Display alternating colors on rows |
| `header_height` | `int`  | `1`     | Height of header row               |
| `show_cursor`   | `bool` | `True`  | Show a cell cursor                 |
"""
# TODO: add expiration date
# TODO: Add short cut to copy to clipboard
# TODO: Add copy to clipboard button


class SecretViewItem(Markdown):
    key: str
    value: str

    def show(self) -> None:
        self.update(SECRET_MARKDOWN.format(name=self.key, value=self.value))
        self.add_class("visible")

    def hide(self) -> None:
        self.remove_class("visible")
