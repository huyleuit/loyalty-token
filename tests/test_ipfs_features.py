from ape import reverts


def test_set_reward_metadata(owner, manager):
    """Test setting IPFS metadata for a reward"""
    reward_id = 1
    ipfs_cid = "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
    
    # Set metadata for existing reward
    tx = manager.setRewardMetadata(reward_id, ipfs_cid, sender=owner)
    assert tx is not None
    
    # Verify metadata was set
    stored_cid = manager.getRewardMetadata(reward_id)
    assert stored_cid == ipfs_cid


def test_set_reward_image(owner, manager):
    """Test setting IPFS image CID for a reward"""
    reward_id = 1
    image_cid = "QmTzQ1JRkWErjk39mryYw2WVaphAZNAREyMchXzYywZCpa"
    
    # Set image for existing reward
    tx = manager.setRewardImage(reward_id, image_cid, sender=owner)
    assert tx is not None
    
    # Verify image CID was set
    stored_cid = manager.getRewardImage(reward_id)
    assert stored_cid == image_cid


def test_set_metadata_for_nonexistent_reward_fails(owner, manager):
    """Test that setting metadata for non-existent reward fails"""
    reward_id = 999
    ipfs_cid = "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
    
    # Should revert because reward doesn't exist
    with reverts():
        manager.setRewardMetadata(reward_id, ipfs_cid, sender=owner)


def test_only_owner_can_set_metadata(owner, user, manager):
    """Test that only owner can set metadata"""
    reward_id = 1
    ipfs_cid = "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
    
    # Non-owner should not be able to set metadata
    with reverts():
        manager.setRewardMetadata(reward_id, ipfs_cid, sender=user)


def test_issue_certificate_to_customer(owner, user, manager):
    """Test issuing certificate to registered customer"""
    # Register customer first
    if not manager.isCustomerRegistered(user.address):
        manager.registerCustomer(user.address, sender=owner)
    
    certificate_cid = "QmS4ustL54uo8FzR9455qaxZwuMiUhyvMcX9Ba8nUH4uVv"
    
    # Issue certificate
    tx = manager.issueCertificate(user.address, certificate_cid, sender=owner)
    assert tx is not None
    
    # Verify certificate was issued
    certificates = manager.getCustomerCertificates(user.address)
    assert certificate_cid in certificates
    assert manager.getCertificateCount(user.address) >= 1


def test_issue_multiple_certificates(owner, user, manager):
    """Test issuing multiple certificates to one customer"""
    # Register customer first
    if not manager.isCustomerRegistered(user.address):
        manager.registerCustomer(user.address, sender=owner)
    
    certs = [
        "QmS4ustL54uo8FzR9455qaxZwuMiUhyvMcX9Ba8nUH4uVv",
        "QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco",
        "QmYjtig7VJQ6XsnUjqqJvj7QaMcCAwtrgNdahSiFofrE7o"
    ]
    
    initial_count = manager.getCertificateCount(user.address)
    
    # Issue multiple certificates
    for cert_cid in certs:
        manager.issueCertificate(user.address, cert_cid, sender=owner)
    
    # Verify all certificates were added
    final_count = manager.getCertificateCount(user.address)
    assert final_count == initial_count + len(certs)


def test_issue_certificate_to_unregistered_customer_fails(owner, accounts, manager):
    """Test that issuing certificate to unregistered customer fails"""
    unregistered_user = accounts[5]  # Assume this account is not registered
    certificate_cid = "QmS4ustL54uo8FzR9455qaxZwuMiUhyvMcX9Ba8nUH4uVv"
    
    # Should revert if customer not registered
    with reverts():
        manager.issueCertificate(unregistered_user.address, certificate_cid, sender=owner)


def test_complete_reward_with_metadata_workflow(owner, user, token, manager):
    """Test complete workflow: create reward, set metadata, redeem"""
    reward_id = 10
    cost = 50 * 10**18  # 50 tokens
    metadata_cid = "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
    image_cid = "QmTzQ1JRkWErjk39mryYw2WVaphAZNAREyMchXzYywZCpa"
    certificate_cid = "QmS4ustL54uo8FzR9455qaxZwuMiUhyvMcX9Ba8nUH4uVv"
    
    # 1. Create reward
    manager.setRewardCost(reward_id, cost, sender=owner)
    
    # 2. Set metadata and image
    manager.setRewardMetadata(reward_id, metadata_cid, sender=owner)
    manager.setRewardImage(reward_id, image_cid, sender=owner)
    
    # 3. Verify metadata
    assert manager.getRewardMetadata(reward_id) == metadata_cid
    assert manager.getRewardImage(reward_id) == image_cid
    
    # 4. Register and fund customer
    if not manager.isCustomerRegistered(user.address):
        manager.registerCustomer(user.address, sender=owner)
    manager.issueTokens(user.address, cost, sender=owner)
    
    # 5. Redeem reward
    token.approve(manager.address, cost, sender=user)
    manager.redeemReward(reward_id, sender=user)
    
    # 6. Issue certificate after redemption
    manager.issueCertificate(user.address, certificate_cid, sender=owner)
    
    # Verify certificate
    assert certificate_cid in manager.getCustomerCertificates(user.address)


def test_get_empty_certificates_for_new_customer(owner, accounts, manager):
    """Test that new registered customer has no certificates"""
    new_customer = accounts[6]
    
    # Register new customer
    manager.registerCustomer(new_customer.address, sender=owner)
    
    # Should have 0 certificates
    assert manager.getCertificateCount(new_customer.address) == 0
    assert len(manager.getCustomerCertificates(new_customer.address)) == 0

