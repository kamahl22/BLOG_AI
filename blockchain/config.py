import os
from dotenv import load_dotenv

load_dotenv()

ALGORAND_NODE = os.getenv("ALGORAND_NODE", "https://testnet-api.algonode.cloud")
ALGORAND_TOKEN = os.getenv("ALGORAND_TOKEN", "")
ALGORAND_INDEXER = os.getenv("ALGORAND_INDEXER", "https://testnet-idx.algonode.cloud")
