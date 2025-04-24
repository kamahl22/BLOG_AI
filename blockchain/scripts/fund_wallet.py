from blockchain.transactions import send_algo

if __name__ == "__main__":
    sender = input("Enter sender address: ")
    receiver = input("Enter receiver address: ")
    amount = int(input("Enter amount in microAlgos: "))
    private_key = input("Enter sender private key: ")
    txid = send_algo(sender, receiver, amount, private_key)
    print(f"Transaction ID: {txid}")
