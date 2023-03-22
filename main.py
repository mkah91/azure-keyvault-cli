from datetime import datetime, timedelta
import os
from pathlib import Path
import sys

import click
from azure.identity import (
    AuthenticationRecord,
    InteractiveBrowserCredential,
    TokenCachePersistenceOptions,
)
from azure.keyvault.secrets import SecretClient

from commands.show import show_list, show_secret
from commands.login import login as login_cmd

AUTH_RECORD_FILE = "auth_record.json"


class Settings:
    def __init__(self, client):
        self.client = client

@click.group()
@click.pass_context
def azkv(ctx):
    if (vault_url := os.environ.get("AZKV_URL")) is None:
        print("Please set AZKV_URL environment variable")
        sys.exit(1)
    auth_record_path = Path(AUTH_RECORD_FILE)
    auth_record_mtime = datetime.fromtimestamp(auth_record_path.stat().st_mtime)
    if not auth_record_path.exists() or auth_record_mtime < (
        datetime.now() - timedelta(hours=4)
    ):
        print("Please login first")
        sys.exit(1)
    with open(AUTH_RECORD_FILE, "r") as f:
        record_json = f.read()
    record = AuthenticationRecord.deserialize(record_json)
    credential = InteractiveBrowserCredential(
        cache_persistence_options=TokenCachePersistenceOptions(
            name="azure-keyvault-cli"
        ),
        authentication_record=record,
    )
    client = SecretClient(vault_url=vault_url, credential=credential)
    ctx.obj = Settings(client)

@azkv.command()
@click.option(
    "-n", "--name", help="The name of the secret"
)
@click.pass_obj
def show(settings, name):
    if name is not None:
        show_secret(settings, name)
    else:
        show_list(settings)

@azkv.command()
def login():
    login_cmd(AUTH_RECORD_FILE)

if __name__ == "__main__":
    azkv()
