import os
from flask import Flask, request, jsonify
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Config from .env file
INFURA_URL = os.getenv("INFURA_SEPOLIA_URL")
OWNER_PRIVATE_KEY = os.getenv("OWNER_PRIVATE_KEY")
MANAGER_CONTRACT_ADDRESS = os.getenv("MANAGER_CONTRACT_ADDRESS")
MANAGER_CONTRACT_ABI = '[...]' # Get ABI from build file of Ape

w3 = Web3(Web3.HTTPProvider(INFURA_URL))
owner_account = w3.eth.account.from_key(OWNER_PRIVATE_KEY)

manager_contract = w3.eth.contract(address=MANAGER_CONTRACT_ADDRESS, abi=MANAGER_CONTRACT_ABI)

@app.route('/issue-tokens', methods=['POST'])
def issue_tokens():
    data = request.get_json()
    customer_address = data['customer_address']
    # Example: 1 USD = 1 LTT
    amount_in_wei = w3.to_wei(data['order_value'], 'ether')

    try:
        # Create transaction
        tx = manager_contract.functions.issueTokens(
            w3.to_checksum_address(customer_address),
            amount_in_wei
        ).build_transaction({
            'from': owner_account.address,
            'nonce': w3.eth.get_transaction_count(owner_account.address),
            'gas': 200000,
            'gasPrice': w3.eth.gas_price
        })

        # Sign and send
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=OWNER_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return jsonify({"status": "success", "tx_hash": w3.to_hex(tx_hash)}), 200
    except Exception as e:
        # Encode sensitive information if there is an error
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001)