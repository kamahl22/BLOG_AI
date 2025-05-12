from algosdk import account, mnemonic

def create_wallet():
    private_key, address = account.generate_account()
    print("Address:", address)
    print("Mnemonic:", mnemonic.from_private_key(private_key))

if __name__ == "__main__":
    create_wallet()