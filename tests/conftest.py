"""Fresh local contracts for deterministic protocol checks."""

from types import SimpleNamespace

import pytest

UNIT = 10**18
MODEL_HASH = bytes.fromhex("11" * 32)


@pytest.fixture
def protocol(accounts, project):
    owner, writer, borrower, liquidator = accounts[:4]
    collateral = owner.deploy(project.MockERC20)
    debt = owner.deploy(project.MockERC20)
    price = owner.deploy(project.PriceOracle, UNIT)
    scores = owner.deploy(project.ScoreOracle, writer.address)
    pool = owner.deploy(project.LendingPool, collateral.address, debt.address,
                        price.address, scores.address, [12000, 15000, 0], [11000, 13000, 0])
    collateral.mint(borrower, 1_000 * UNIT, sender=owner)
    debt.mint(pool, 10_000 * UNIT, sender=owner)
    debt.mint(liquidator, 1_000 * UNIT, sender=owner)
    collateral.approve(pool, 1_000 * UNIT, sender=borrower)
    debt.approve(pool, 1_000 * UNIT, sender=borrower)
    debt.approve(pool, 1_000 * UNIT, sender=liquidator)
    return SimpleNamespace(owner=owner, writer=writer, borrower=borrower, liquidator=liquidator,
                           collateral=collateral, debt=debt, price=price, scores=scores, pool=pool)
