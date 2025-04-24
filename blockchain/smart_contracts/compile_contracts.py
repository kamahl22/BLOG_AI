from algosdk import encoding
from blockchain.client import get_algod_client

def compile_teal(source_code):
    client = get_algod_client()
    compiled = client.compile(source_code)
    return encoding.decode_address(compiled["result"])
