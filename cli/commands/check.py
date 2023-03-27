import click
import sys

from azure.core.exceptions import HttpResponseError
from cli.clients.keyvault_client import KeyVaultClient, ClientNotInitializedError


def check(kv: KeyVaultClient):
    try:
        secrets = kv.get_secrets()
        expired_secrets = [s for s in secrets if s.is_expired()]
        soon_expired_secrets = [s for s in secrets if s.is_soon_expired()]
        if len(expired_secrets) > 0:
            click.secho("Expired secrets:", fg="bright_red")
            for s in expired_secrets:
                click.secho(f"  {s.name}", fg="bright_red")
        if len(soon_expired_secrets) > 0:
            click.secho("Soon to expire secrets:", fg="bright_yellow")
            for s in soon_expired_secrets:
                click.secho(f"  {s.name}", fg="bright_yellow")
        if len(expired_secrets) == 0 and len(soon_expired_secrets) == 0:
            click.secho("No expired secrets found!", fg="bright_green")
    except HttpResponseError as e:
        click.secho("Error listing the secrets!", fg="bright_red", err=True)
        click.secho(f"Error was:\n{e}", fg="red", err=True)
        sys.exit(1)
    except ClientNotInitializedError:
        click.secho("Client not initialized!", fg="bright_red", err=True)
        sys.exit(1)