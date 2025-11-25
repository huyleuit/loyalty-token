from ape import reverts


def test_register_and_issue_tokens(owner, user, token, manager):
    # Register user
    tx = manager.registerCustomer(user.address, sender=owner)
    assert tx is not None
    assert manager.isCustomerRegistered(user.address) is True

    # Issue tokens to user (manager is token owner)
    amount = 1_000 * 10**18
    manager.issueTokens(user.address, amount, sender=owner)
    assert token.balanceOf(user.address) == amount


def test_redeem_requires_balance_and_allowance(owner, user, token, manager):
    reward_id = 1
    cost = manager.reward_costs(reward_id)
    assert cost > 0

    # Ensure user is registered and funded
    if not manager.isCustomerRegistered(user.address):
        manager.registerCustomer(user.address, sender=owner)
    # Top-up if needed
    balance = token.balanceOf(user.address)
    if balance < cost:
        manager.issueTokens(user.address, cost - balance, sender=owner)
        balance = token.balanceOf(user.address)
    assert balance >= cost

    # Without allowance -> should revert
    with reverts():
        manager.redeemReward(reward_id, sender=user)

    # Approve manager to pull tokens, then redeem succeeds
    token.approve(manager.address, cost, sender=user)
    manager.redeemReward(reward_id, sender=user)
    assert token.balanceOf(user.address) == balance - cost


