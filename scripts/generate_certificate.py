"""
Script to generate PDF certificates for redeemed rewards
Includes QR code for verification
"""

import json
import hashlib
import uuid
from datetime import datetime
from io import BytesIO

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor
    import qrcode
except ImportError:
    print("⚠️  Missing dependencies. Install with:")
    print("   pip install reportlab qrcode[pil] Pillow")
    exit(1)


class CertificateGenerator:
    """Generate PDF certificates for loyalty program"""
    
    def __init__(self):
        self.page_size = A4
        self.width, self.height = self.page_size
    
    def generate_voucher_code(self) -> str:
        """Generate unique voucher code"""
        return f"LTT-{uuid.uuid4().hex[:12].upper()}"
    
    def generate_verification_hash(self, customer_address: str, voucher_code: str) -> str:
        """Generate verification hash for certificate"""
        data = f"{customer_address}{voucher_code}{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16].upper()
    
    def create_qr_code(self, data: str) -> BytesIO:
        """Create QR code image"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to BytesIO
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return img_buffer
    
    def generate_certificate(
        self,
        customer_address: str,
        customer_name: str,
        reward_name: str,
        reward_description: str,
        token_cost: int,
        redemption_date: str,
        output_path: str
    ) -> dict:
        """
        Generate PDF certificate
        
        Returns:
            dict with voucher_code, verification_hash, and certificate metadata
        """
        # Create canvas
        c = canvas.Canvas(output_path, pagesize=self.page_size)
        
        # Generate voucher code and verification hash
        voucher_code = self.generate_voucher_code()
        verification_hash = self.generate_verification_hash(customer_address, voucher_code)
        
        # Colors
        primary_color = HexColor('#2563eb')  # Blue
        secondary_color = HexColor('#64748b')  # Gray
        accent_color = HexColor('#10b981')  # Green
        
        # Header - Certificate Title
        c.setFillColor(primary_color)
        c.setFont("Helvetica-Bold", 32)
        c.drawCentredString(self.width / 2, self.height - 1.5*inch, "REWARD CERTIFICATE")
        
        # Border decoration
        c.setStrokeColor(primary_color)
        c.setLineWidth(3)
        c.rect(0.5*inch, 0.5*inch, self.width - inch, self.height - inch)
        
        c.setLineWidth(1)
        c.rect(0.6*inch, 0.6*inch, self.width - 1.2*inch, self.height - 1.2*inch)
        
        # Subtitle
        c.setFillColor(secondary_color)
        c.setFont("Helvetica", 14)
        c.drawCentredString(self.width / 2, self.height - 2*inch, 
                          "LoyaltyToken Rewards Platform")
        
        # Horizontal line
        c.setStrokeColor(accent_color)
        c.setLineWidth(2)
        c.line(2*inch, self.height - 2.3*inch, self.width - 2*inch, self.height - 2.3*inch)
        
        # Certificate details
        y_position = self.height - 3.2*inch
        line_height = 0.35*inch
        
        c.setFillColor(HexColor('#000000'))
        c.setFont("Helvetica", 12)
        
        # Customer name
        c.setFont("Helvetica-Bold", 11)
        c.drawString(1.5*inch, y_position, "Issued to:")
        c.setFont("Helvetica", 11)
        c.drawString(3*inch, y_position, customer_name)
        
        y_position -= line_height
        
        # Customer address (shortened)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(1.5*inch, y_position, "Wallet Address:")
        c.setFont("Courier", 9)
        c.drawString(3*inch, y_position, f"{customer_address[:10]}...{customer_address[-8:]}")
        
        y_position -= line_height * 1.3
        
        # Reward details box
        c.setFillColor(HexColor('#f1f5f9'))
        c.rect(1.3*inch, y_position - 0.6*inch, self.width - 2.6*inch, 1.8*inch, fill=1)
        
        c.setFillColor(HexColor('#000000'))
        c.setFont("Helvetica-Bold", 14)
        c.drawString(1.5*inch, y_position + 0.9*inch, "Reward Details")
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1.5*inch, y_position + 0.4*inch, reward_name)
        
        c.setFont("Helvetica", 10)
        c.drawString(1.5*inch, y_position + 0.05*inch, reward_description[:70])
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1.5*inch, y_position - 0.3*inch, f"Token Cost: {token_cost:,} LTT")
        
        y_position -= 2.2*inch
        
        # Voucher code (prominent)
        c.setFillColor(accent_color)
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(self.width / 2, y_position, f"VOUCHER CODE: {voucher_code}")
        
        y_position -= 0.6*inch
        
        # Verification details
        c.setFillColor(secondary_color)
        c.setFont("Helvetica", 9)
        c.drawString(1.5*inch, y_position, f"Verification Hash: {verification_hash}")
        
        y_position -= 0.25*inch
        c.drawString(1.5*inch, y_position, f"Redemption Date: {redemption_date}")
        
        # QR Code
        qr_data = json.dumps({
            "voucher_code": voucher_code,
            "customer": customer_address,
            "verification": verification_hash,
            "reward": reward_name
        })
        
        qr_buffer = self.create_qr_code(qr_data)
        qr_size = 1.5*inch
        
        # Save QR code temporarily and draw it
        from reportlab.platypus import Image as RLImage
        qr_img = RLImage(qr_buffer, width=qr_size, height=qr_size)
        qr_img.drawOn(c, self.width - 2.5*inch, 1.2*inch)
        
        # QR code label
        c.setFont("Helvetica", 8)
        c.drawCentredString(self.width - 1.75*inch, 0.9*inch, "Scan to verify")
        
        # Footer
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColor(secondary_color)
        c.drawCentredString(self.width / 2, 0.7*inch, 
                          "This certificate is cryptographically secured on Ethereum blockchain")
        c.drawCentredString(self.width / 2, 0.5*inch, 
                          "Visit loyalty-token.example.com to verify authenticity")
        
        # Save PDF
        c.save()
        
        # Return metadata
        metadata = {
            "voucher_code": voucher_code,
            "verification_hash": verification_hash,
            "customer_address": customer_address,
            "customer_name": customer_name,
            "reward_name": reward_name,
            "token_cost": token_cost,
            "redemption_date": redemption_date,
            "qr_data": qr_data,
            "file_path": output_path
        }
        
        return metadata


def main():
    """Demo certificate generation"""
    
    print("=" * 70)
    print("Certificate Generator Demo")
    print("=" * 70)
    print()
    
    generator = CertificateGenerator()
    
    # Example certificate data
    certificate_data = {
        "customer_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "customer_name": "Nguyen Van A",
        "reward_name": "Voucher giảm giá 20%",
        "reward_description": "Giảm 20% cho đơn hàng tiếp theo, áp dụng từ 500,000 VNĐ",
        "token_cost": 500,
        "redemption_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "output_path": "sample_certificate.pdf"
    }
    
    print("Generating certificate with following details:")
    print(f"  Customer: {certificate_data['customer_name']}")
    print(f"  Address: {certificate_data['customer_address']}")
    print(f"  Reward: {certificate_data['reward_name']}")
    print(f"  Token Cost: {certificate_data['token_cost']} LTT")
    print()
    
    # Generate certificate
    metadata = generator.generate_certificate(**certificate_data)
    
    print("✅ Certificate generated successfully!")
    print()
    print("Certificate Details:")
    print(f"  📄 File: {metadata['file_path']}")
    print(f"  🎟️  Voucher Code: {metadata['voucher_code']}")
    print(f"  🔐 Verification Hash: {metadata['verification_hash']}")
    print()
    print("Next steps:")
    print("  1. Upload PDF to IPFS")
    print("  2. Call manager.issueCertificate(customer, ipfs_cid)")
    print("  3. Customer can download and use voucher")
    print()
    print("=" * 70)
    
    # Save metadata as JSON for IPFS upload
    metadata_path = "sample_certificate_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"💾 Metadata saved to: {metadata_path}")


if __name__ == "__main__":
    main()

