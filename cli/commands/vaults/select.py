from cli.commands.common import vaults_blade


class VaultsNotFoundError(Exception):
    pass


def select(clients, enable_all=False):
    if enable_all:
        for client in clients.clients.values():
            client.is_active = True
        return
    if len(clients.clients) == 0:
        raise VaultsNotFoundError("No vaults found. Please add a vault first.")
    vaults_blade(clients, instruction="(Use 'space' to toggle, 'enter' to submit)")
