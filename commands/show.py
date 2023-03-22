from azure.core.exceptions import ResourceNotFoundError
import click
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
import pyperclip

def show_list(settings):
    secret_properties = settings.client.list_properties_of_secrets()
    secrets = [s.name for s in secret_properties]
    secrets.append(Choice(value=None, name="Exit"))
    choice = inquirer.fuzzy(
        message="Select a secret to show:",
        choices=secrets,
        default=None,
    ).execute()
    if choice:
        secret = settings.client.get_secret(choice)
        click.echo()
        click.secho(secret.value, fg="bright_black")
        pyperclip.copy(secret.value)

def show_secret(settings, name):
    try:
        secret = settings.client.get_secret(name)
        click.echo()
        click.secho(secret.value, fg="bright_black")
        pyperclip.copy(secret.value)
    except ResourceNotFoundError:
        click.secho("Secret does not exist!", fg="red", err=True)