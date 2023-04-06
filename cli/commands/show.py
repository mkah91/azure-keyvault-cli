import sys

import click
import pyperclip  # type: ignore

from cli.client.keyvault_client import (
    ClientNotInitializedError,
    KeyVaultClient,
    SecretNotFoundError,
    SecretRequestError,
)
from cli.client.keyvault_clients import KeyVaultClients
from cli.commands.common import secret_selection


def show_list(vs: KeyVaultClients, name: str = None):
    (vault_url, secret) = secret_selection(vs, name)
    show_secret(vs.clients[vault_url], secret)


def show_secret(kv: KeyVaultClient, name: str):
    try:
        secret = kv.get_secret(name)
        if secret.expires_on:
            expires_color = "bright_white"
            if secret.is_expired():
                expires_color = "red"
            elif secret.is_soon_expired():
                expires_color = "yellow"
            click.secho(f"Expires: {secret.expires_on}", fg=expires_color)
        click.echo()
        click.secho(secret.value, fg="bright_white")
        click.echo()
        try:
            pyperclip.copy(secret.value)
            click.secho("Secret copied to clipboard!", fg=(97, 175, 239))
        except pyperclip.PyperclipException:
            pass
    except SecretNotFoundError:
        click.secho("Secret does not exist!", fg="bright_red", err=True)
        sys.exit(1)
    except SecretRequestError as e:
        click.secho("Error getting the secret!", fg="bright_red", err=True)
        click.secho(f"Error was:\n{e}", fg="bright_red", err=True)
        sys.exit(1)
    except ClientNotInitializedError:
        click.secho("Client not initialized!", fg="bright_red", err=True)
        sys.exit(1)
