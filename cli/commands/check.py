from datetime import datetime, timezone, timedelta

import click

from cli.commands.show import get_secret_list

DAYS_BEFORE_EXPIRATION = 15

def check(settings):
    secrets = get_secret_list(settings.client)
    def expired(s):
        if s.expires_on is None:
            return False
        secrets.remove(s)
        return s.expires_on < datetime.now(timezone.utc)
    def soon_expired(s):
        if s.expires_on is None:
            return False
        secrets.remove(s)
        return s.expires_on < datetime.now(timezone.utc) + timedelta(days=DAYS_BEFORE_EXPIRATION)
    expired_secrets = list(filter(expired, secrets))
    soon_expired_secrets = list(filter(soon_expired, secrets))
    if len(expired_secrets) > 0:
        click.secho("Expired secrets:", fg="bright_red")
        for s in expired_secrets:
            click.secho(f"  {s.name}", fg="bright_red")
    if len(soon_expired_secrets) > 0:
        click.secho("Soon to expire secrets:", fg="bright_yellow")
        for s in soon_expired_secrets:
            click.secho(f"  {s.name}", fg="bright_yellow")
    if len(secrets) > 0:
        click.secho("Not expired secrets:", fg="bright_green")
        for s in secrets:
            click.secho(f"  {s.name}", fg="bright_green")
