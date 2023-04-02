import sys

import click
from InquirerPy import inquirer

from cli.client.keyvault_client import (
    ClientNotInitializedError,
    KeyVaultClient,
    Secret,
    SecretNotFoundError,
    SecretRequestError,
)


def edit_list(kv: KeyVaultClient, name: str = None):
    try:
        secrets = kv.get_secrets()
        secret_names = [s.name for s in secrets]
        if not secret_names:
            click.secho("No secrets found.", fg="bright_white")
            sys.exit(0)
        if name in secret_names:
            edit_secret(kv, name)
        choice = inquirer.fuzzy(
            message="Select a secret to edit:",
            choices=secret_names,
            default=name,
        ).execute()
        if choice:
            edit_secret(kv, choice)
    except SecretRequestError as e:
        click.secho("Error listing the secrets!", fg="bright_red", err=True)
        click.secho(f"Error was:\n{e}", fg="red", err=True)
        sys.exit(1)
    except ClientNotInitializedError:
        click.secho("Client not initialized!", fg="bright_red", err=True)
        sys.exit(1)


def edit_secret(kv: KeyVaultClient, name: str):
    try:
        secret = kv.get_secret(name)
        click.secho(f"Editing secret '{secret.name}':", fg="bright_blue")
        click.secho(f"Value: {secret.value}", fg="blue")
        user_input = click.edit(secret.value)
        if user_input is not None:
            new_secret: Secret = Secret(secret.name, secret.expires_on, user_input.strip())
            click.secho("New value:", fg="bright_blue")
            click.secho(new_secret.value, fg="blue")
            kv.set_secret(new_secret)
    except SecretNotFoundError:
        click.secho("Secret does not exist!", fg="bright_red", err=True)
        sys.exit(1)
    except SecretRequestError as e:
        click.secho("Error getting the secret!", fg="bright_red", err=True)
        click.secho(f"Error was:\n{e}", fg="red", err=True)
        sys.exit(1)
    except ClientNotInitializedError:
        click.secho("Client not initialized!", fg="bright_red", err=True)
        sys.exit(1)
