# Tích hợp IPFS vào LoyaltyManager Contract

## 📋 Tổng quan

Smart contract `LoyaltyManager.vy` đã được cập nhật để hỗ trợ lưu trữ **3 loại dữ liệu trên IPFS**:

1. **📄 Metadata JSON** - Thông tin chi tiết về phần thưởng (tên, mô tả, điều kiện...)
2. **🖼️ Image** - Hình ảnh minh họa của phần thưởng
3. **📜 Certificates** - Chứng nhận/Voucher khi khách hàng đổi quà

---

## 🔧 Các chức năng mới

### 1. Quản lý Metadata (JSON)

#### `setRewardMetadata(reward_id, ipfs_cid)`
Lưu IPFS CID của file metadata JSON cho phần thưởng.

```python
# Ví dụ metadata JSON trên IPFS:
{
  "name": "Voucher giảm giá 20%",
  "description": "Giảm 20% cho đơn hàng tiếp theo",
  "terms": "Áp dụng cho đơn từ 500k",
  "expiry": "2025-12-31",
  "category": "discount"
}
```

**Yêu cầu:**
- Chỉ owner
- Reward phải tồn tại (đã set cost)

#### `getRewardMetadata(reward_id) -> String[100]`
Trả về IPFS CID của metadata.

---

### 2. Quản lý Hình ảnh

#### `setRewardImage(reward_id, ipfs_cid)`
Lưu IPFS CID của hình ảnh phần thưởng (PNG, JPG, WebP...).

**Yêu cầu:**
- Chỉ owner
- Reward phải tồn tại

#### `getRewardImage(reward_id) -> String[100]`
Trả về IPFS CID của hình ảnh.

---

### 3. Quản lý Chứng nhận (Certificates)

#### `issueCertificate(customer, certificate_cid)`
Phát hành chứng nhận/voucher PDF cho khách hàng sau khi đổi quà.

```python
# Ví dụ certificate PDF có thể chứa:
- Mã voucher: VOUCHER-123456
- Ngày phát hành
- Ngày hết hạn
- QR code để xác thực
- Chữ ký số
```

**Yêu cầu:**
- Chỉ owner
- Khách hàng phải đã đăng ký

#### `getCustomerCertificates(customer) -> DynArray[String[100], 50]`
Trả về danh sách tất cả IPFS CID của chứng nhận của khách hàng (tối đa 50).

#### `getCertificateCount(customer) -> uint256`
Đếm số lượng chứng nhận của khách hàng.

---

## 📊 Cấu trúc dữ liệu mới

```vyper
# Lưu trữ IPFS CID
reward_metadata: public(HashMap[uint256, String[100]])           # reward_id -> metadata CID
reward_images: public(HashMap[uint256, String[100]])              # reward_id -> image CID
customer_certificates: public(HashMap[address, DynArray[String[100], 50]])  # customer -> certificates
```

---

## 🔔 Events mới

```vyper
event RewardMetadataSet:
    reward_id: indexed(uint256)
    metadata_cid: String[100]

event RewardImageSet:
    reward_id: indexed(uint256)
    image_cid: String[100]

event CertificateIssued:
    customer: indexed(address)
    certificate_cid: String[100]
```

---

## 🚀 Luồng hoạt động hoàn chỉnh

### Kịch bản: Tạo phần thưởng mới với IPFS

```python
# 1. Upload metadata JSON lên IPFS
metadata = {
    "name": "iPhone 15 Pro",
    "description": "Điện thoại cao cấp",
    "value": 30000000
}
# -> IPFS CID: QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG

# 2. Upload hình ảnh lên IPFS
# iphone_image.png -> QmTzQ1JRkWErjk39mryYw2WVaphAZNAREyMchXzYywZCpa

# 3. Tạo reward trên blockchain
manager.setRewardCost(reward_id=5, cost=1000 * 10**18)  # 1000 tokens

# 4. Set metadata và image
manager.setRewardMetadata(5, "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG")
manager.setRewardImage(5, "QmTzQ1JRkWErjk39mryYw2WVaphAZNAREyMchXzYywZCpa")
```

### Kịch bản: Khách hàng đổi quà và nhận chứng nhận

```python
# 1. Khách hàng đổi phần thưởng
token.approve(manager_address, cost)
manager.redeemReward(reward_id=5)

# 2. Backend tạo certificate PDF với thông tin:
#    - Tên khách hàng
#    - Reward đã đổi
#    - Mã voucher unique
#    - QR code

# 3. Upload certificate PDF lên IPFS
# certificate.pdf -> QmS4ustL54uo8FzR9455qaxZwuMiUhyvMcX9Ba8nUH4uVv

# 4. Phát hành certificate on-chain
manager.issueCertificate(
    customer_address,
    "QmS4ustL54uo8FzR9455qaxZwuMiUhyvMcX9Ba8nUH4uVv"
)

# 5. Khách hàng có thể xem tất cả certificates của mình
certificates = manager.getCustomerCertificates(customer_address)
# -> ['QmS4ustL54uo8FzR9455qaxZwuMiUhyvMcX9Ba8nUH4uVv', ...]
```

---

## ✅ Đáp ứng tiêu chí

### ✅ Tối thiểu 3 loại dữ liệu lưu trữ
1. ✅ **Metadata JSON** - Thông tin chi tiết phần thưởng
2. ✅ **Image** - Hình ảnh phần thưởng (PNG/JPG/WebP)
3. ✅ **Certificate PDF** - Chứng nhận/Voucher

### ✅ Tối thiểu 2 thao tác
1. ✅ **Upload (Set)** - `setRewardMetadata`, `setRewardImage`, `issueCertificate`
2. ✅ **Retrieve (Get)** - `getRewardMetadata`, `getRewardImage`, `getCustomerCertificates`

### ✅ Demo truy xuất thành công
- Đã có test cases trong `tests/test_ipfs_features.py`
- Có thể demo qua Web3.py API

---

## 🧪 Kiểm thử

Chạy test suite mới:

```bash
ape test tests/test_ipfs_features.py -v
```

Test cases bao gồm:
- ✅ Set và get metadata
- ✅ Set và get image
- ✅ Issue và retrieve certificates
- ✅ Multiple certificates per customer
- ✅ Access control (only owner)
- ✅ Validation (reward exists, customer registered)
- ✅ Complete workflow end-to-end

---

## 🔗 Bước tiếp theo

1. **Triển khai lại contract** lên testnet với chức năng IPFS
2. **Cập nhật backend API** để upload/retrieve từ IPFS
3. **Tích hợp IPFS gateway** (Pinata/Infura/Web3.Storage)
4. **Cập nhật frontend** để hiển thị metadata và certificates

---

## 📚 Tham khảo IPFS CID

IPFS CID (Content Identifier) là hash duy nhất của nội dung file:
- **Format**: `Qm...` (CIDv0) hoặc `bafy...` (CIDv1)
- **Truy xuất**: `https://ipfs.io/ipfs/{CID}` hoặc `https://gateway.pinata.cloud/ipfs/{CID}`
- **Max length**: 100 ký tự (đủ cho cả CIDv0 và CIDv1)

