from algosdk.v2client import algod
from algosdk.future import transaction
from algosdk import account, mnemonic
import os
from dotenv import load_dotenv

load_dotenv()

ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""  # No token needed for algonode
ASA_ID = 737897145

# Load account info
mnemonic_phrase = os.getenv("WALLET_MNEMONIC")
private_key = mnemonic.to_private_key(mnemonic_phrase)
address = account.address_from_private_key(private_key)

client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

params = client.suggested_params()

txn = transaction.AssetTransferTxn(
    sender=address,
    sp=params,
    receiver=address,
    amt=0,
    index=ASA_ID,
)

signed_txn = txn.sign(private_key)
tx_id = client.send_transaction(signed_txn)
print(f"Sent opt-in transaction with txID: {tx_id}")