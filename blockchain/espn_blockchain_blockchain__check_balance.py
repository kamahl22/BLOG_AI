from algosdk.v2client import algod
from config import ALGOD_ADDRESS, ALGOD_TOKEN
import sys

client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

def check_balance(address):
    account_info = client.account_info(address)
    print("ALGO Balance:", account_info.get("amount") / 1e6, "ALGO")
    assets = account_info.get("assets", [])
    for asset in assets:
        if asset["asset-id"] == 737897145:
            print("TBLOG Balance:", asset["amount"] / 1e6)

if __name__ == "__main__":
    check_balance(sys.argv[1])