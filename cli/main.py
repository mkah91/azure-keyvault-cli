from pathlib import Path

import click
import toml  # type: ignore

from cli.azkv import azkv as azkv_cmd
from cli.client.keyvault_client import KeyVaultClient, KeyVaultClientSettings
from cli.commands.check import check as check_cmd
from cli.commands.show import show_list

pyproject_file = Path(__file__).parent.parent / "pyproject.toml"
version = toml.load(pyproject_file)["tool"]["poetry"]["version"]


@click.group(invoke_without_command=True, no_args_is_help=True)
@click.version_option(version)
@click.pass_context
@click.option("--reset-vault-url", is_flag=True, default=False, help="Reset Vault URL")
@click.option("--reset-login", is_flag=True, default=False, help="Reset login information")
@click.option("-r", "--reset", is_flag=True, default=False, help="Reset all settings")
def azkv(ctx, reset_vault_url, reset_login, reset):
    try:
        settings = KeyVaultClientSettings()
        try:
            settings.load()
        except (FileNotFoundError, KeyError):
            pass
        if reset_vault_url or reset:
            settings.vault_url = None
        if reset_login or reset:
            settings.auth_record = None
            settings.last_login_time = None
        settings.save()

        client = KeyVaultClient(settings)

        ctx.obj = client
        azkv_cmd(ctx)
    except Exception as e:
        click.secho("Unexpected error", fg="bright_red")
        click.secho(f"Error was:\n{e}", fg="red")


@azkv.command()
@click.argument("name", required=False)
@click.pass_obj
def show(client, name):
    try:
        show_list(client, name)
    except Exception as e:
        click.secho("Unexpected error", fg="bright_red")
        click.secho(f"Error was:\n{e}", fg="red")


@azkv.command()
@click.pass_obj
def check(client):
    try:
        check_cmd(client)
    except Exception as e:
        click.secho("Unexpected error", fg="bright_red")
        click.secho(f"Error was:\n{e}", fg="red")


if __name__ == "__main__":
    azkv()
