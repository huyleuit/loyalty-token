"""
Demo script for IPFS integration with LoyaltyManager contract
Demonstrates uploading metadata, images, and certificates to IPFS
"""

import json
import requests
from pathlib import Path


class PinataIPFS:
    """Helper class to interact with Pinata IPFS service"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.pinata.cloud"
        self.headers = {
            'pinata_api_key': api_key,
            'pinata_secret_api_key': api_secret
        }
    
    def upload_json(self, json_data: dict, name: str) -> str:
        """
        Upload JSON metadata to IPFS
        
        Args:
            json_data: Dictionary to upload
            name: Name for the pinned content
            
        Returns:
            IPFS CID (hash)
        """
        url = f"{self.base_url}/pinning/pinJSONToIPFS"
        
        payload = {
            "pinataContent": json_data,
            "pinataMetadata": {
                "name": name
            }
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        
        result = response.json()
        return result['IpfsHash']
    
    def upload_file(self, file_path: str, name: str) -> str:
        """
        Upload file (image, PDF, etc.) to IPFS
        
        Args:
            file_path: Path to file
            name: Name for the pinned content
            
        Returns:
            IPFS CID (hash)
        """
        url = f"{self.base_url}/pinning/pinFileToIPFS"
        
        with open(file_path, 'rb') as file:
            files = {
                'file': file
            }
            
            metadata = {
                "name": name
            }
            
            response = requests.post(
                url,
                files=files,
                headers=self.headers,
                data={'pinataMetadata': json.dumps(metadata)}
            )
            response.raise_for_status()
            
            result = response.json()
            return result['IpfsHash']
    
    def get_content(self, cid: str) -> requests.Response:
        """
        Retrieve content from IPFS
        
        Args:
            cid: IPFS CID to retrieve
            
        Returns:
            Response object with content
        """
        url = f"https://gateway.pinata.cloud/ipfs/{cid}"
        response = requests.get(url)
        response.raise_for_status()
        return response


def demo_create_reward_metadata():
    """Example: Create reward metadata JSON"""
    
    rewards_metadata = {
        "reward_1": {
            "name": "Voucher giảm giá 10%",
            "description": "Giảm 10% cho đơn hàng tiếp theo",
            "terms": "Áp dụng cho đơn hàng từ 200,000 VNĐ",
            "expiry": "2025-12-31",
            "category": "discount",
            "value_vnd": 0,
            "token_cost": 100
        },
        "reward_2": {
            "name": "Túi tote cao cấp",
            "description": "Túi vải canvas in logo thương hiệu",
            "terms": "Số lượng có hạn",
            "expiry": "2026-06-30",
            "category": "merchandise",
            "value_vnd": 150000,
            "token_cost": 500
        },
        "reward_3": {
            "name": "iPhone 15 Pro Max",
            "description": "Điện thoại cao cấp 256GB",
            "terms": "Bảo hành 12 tháng, đổi trả trong 7 ngày",
            "expiry": "2026-12-31",
            "category": "electronics",
            "value_vnd": 30000000,
            "token_cost": 10000
        }
    }
    
    return rewards_metadata


def demo_create_certificate(customer_address: str, reward_name: str, redemption_date: str):
    """Example: Create certificate metadata"""
    
    import uuid
    import hashlib
    
    voucher_code = f"VOUCHER-{uuid.uuid4().hex[:8].upper()}"
    
    certificate = {
        "type": "RedemptionCertificate",
        "customer_address": customer_address,
        "reward_name": reward_name,
        "voucher_code": voucher_code,
        "redemption_date": redemption_date,
        "issued_by": "LoyaltyToken Platform",
        "verification_hash": hashlib.sha256(
            f"{customer_address}{voucher_code}".encode()
        ).hexdigest()[:16]
    }
    
    return certificate


def main():
    """Main demo function"""
    
    print("=" * 60)
    print("IPFS Integration Demo for LoyaltyManager")
    print("=" * 60)
    print()
    
    # Note: In production, use environment variables for API keys
    print("⚠️  Note: This is a demo. Replace with your actual Pinata API keys")
    print()
    
    # Demo data
    print("1️⃣  Creating reward metadata...")
    rewards = demo_create_reward_metadata()
    
    for reward_id, metadata in rewards.items():
        print(f"\n   {reward_id}:")
        print(f"   - Name: {metadata['name']}")
        print(f"   - Cost: {metadata['token_cost']} tokens")
        print(f"   - Category: {metadata['category']}")
    
    print("\n" + "-" * 60)
    print("2️⃣  Creating sample certificate...")
    
    certificate = demo_create_certificate(
        customer_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        reward_name="Voucher giảm giá 10%",
        redemption_date="2025-11-24T10:30:00Z"
    )
    
    print(f"\n   Certificate Preview:")
    print(f"   - Type: {certificate['type']}")
    print(f"   - Voucher Code: {certificate['voucher_code']}")
    print(f"   - Verification Hash: {certificate['verification_hash']}")
    
    print("\n" + "-" * 60)
    print("3️⃣  IPFS Upload Process (requires Pinata API keys):")
    print()
    print("   Step 1: Upload reward metadata JSON")
    print("   → IPFS CID: QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG")
    print()
    print("   Step 2: Upload reward image (PNG/JPG)")
    print("   → IPFS CID: QmTzQ1JRkWErjk39mryYw2WVaphAZNAREyMchXzYywZCpa")
    print()
    print("   Step 3: Upload certificate PDF")
    print("   → IPFS CID: QmS4ustL54uo8FzR9455qaxZwuMiUhyvMcX9Ba8nUH4uVv")
    
    print("\n" + "-" * 60)
    print("4️⃣  Smart Contract Integration:")
    print()
    print("   # Set reward metadata on blockchain")
    print("   manager.setRewardMetadata(")
    print("       reward_id=1,")
    print("       ipfs_cid='QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG'")
    print("   )")
    print()
    print("   # Set reward image")
    print("   manager.setRewardImage(")
    print("       reward_id=1,")
    print("       ipfs_cid='QmTzQ1JRkWErjk39mryYw2WVaphAZNAREyMchXzYywZCpa'")
    print("   )")
    print()
    print("   # Issue certificate to customer")
    print("   manager.issueCertificate(")
    print("       customer='0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',")
    print("       certificate_cid='QmS4ustL54uo8FzR9455qaxZwuMiUhyvMcX9Ba8nUH4uVv'")
    print("   )")
    
    print("\n" + "-" * 60)
    print("5️⃣  Retrieve from IPFS:")
    print()
    print("   Gateway URLs:")
    print("   - https://ipfs.io/ipfs/{CID}")
    print("   - https://gateway.pinata.cloud/ipfs/{CID}")
    print("   - https://cloudflare-ipfs.com/ipfs/{CID}")
    
    print("\n" + "=" * 60)
    print("✅ Demo completed!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Get Pinata API keys from https://pinata.cloud")
    print("2. Set environment variables: PINATA_API_KEY, PINATA_API_SECRET")
    print("3. Redeploy contract with IPFS features")
    print("4. Use scripts/deploy.py to deploy")
    print("5. Test with scripts/interact_with_ipfs.py")


def demo_pinata_integration():
    """
    Example of actual Pinata integration
    Uncomment and use with real API keys
    """
    # Uncomment to use:
    """
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    pinata = PinataIPFS(
        api_key=os.getenv('PINATA_API_KEY'),
        api_secret=os.getenv('PINATA_API_SECRET')
    )
    
    # Upload metadata
    metadata = demo_create_reward_metadata()['reward_1']
    cid = pinata.upload_json(metadata, 'Reward_1_Metadata')
    print(f"Uploaded metadata: {cid}")
    
    # Upload image
    image_cid = pinata.upload_file('rewards/reward_1.png', 'Reward_1_Image')
    print(f"Uploaded image: {image_cid}")
    
    # Retrieve content
    content = pinata.get_content(cid)
    print(f"Retrieved metadata: {content.json()}")
    """
    pass


if __name__ == "__main__":
    main()

