import sys

import click

from cli.client.keyvault_client import (
    ClientNotInitializedError,
    KeyVaultClient,
    Secret,
    SecretNotFoundError,
    SecretRequestError,
)
from cli.client.keyvault_clients import KeyVaultClients
from cli.commands.common import secret_selection


def edit_list(vs: KeyVaultClients, name: str = None):
    (kv, secret) = secret_selection(vs, name)
    edit_secret(kv, secret)


def edit_secret(kv: KeyVaultClient, name: str):
    try:
        secret = kv.get_secret(name)
        click.secho(f"Editing secret '{secret.name}':", fg="bright_blue")
        click.secho(f"Value: {secret.value}", fg="bright_blue")
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
    except ClientNotInitializedError:
        click.secho("Client not initialized!", fg="bright_red", err=True)
        sys.exit(1)
