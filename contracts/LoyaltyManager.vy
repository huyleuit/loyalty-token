# @version 0.3.10

interface LoyaltyToken:
    def mint(_to: address, _value: uint256): nonpayable
    def transfer(_to: address, _value: uint256) -> bool: nonpayable
    def transferFrom(_from: address, _to: address, _value: uint256) -> bool: nonpayable
    def balanceOf(_owner: address) -> uint256: view
    def allowance(_owner: address, _spender: address) -> uint256: view

token_contract: public(address)
owner: public(address)
registered_customers: public(HashMap[address, bool])
reward_costs: public(HashMap[uint256, uint256]) # reward_id -> token cost
reward_metadata: public(HashMap[uint256, String[100]]) # reward_id -> IPFS CID (metadata JSON)
reward_images: public(HashMap[uint256, String[100]]) # reward_id -> IPFS CID (image)
customer_certificates: public(HashMap[address, DynArray[String[100], 50]]) # customer -> list of certificate IPFS CIDs

event CustomerRegistered:
    customer: indexed(address)

event RewardRedeemed:
    customer: indexed(address)
    reward_id: uint256
    cost: uint256

event RewardCreated:
    reward_id: indexed(uint256)
    cost: uint256

event RewardUpdated:
    reward_id: indexed(uint256)
    old_cost: uint256
    new_cost: uint256

event RewardRemoved:
    reward_id: indexed(uint256)

event RewardMetadataSet:
    reward_id: indexed(uint256)
    metadata_cid: String[100]

event RewardImageSet:
    reward_id: indexed(uint256)
    image_cid: String[100]

event CertificateIssued:
    customer: indexed(address)
    certificate_cid: String[100]

@external
def __init__(_token_address: address):
    self.owner = msg.sender
    self.token_contract = _token_address
    # Example: set price for reward 1
    self.reward_costs[1] = 100 * 10**18 # 100 tokens

# Requirement 1: Business - Register customer
@external
def registerCustomer(_customer: address):
    assert msg.sender == self.owner, "Only owner"
    assert not self.registered_customers[_customer], "Already registered"
    self.registered_customers[_customer] = True
    log CustomerRegistered(_customer)

# Requirement 1: Business - Issue reward tokens (called from backend)
@external
def issueTokens(_customer: address, _amount: uint256):
    assert msg.sender == self.owner, "Only owner"
    assert self.registered_customers[_customer], "Customer not registered"
    LoyaltyToken(self.token_contract).mint(_customer, _amount)

# Requirement 1: Business - Redeem reward (called from frontend)
@external
def redeemReward(_reward_id: uint256):
    cost: uint256 = self.reward_costs[_reward_id]
    assert cost > 0, "Invalid reward"

    # Requirement 2: Logic constraint - Check sufficient tokens
    current_balance: uint256 = LoyaltyToken(self.token_contract).balanceOf(msg.sender)
    current_allowance: uint256 = LoyaltyToken(self.token_contract).allowance(msg.sender, self)
    assert current_balance >= cost, "Insufficient tokens"
    assert current_allowance >= cost, "Insufficient allowance"

    # Pull tokens from user to this contract (or burn)
    LoyaltyToken(self.token_contract).transferFrom(msg.sender, self, cost)
    log RewardRedeemed(msg.sender, _reward_id, cost)

# Data retrieval function
@view
@external
def isCustomerRegistered(_customer: address) -> bool:
    return self.registered_customers[_customer]

# Reward Management Functions

# Create or update reward (owner only)
@external
def setRewardCost(_reward_id: uint256, _cost: uint256):
    assert msg.sender == self.owner, "Only owner"
    old_cost: uint256 = self.reward_costs[_reward_id]
    
    if old_cost == 0:
        # Create new reward
        self.reward_costs[_reward_id] = _cost
        log RewardCreated(_reward_id, _cost)
    else:
        # Update existing reward
        self.reward_costs[_reward_id] = _cost
        log RewardUpdated(_reward_id, old_cost, _cost)

# Remove reward (owner only)
@external
def removeReward(_reward_id: uint256):
    assert msg.sender == self.owner, "Only owner"
    assert self.reward_costs[_reward_id] > 0, "Reward does not exist"
    self.reward_costs[_reward_id] = 0
    log RewardRemoved(_reward_id)

# Get reward cost (view function - no gas cost)
@view
@external
def getRewardCost(_reward_id: uint256) -> uint256:
    return self.reward_costs[_reward_id]

# IPFS Metadata Management Functions

# Set reward metadata (IPFS CID for JSON metadata)
@external
def setRewardMetadata(_reward_id: uint256, _ipfs_cid: String[100]):
    assert msg.sender == self.owner, "Only owner"
    assert self.reward_costs[_reward_id] > 0, "Reward does not exist"
    self.reward_metadata[_reward_id] = _ipfs_cid
    log RewardMetadataSet(_reward_id, _ipfs_cid)

# Set reward image (IPFS CID for image file)
@external
def setRewardImage(_reward_id: uint256, _ipfs_cid: String[100]):
    assert msg.sender == self.owner, "Only owner"
    assert self.reward_costs[_reward_id] > 0, "Reward does not exist"
    self.reward_images[_reward_id] = _ipfs_cid
    log RewardImageSet(_reward_id, _ipfs_cid)

# Get reward metadata CID
@view
@external
def getRewardMetadata(_reward_id: uint256) -> String[100]:
    return self.reward_metadata[_reward_id]

# Get reward image CID
@view
@external
def getRewardImage(_reward_id: uint256) -> String[100]:
    return self.reward_images[_reward_id]

# Issue certificate to customer (store IPFS CID)
@external
def issueCertificate(_customer: address, _certificate_cid: String[100]):
    assert msg.sender == self.owner, "Only owner"
    assert self.registered_customers[_customer], "Customer not registered"
    self.customer_certificates[_customer].append(_certificate_cid)
    log CertificateIssued(_customer, _certificate_cid)

# Get all certificates for a customer
@view
@external
def getCustomerCertificates(_customer: address) -> DynArray[String[100], 50]:
    return self.customer_certificates[_customer]

# Get certificate count for a customer
@view
@external
def getCertificateCount(_customer: address) -> uint256:
    return len(self.customer_certificates[_customer])