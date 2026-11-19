"""Defensive checks for local contract guards and the collateral invariant."""

import ape
import pytest
from hypothesis import given, settings, strategies as st

from conftest import MODEL_HASH, UNIT


def test_writer_role(protocol):
    with ape.reverts("oracle only"):
        protocol.scores.set_score(protocol.borrower, 1, 1, sender=protocol.borrower)


def test_current_version_required(protocol):
    p = protocol
    p.scores.register_model(MODEL_HASH, 1, sender=p.owner)
    with ape.reverts("version mismatch"):
        p.scores.set_score(p.borrower, 1, 2, sender=p.writer)


def test_stale_score_uses_default_terms(protocol, chain):
    p = protocol
    p.scores.register_model(MODEL_HASH, 1, sender=p.owner)
    p.scores.set_score(p.borrower, 1, 1, sender=p.writer)
    written_at = p.scores.scores(p.borrower).updated_at
    chain.mine(timestamp=written_at + 30 * 86400 + 1)
    assert p.scores.get_tier(p.borrower) == 2
    p.pool.deposit_collateral(120 * UNIT, sender=p.borrower)
    with ape.reverts("insufficient collateral"):
        p.pool.borrow(100 * UNIT, sender=p.borrower)
    p.pool.deposit_collateral(30 * UNIT, sender=p.borrower)
    p.pool.borrow(100 * UNIT, sender=p.borrower)
    assert p.pool.positions(p.borrower).tier_at_borrow == 2


def test_healthy_position_guard(protocol):
    p = protocol
    p.pool.deposit_collateral(150 * UNIT, sender=p.borrower)
    p.pool.borrow(100 * UNIT, sender=p.borrower)
    with ape.reverts("healthy loan"):
        p.pool.liquidate(p.borrower, 50 * UNIT, sender=p.liquidator)


def test_close_factor_guard(protocol):
    p = protocol
    p.pool.deposit_collateral(150 * UNIT, sender=p.borrower)
    p.pool.borrow(100 * UNIT, sender=p.borrower)
    p.price.set_price(8 * UNIT // 10, sender=p.owner)
    with ape.reverts("exceeds close factor"):
        p.pool.liquidate(p.borrower, 50 * UNIT + 1, sender=p.liquidator)


@pytest.mark.parametrize("amount", [0, 2**256 - 1])
def test_amount_bounds(protocol, amount):
    with ape.reverts("invalid amount"):
        protocol.pool.borrow(amount, sender=protocol.borrower)


def test_unscored_wallet_has_b_terms(protocol):
    p = protocol
    assert p.scores.get_tier(p.borrower) == 2
    p.pool.deposit_collateral(120 * UNIT, sender=p.borrower)
    with ape.reverts("insufficient collateral"):
        p.pool.borrow(100 * UNIT, sender=p.borrower)


def test_tier_c_is_ineligible(protocol):
    p = protocol
    p.scores.register_model(MODEL_HASH, 1, sender=p.owner)
    p.scores.set_score(p.borrower, 3, 1, sender=p.writer)
    p.pool.deposit_collateral(150 * UNIT, sender=p.borrower)
    with ape.reverts("tier cannot borrow"):
        p.pool.borrow(UNIT, sender=p.borrower)


def test_borrow_limit_examples(protocol):
    p = protocol
    p.pool.deposit_collateral(150 * UNIT, sender=p.borrower)
    p.scores.register_model(MODEL_HASH, 1, sender=p.owner)

    @settings(max_examples=200, deadline=None, derandomize=True)
    @given(tier=st.sampled_from([1, 2]), basis=st.integers(8000, 12000),
           extra=st.integers(1, 10 * UNIT))
    def check(tier, basis, extra):
        p.scores.set_score(p.borrower, tier, 1, sender=p.writer)
        p.price.set_price(basis * UNIT // 10000, sender=p.owner)
        collateral_value = 150 * UNIT * basis // 10000
        limit = collateral_value * 10000 // {1: 12000, 2: 15000}[tier]
        p.pool.borrow.call(limit, sender=p.borrower)
        with ape.reverts("insufficient collateral"):
            p.pool.borrow.call(limit + extra, sender=p.borrower)
        assert p.pool.positions(p.borrower).debt == 0

    check()
