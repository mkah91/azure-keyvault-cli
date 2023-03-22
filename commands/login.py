import os
import sys
from azure.identity import InteractiveBrowserCredential, TokenCachePersistenceOptions


def login(auth_record_file):
    credential = InteractiveBrowserCredential(
        cache_persistence_options=TokenCachePersistenceOptions(
            cache_persistence_options=TokenCachePersistenceOptions(
                name="azure-keyvault-cli")))
    record = credential.authenticate()
    record_json = record.serialize()
    with open(auth_record_file, "w") as f:
        f.write(record_json)