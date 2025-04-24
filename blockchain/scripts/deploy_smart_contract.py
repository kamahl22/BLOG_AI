from algosdk import transaction
from blockchain.client import get_algod_client

def deploy_contract(approval_program, clear_program, creator, private_key):
    client = get_algod_client()
    params = client.suggested_params()
    app_create_txn = transaction.ApplicationCreateTxn(
        sender=creator,
        sp=params,
        on_complete=transaction.OnComplete.NoOpOC,
        approval_program=approval_program,
        clear_program=clear_program,
        global_schema=transaction.StateSchema(num_uints=1, num_byte_slices=1),
        local_schema=transaction.StateSchema(num_uints=0, num_byte_slices=0)
    )
    signed_txn = app_create_txn.sign(private_key)
    txid = client.send_transaction(signed_txn)
    return txid

if __name__ == "__main__":
    print("Deploy smart contract: TBD")
