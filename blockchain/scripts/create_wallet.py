from blockchain.wallet import create_wallet

if __name__ == "__main__":
    wallet = create_wallet()
    print(f"Address: {wallet['address']}")
    print(f"Mnemonic: {wallet['mnemonic']}")
    print("Store the mnemonic securely!")
