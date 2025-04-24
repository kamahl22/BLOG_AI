from algosdk import transaction
from .client import get_algod_client

def create_asa(creator, total, decimals, asset_name, unit_name, private_key):
    client = get_algod_client()
    params = client.suggested_params()
    txn = transaction.AssetConfigTxn(
        sender=creator,
        sp=params,
        total=total,
        decimals=decimals,
        asset_name=asset_name,
        unit_name=unit_name,
        manager=creator,
        reserve=creator,
        freeze=creator,
        clawback=creator
    )
    signed_txn = txn.sign(private_key)
    txid = client.send_transaction(signed_txn)
    return txid
