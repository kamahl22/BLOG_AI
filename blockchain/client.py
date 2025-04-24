from algosdk.v2client import algod, indexer
from .config import ALGORAND_NODE, ALGORAND_TOKEN, ALGORAND_INDEXER

def get_algod_client():
    headers = {"X-API-Key": ALGORAND_TOKEN} if ALGORAND_TOKEN else {}
    return algod.AlgodClient(ALGORAND_TOKEN, ALGORAND_NODE, headers)

def get_indexer_client():
    headers = {"X-API-Key": ALGORAND_TOKEN} if ALGORAND_TOKEN else {}
    return indexer.IndexerClient("", ALGORAND_INDEXER, headers)
