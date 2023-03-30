import sys

import click
import pyperclip  # type: ignore
from InquirerPy import inquirer

from cli.client.keyvault_client import (ClientNotInitializedError,
                                        KeyVaultClient, SecretNotFoundError,
                                        SecretRequestError)


def show_list(kv: KeyVaultClient):
    try:
        secrets = kv.get_secrets()
        secret_names = [s.name for s in secrets]
        if not secret_names:
            click.secho("No secrets found.", fg="bright_white")
            sys.exit(0)
        choice = inquirer.fuzzy(
            message="Select a secret to show:",
            choices=secret_names,
            default=None,
        ).execute()
        if choice:
            show_secret(kv, choice)
    except SecretRequestError as e:
        click.secho("Error listing the secrets!", fg="bright_red", err=True)
        click.secho(f"Error was:\n{e}", fg="red", err=True)
        sys.exit(1)
    except ClientNotInitializedError:
        click.secho("Client not initialized!", fg="bright_red", err=True)
        sys.exit(1)


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
        pyperclip.copy(secret.value)
        click.secho("Secret copied to clipboard!", fg="bright_blue")
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
