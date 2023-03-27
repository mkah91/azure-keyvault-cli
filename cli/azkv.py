from azure.core.exceptions import ClientAuthenticationError
import click
from InquirerPy import inquirer
from urllib.parse import urlparse


def azkv(ctx):
    client = ctx.obj
    if client.settings.vault_url is None:
        client.settings.vault_url = inquirer.text(
            message="Enter Vault URL:",
            validate=is_valid_url,
            invalid_message="Input must be a valid url",
            filter=lambda x: x.strip('"').strip("'").strip(),
        ).execute()
    try:
        client.login()
    except ClientAuthenticationError as e:
        click.secho("Authentication error", fg="bright_red")
        click.secho(f"Error was:\n{e}", fg="red")


def is_valid_url(url):
    try:
        url = url.strip('"').strip("'").strip()
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False
