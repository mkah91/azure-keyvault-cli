import asyncio
from functools import wraps

from cli.commands.vaults.add import add as add_vault


def run_async(f):
    @wraps(f)
    def async_wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return async_wrapper


def login(f):
    @wraps(f)
    def login_wrapper(vaults, **kwargs):
        if not vaults.clients:
            add_vault(vaults)
        vaults.login()
        vaults.save()
        return f(vaults, **kwargs)

    return login_wrapper
