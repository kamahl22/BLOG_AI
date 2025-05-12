from pyteal import *

def approval_program():
    return Approve()

def clear_program():
    return Approve()

if __name__ == "__main__":
    with open("build/escrow_approval.teal", "w") as f:
        f.write(compileTeal(approval_program(), mode=Mode.Application, version=6))

    with open("build/escrow_clear.teal", "w") as f:
        f.write(compileTeal(clear_program(), mode=Mode.Application, version=6))