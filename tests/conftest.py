import json
import os
from pathlib import Path
import pytest
from ape import project, accounts, networks


DEPLOY_FILE = Path("deployments/sepolia.json")


def _load_deployed_addresses():
    if not DEPLOY_FILE.exists():
        return None
    try:
        data = json.loads(DEPLOY_FILE.read_text())
        token_addr = data["contracts"]["LoyaltyToken"]["address"]
        manager_addr = data["contracts"]["LoyaltyManager"]["address"]
        return token_addr, manager_addr
    except Exception:
        return None


@pytest.fixture(scope="session")
def owner():
    use_deployed = os.getenv("USE_DEPLOYED", "0") == "1"
    if use_deployed and networks.provider.network.name == "sepolia":
        # Requires `ape accounts import sepolia-owner ...`
        return accounts.load("sepolia-owner")
    # Local ephemeral account
    return accounts.test_accounts[0]


@pytest.fixture(scope="session")
def user(owner):
    # Separate user for testing flows
    return accounts.test_accounts[1] if owner != accounts.test_accounts[1] else accounts.test_accounts[2]


@pytest.fixture(scope="session")
def token(owner):
    use_deployed = os.getenv("USE_DEPLOYED", "0") == "1"
    if use_deployed and networks.provider.network.name == "sepolia":
        addrs = _load_deployed_addresses()
        assert addrs is not None, "Missing deployments/sepolia.json"
        token_addr, _ = addrs
        return project.LoyaltyToken.at(token_addr)
    # Deploy local instance
    return owner.deploy(project.LoyaltyToken, "Loyalty Token", "LTT", 18)


@pytest.fixture(scope="session")
def manager(owner, token):
    use_deployed = os.getenv("USE_DEPLOYED", "0") == "1"
    if use_deployed and networks.provider.network.name == "sepolia":
        addrs = _load_deployed_addresses()
        assert addrs is not None, "Missing deployments/sepolia.json"
        _, manager_addr = addrs
        return project.LoyaltyManager.at(manager_addr)
    # Deploy local instance
    m = owner.deploy(project.LoyaltyManager, token.address)
    # Transfer token ownership to manager so it can mint
    token.set_owner(m.address, sender=owner)
    return m


