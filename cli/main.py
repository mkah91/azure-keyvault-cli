import sys
from pathlib import Path

import click
import toml  # type: ignore

from cli.azkv import azkv as azkv_cmd
from cli.commands.check import check as check_cmd
from cli.commands.edit import edit_list
from cli.commands.show import show_list
from cli.commands.vaults.main import add as vaults_add_cmd
from cli.commands.vaults.main import login as vaults_login_cmd
from cli.commands.vaults.main import remove as vaults_remove_cmd
from cli.commands.vaults.main import select as vaults_select_cmd
from cli.decorators import login

pyproject_file = Path(__file__).parent.parent / "pyproject.toml"
version = toml.load(pyproject_file)["tool"]["poetry"]["version"]


@click.group(invoke_without_command=True, no_args_is_help=True)
@click.version_option(version)
@click.pass_context
@click.option("-r", "--reset", is_flag=True, default=False, help="Reset all settings")
def azkv(ctx, reset):
    """A CLI tool to manage Azure Key Vault secrets"""
    try:
        azkv_cmd(ctx, reset)
    except ValueError:
        click.secho("Resetting due to an invalid settings file.", fg="bright_red")
        click.secho("Please run 'azkv vaults add' to add a new vault.", fg="bright_red")
        click.echo()
        with click.get_current_context() as ctx:
            click.echo(ctx.get_help())
        sys.exit(1)


@azkv.group(no_args_is_help=True)
def vaults():
    """Manage vaults"""


vaults.add_command(vaults_add_cmd)
vaults.add_command(vaults_select_cmd)
vaults.add_command(vaults_login_cmd)
vaults.add_command(vaults_remove_cmd)


@azkv.command()
@click.argument("name", required=False)
@click.pass_obj
@login
def show(vaults, name):
    """List and show secrets"""
    show_list(vaults, name)


@azkv.command()
@click.argument("name", required=False)
@click.pass_obj
@login
def edit(vaults, name):
    """List and edit secrets"""
    edit_list(vaults, name)


@azkv.command()
@click.pass_obj
@login
def check(vaults):
    """Check for expired secrets"""
    check_cmd(vaults)


if __name__ == "__main__":
    try:
        azkv()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        click.secho("Unexpected error", fg="bright_red")
        click.secho(f"Error was:\n{e}", fg="red")
        click.secho("Unexpected error", fg="bright_red")
        click.secho(f"Error was:\n{e}", fg="red")
