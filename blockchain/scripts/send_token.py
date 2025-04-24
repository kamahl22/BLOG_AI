from algosdk import transaction
from blockchain.client import get_algod_client

if __name__ == "__main__":
    sender = input("Enter sender address: ")
    receiver = input("Enter receiver address: ")
    asset_id = int(input("Enter TBLOG asset ID: "))
    amount = int(input("Enter amount: "))
    private_key = input("Enter sender private key: ")
    client = get_algod_client()
    params = client.suggested_params()
    txn = transaction.AssetTransferTxn(sender, params, receiver, amount, asset_id)
    signed_txn = txn.sign(private_key)
    txid = client.send_transaction(signed_txn)
    print(f"Transaction ID: {txid}")
