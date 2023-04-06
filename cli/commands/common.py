import sys
from typing import Optional, Tuple
from urllib.parse import urlparse

import click
from halo import Halo
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from cli.client.keyvault_client import (
    ClientNotInitializedError,
    KeyVaultClient,
    SecretRequestError,
)
from cli.client.keyvault_clients import KeyVaultClients

CURSOR_UP_ONE = "\x1b[1A"
ERASE_LINE = "\x1b[2K"


def secret_selection(vs: KeyVaultClients, name: str = None) -> Tuple[KeyVaultClient, str]:
    try:
        choice = None
        while not choice:
            choice = secrets_blade(vs, name)
            print(
                CURSOR_UP_ONE + ERASE_LINE, end=""
            )  # erase the last line printed by the inquirer method
            if not choice:
                keybindings = {
                    "skip": [{"key": "left"}],
                }
                vaults_blade(
                    vs,
                    keybindings=keybindings,
                    mandatory=False,
                    instruction="(Use 'space' to toggle, 'enter' to save and 'left arrow' switch to secrets blade without saving)",
                )
            print(
                CURSOR_UP_ONE + ERASE_LINE, end=""
            )  # erase the last line printed by the inquirer method
        return choice
    except SecretRequestError as e:
        click.secho("Error listing the secrets!", fg="bright_red", err=True)
        click.secho(f"Error was:\n{e}", fg="red", err=True)
        sys.exit(1)
    except ClientNotInitializedError:
        click.secho("Client not initialized!", fg="bright_red", err=True)
        sys.exit(1)


def secrets_blade(
    vs: KeyVaultClients, name: str = None
) -> Tuple[Optional[KeyVaultClient], Optional[str]]:
    secret_names = []
    with Halo(text="Loading secrets", spinner="dots"):
        secrets = vs.run_command("get_secrets")
    for vault_url, secrets in secrets.items():
        for s in secrets:
            secret_names.append(
                {
                    "name": f"[{urlparse(vault_url).hostname.split('.', 1)[0]}] {s.name}",
                    "value": (vault_url, s.name),
                }
            )
    keybindings = {
        "skip": [{"key": "right"}],
    }
    choice = inquirer.fuzzy(
        message="Select a secret to show:",
        choices=secret_names,
        default=name,
        keybindings=keybindings,
        mandatory=False,
        instruction="(Use 'enter' to submit and 'right arrow' switch to active vaults blade)",
    ).execute()
    return choice


def vaults_blade(clients, keybindings=None, mandatory=True, instruction=None):
    choices = []
    for client in clients.clients.values():
        choices.append(Choice(value=client.vault_url, enabled=client.is_active))
    active_vaults = inquirer.checkbox(
        message="Select active vaults:",
        choices=choices,
        validate=lambda v: len(v) >= 1,
        invalid_message="At least one vault must be selected",
        instruction=instruction,
        keybindings=keybindings,
        mandatory=mandatory,
    ).execute()
    if not active_vaults:
        return
    for key, vault in clients.clients.items():
        if key in active_vaults:
            vault.is_active = True
        else:
            vault.is_active = False
    clients.save()
