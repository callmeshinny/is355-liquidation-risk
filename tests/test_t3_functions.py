"""Valid calls and direct guard checks for the contract interface."""

import ape
from eth.constants import ZERO_ADDRESS as ZERO_ADDRESS_BYTES

from conftest import MODEL_HASH, UNIT

ZERO_ADDRESS = "0x" + ZERO_ADDRESS_BYTES.hex()



def test_register_model(protocol):
    p = protocol
    p.scores.register_model(MODEL_HASH, 1, sender=p.owner)
    assert p.scores.model_hashes(1) == MODEL_HASH
    with ape.reverts("version not increasing"):
        p.scores.register_model(MODEL_HASH, 1, sender=p.owner)


def test_set_oracle(protocol):
    p = protocol
    p.scores.set_oracle(p.borrower, sender=p.owner)
    assert p.scores.oracle() == p.borrower.address
    with ape.reverts("zero address"):
        p.scores.set_oracle(ZERO_ADDRESS, sender=p.owner)


def test_set_score(protocol):
    p = protocol
    p.scores.register_model(MODEL_HASH, 1, sender=p.owner)
    p.scores.set_score(p.borrower, 1, 1, sender=p.writer)
    assert p.scores.get_tier(p.borrower) == 1
    with ape.reverts("invalid tier"):
        p.scores.set_score(p.borrower, 0, 1, sender=p.writer)


def test_set_scores_batch(protocol):
    p = protocol
    p.scores.register_model(MODEL_HASH, 1, sender=p.owner)
    p.scores.set_scores_batch([p.borrower, p.liquidator], [1, 3], 1, sender=p.writer)
    assert (p.scores.get_tier(p.borrower), p.scores.get_tier(p.liquidator)) == (1, 3)
    with ape.reverts("invalid batch"):
        p.scores.set_scores_batch([p.borrower], [], 1, sender=p.writer)


def test_get_tier(protocol):
    assert protocol.scores.get_tier(protocol.borrower) == 2
    with ape.reverts("zero address"):
        protocol.scores.get_tier(ZERO_ADDRESS)


def test_deposit_collateral(protocol):
    p = protocol
    p.pool.deposit_collateral(150 * UNIT, sender=p.borrower)
    assert p.pool.positions(p.borrower).collateral == 150 * UNIT
    with ape.reverts("invalid amount"):
        p.pool.deposit_collateral(0, sender=p.borrower)


def test_withdraw_collateral(protocol):
    p = protocol
    p.pool.deposit_collateral(151 * UNIT, sender=p.borrower)
    p.pool.borrow(100 * UNIT, sender=p.borrower)
    p.pool.withdraw_collateral(UNIT, sender=p.borrower)
    assert p.pool.positions(p.borrower).collateral == 150 * UNIT
    with ape.reverts("unsafe withdrawal"):
        p.pool.withdraw_collateral(UNIT, sender=p.borrower)


def test_borrow(protocol):
    p = protocol
    p.pool.deposit_collateral(150 * UNIT, sender=p.borrower)
    p.pool.borrow(100 * UNIT, sender=p.borrower)
    assert p.pool.positions(p.borrower).tier_at_borrow == 2
    assert p.debt.balanceOf(p.borrower) == 100 * UNIT
    with ape.reverts("insufficient collateral"):
        p.pool.borrow(1, sender=p.borrower)


def test_repay(protocol):
    p = protocol
    p.pool.deposit_collateral(150 * UNIT, sender=p.borrower)
    p.pool.borrow(100 * UNIT, sender=p.borrower)
    with ape.reverts("exceeds debt"):
        p.pool.repay(101 * UNIT, sender=p.borrower)
    p.pool.repay(100 * UNIT, sender=p.borrower)
    position = p.pool.positions(p.borrower)
    assert (position.debt, position.tier_at_borrow) == (0, 0)


def test_liquidate(protocol):
    p = protocol
    p.pool.deposit_collateral(150 * UNIT, sender=p.borrower)
    p.pool.borrow(100 * UNIT, sender=p.borrower)
    with ape.reverts("healthy loan"):
        p.pool.liquidate(p.borrower, 50 * UNIT, sender=p.liquidator)
    p.price.set_price(8 * UNIT // 10, sender=p.owner)
    p.pool.liquidate(p.borrower, 50 * UNIT, sender=p.liquidator)
    position = p.pool.positions(p.borrower)
    assert position.debt == 50 * UNIT
    assert position.collateral == 150 * UNIT - 525 * UNIT // 8


def test_set_price(protocol):
    p = protocol
    p.price.set_price(2 * UNIT, sender=p.owner)
    assert p.price.price() == 2 * UNIT
    with ape.reverts("invalid price"):
        p.price.set_price(0, sender=p.owner)
