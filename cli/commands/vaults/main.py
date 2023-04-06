import click

from cli.commands.vaults.add import add as add_cmd
from cli.commands.vaults.login import login as login_cmd
from cli.commands.vaults.remove import remove as remove_cmd
from cli.commands.vaults.select import VaultsNotFoundError
from cli.commands.vaults.select import select as select_cmd


@click.command()
@click.option("--vault-url", required=False, help="URL of the Key Vault")
@click.pass_obj
def add(vaults, vault_url):
    """Add a new vault"""
    add_cmd(vaults, vault_url)


@click.command()
@click.option("--enable-all", is_flag=True, default=False, help="Enable all vaults")
@click.pass_obj
def select(vaults, enable_all):
    """List and select vaults"""
    try:
        select_cmd(vaults, enable_all)
    except VaultsNotFoundError:
        ctx = click.get_current_context()
        click.secho("No vaults found. Please add a vault first.", fg="bright_yellow")
        click.echo()
        with click.get_current_context() as ctx:
            click.echo(ctx.parent.get_help())


@click.command()
@click.option("--vault-url", required=False, help="URL of the Key Vault")
@click.pass_obj
def login(vaults, vault_url):
    """Login to a vault"""
    login_cmd(vaults, vault_url)


@click.command()
@click.option("--vault-url", required=False, help="URL of the Key Vault")
@click.pass_obj
def remove(vaults, vault_url):
    """Remove a vault"""
    remove_cmd(vaults, vault_url)
