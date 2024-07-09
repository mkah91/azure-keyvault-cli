"""Find and print secrets that match substring"""
import sys

import click

from cli.client.keyvault_client import (
    ClientNotInitializedError,
    KeyVaultClient,
    SecretRequestError,
)


def find_secret(kv: KeyVaultClient, name: str = None):
    """Find and print secrets that match substring"""
    try:
        secrets = kv.get_secrets()
        secret_names = [s.name for s in secrets]
        if not secret_names:
            click.secho("No secrets found.", fg="bright_white")
            sys.exit(0)
        print("\n".join(s for s in secret_names if name.lower() in s.lower()))
    except SecretRequestError as err_msg:
        click.secho("Error finding secrets!", fg="bright_red", err=True)
        click.secho(f"Error was:\n{err_msg}", fg="red", err=True)
        sys.exit(1)
    except ClientNotInitializedError:
        click.secho("Client not initialized!", fg="bright_red", err=True)
        sys.exit(1)
