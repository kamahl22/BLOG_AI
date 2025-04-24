from algosdk import account, transaction, mnemonic
from algosdk.v2client import algod
from config import ALGOD_ADDRESS, ALGOD_TOKEN, ASA_ID

def send_token(sender_mnemonic, receiver_address, amount):
    client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
    sender_key = mnemonic.to_private_key(sender_mnemonic)
    sender_address = account.address_from_private_key(sender_key)

    params = client.suggested_params()
    unsigned_txn = transaction.AssetTransferTxn(
        sender=sender_address,
        sp=params,
        receiver=receiver_address,
        amt=int(amount * 1e6),  # Convert to microalgos
        index=ASA_ID,
    )

    signed_txn = unsigned_txn.sign(sender_key)
    tx_id = client.send_transaction(signed_txn)
    print("Transaction ID:", tx_id)

if __name__ == "__main__":
    import sys
    send_token(sys.argv[1], sys.argv[2], float(sys.argv[3]))