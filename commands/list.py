import os

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
import click

def show(settings):
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
