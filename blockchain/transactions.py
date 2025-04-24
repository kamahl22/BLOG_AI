from algosdk import transaction
from .client import get_algod_client

def send_algo(sender, receiver, amount, private_key, note=""):
    client = get_algod_client()
    params = client.suggested_params()
    txn = transaction.PaymentTxn(sender, params, receiver, amount, note=note.encode())
    signed_txn = txn.sign(private_key)
    txid = client.send_transaction(signed_txn)
    return txid
