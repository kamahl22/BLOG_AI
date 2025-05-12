from algosdk.v2client import algod
from config import ALGOD_ADDRESS, ALGOD_TOKEN

def get_algod_client():
    return algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)