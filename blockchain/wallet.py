from algosdk import account, mnemonic

def create_wallet():
    private_key, address = account.generate_account()
    mnemonic_phrase = mnemonic.from_private_key(private_key)
    return {"address": address, "private_key": private_key, "mnemonic": mnemonic_phrase}

def recover_wallet(mnemonic_phrase):
    private_key = mnemonic.to_private_key(mnemonic_phrase)
    address = account.address_from_private_key(private_key)
    return {"address": address, "private_key": private_key}
