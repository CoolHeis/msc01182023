import os
#from eth_utils import address
from web3 import Web3
from dotenv import load_dotenv
from compile import compile_contract

def main():
    load_dotenv()
    abi, bytecode = compile_contract()
    URL_RPC = os.getenv("URL_RPC")
    chain_id = os.getenv("CHAIN_ID")
    print(chain_id)
    print(type(chain_id))
    priv_key = os.getenv("PRIVATE_KEY")

    #connecting to the blockchain
    w3 = Web3(Web3.HTTPProvider(URL_RPC))
    addr = w3.eth.accounts[0]
    print(addr)

    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.get_transaction_count(addr)
    print(nonce)
    # build transaction
    transaction = contract.constructor().build_transaction(
        {
            "chainId": int(chain_id),
            "gasPrice": w3.eth.gas_price,
            "from": addr,
            "nonce": nonce,
        }
    )
    
    # Sign the transaction
    sign_transaction = w3.eth.account.sign_transaction(transaction, private_key=priv_key)
    print("Deploying Contract!")

    # Send the transaction
    transaction_hash = w3.eth.send_raw_transaction(sign_transaction.rawTransaction)
    # Wait for the transaction to be mined, and get the transaction receipt
    print("Waiting for transaction to finish...")
    transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
    print(f"Done! Contract deployed to {transaction_receipt.contractAddress}")

if __name__ == '__main__':
    main()