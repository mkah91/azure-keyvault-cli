from datetime import datetime, timezone

from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
import click
from InquirerPy import inquirer
import pyperclip

def show_list(client):
    secret_names = map(lambda s: s.name, get_secret_list(client))
    choice = inquirer.fuzzy(
        message="Select a secret to show:",
        choices=secret_names,
        default=None,
    ).execute()
    if choice:
        show_secret(client, choice)

def get_secret_list(client): 
    try:
        return list(client.list_properties_of_secrets())
    except HttpResponseError as e:
        click.secho("Error listing the secrets!", fg="bright_red", err=True)
        click.secho(f"Error was:\n{e}", fg="red", err=True)

def show_secret(client, name):
    secret = get_secret(client, name)
    if secret:
        click.secho(f"Secret: {secret.name}", fg="bright_black")
        if secret.properties.expires_on:
            expires_color = "bright_black"
            if secret.properties.expires_on < datetime.now(timezone.utc):
                expires_color = "red"
            click.secho(f"Expires: {secret.properties.expires_on}", fg=expires_color)
        click.echo()
        click.secho(secret.value, fg="bright_black")
        pyperclip.copy(secret.value)

def get_secret(client, name):
    try:
        return client.get_secret(name)
    except ResourceNotFoundError:
        click.secho("Secret does not exist!", fg="bright_red", err=True)
    except HttpResponseError as e:
        click.secho("Error getting the secret!", fg="bright_red", err=True)
        click.secho(f"Error was:\n{e}", fg="red", err=True)
