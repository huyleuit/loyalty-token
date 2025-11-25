import os, json, time
from pathlib import Path
from dotenv import load_dotenv
from ape import project, accounts

load_dotenv()

DEPLOY_FILE = Path("deployments/sepolia.json")
DEPLOY_FILE.parent.mkdir(parents=True, exist_ok=True)

def save_deployments(token_addr: str, manager_addr: str):
    data = {
        "chainId": 11155111,  # Sepolia
        "contracts": {
            "LoyaltyToken": {"address": token_addr},
            "LoyaltyManager": {"address": manager_addr},
        },
    }
    DEPLOY_FILE.write_text(json.dumps(data, indent=2))

def main():
    owner = accounts.load("sepolia-owner")

    # Deploy token
    token = owner.deploy(project.LoyaltyToken, "Loyalty Token", "LTT", 18)
    print(f"✔ LoyaltyToken deployed to: {token.address}")
    time.sleep(2)

    # Deploy manager
    manager = owner.deploy(project.LoyaltyManager, token.address)
    print(f"✔ LoyaltyManager deployed to: {manager.address}")
    time.sleep(2)

    # Chuyển quyền (minter/owner) cho manager
    token.set_owner(manager.address, sender=owner)
    print("✔ Token ownership transferred to Manager contract.")

    # Xác nhận lại nếu token có hàm owner()
    try:
        print("ℹ Current token owner:", token.owner())
    except Exception:
        pass

    # Lưu địa chỉ để dùng lại
    save_deployments(token.address, manager.address)
    print(f"📝 Saved to {DEPLOY_FILE}")