#pragma version 0.4.3
# Local pilot with trusted test tokens, 18 decimals and ratios in basis points.

interface Token:
    def transfer(receiver: address, amount: uint256) -> bool: nonpayable
    def transferFrom(sender: address, receiver: address, amount: uint256) -> bool: nonpayable

interface Price:
    def price() -> uint256: view

interface Scores:
    def get_tier(wallet: address) -> uint8: view

struct Position:
    collateral: uint256
    debt: uint256
    tier_at_borrow: uint8

positions: public(HashMap[address, Position])
collateral_token: public(immutable(address))
debt_token: public(immutable(address))
price_oracle: public(immutable(address))
score_oracle: public(immutable(address))
borrow_bps: public(immutable(uint256[3]))
liquidation_bps: public(immutable(uint256[3]))
BPS: constant(uint256) = 10000
UNIT: constant(uint256) = 10**18
MAX_AMOUNT: constant(uint256) = 10**36

event CollateralDeposited:
    wallet: indexed(address)
    amount: uint256

event CollateralWithdrawn:
    wallet: indexed(address)
    amount: uint256

event Borrowed:
    wallet: indexed(address)
    amount: uint256
    tier: uint8

event Repaid:
    wallet: indexed(address)
    amount: uint256

event Liquidated:
    wallet: indexed(address)
    liquidator: indexed(address)
    repaid: uint256
    seized: uint256

@deploy
def __init__(collateral: address, debt: address, prices: address, scores: address,
             initial_bps: uint256[3], maintenance_bps: uint256[3]):
    assert collateral != empty(address) and debt != empty(address) and prices != empty(address) and scores != empty(address), "zero address"
    assert collateral != debt, "same token"
    for i: uint256 in range(3):
        assert initial_bps[i] <= 100000 and maintenance_bps[i] <= initial_bps[i], "invalid policy"
        assert (initial_bps[i] == 0 and maintenance_bps[i] == 0) or maintenance_bps[i] >= BPS, "invalid policy"
    collateral_token = collateral
    debt_token = debt
    price_oracle = prices
    score_oracle = scores
    borrow_bps = initial_bps
    liquidation_bps = maintenance_bps

@internal
@pure
def _check_amount(amount: uint256):
    assert 0 < amount and amount <= MAX_AMOUNT, "invalid amount"

@internal
@view
def _value(collateral: uint256) -> uint256:
    return collateral * staticcall Price(price_oracle).price() // UNIT

@external
@nonreentrant
def deposit_collateral(amount: uint256):
    self._check_amount(amount)
    new_total: uint256 = self.positions[msg.sender].collateral + amount
    assert new_total <= MAX_AMOUNT, "position limit"
    self.positions[msg.sender].collateral = new_total
    assert extcall Token(collateral_token).transferFrom(msg.sender, self, amount), "transfer failed"
    log CollateralDeposited(wallet=msg.sender, amount=amount)

@external
@nonreentrant
def withdraw_collateral(amount: uint256):
    self._check_amount(amount)
    p: Position = self.positions[msg.sender]
    assert amount <= p.collateral, "insufficient collateral"
    remaining: uint256 = p.collateral - amount
    if p.debt > 0:
        assert self._value(remaining) * BPS >= p.debt * borrow_bps[convert(p.tier_at_borrow, uint256) - 1], "unsafe withdrawal"
    self.positions[msg.sender].collateral = remaining
    assert extcall Token(collateral_token).transfer(msg.sender, amount), "transfer failed"
    log CollateralWithdrawn(wallet=msg.sender, amount=amount)

@external
@nonreentrant
def borrow(amount: uint256):
    self._check_amount(amount)
    p: Position = self.positions[msg.sender]
    tier: uint8 = staticcall Scores(score_oracle).get_tier(msg.sender)
    current_bps: uint256 = borrow_bps[convert(tier, uint256) - 1]
    assert current_bps != 0, "tier cannot borrow"
    required_bps: uint256 = current_bps
    if p.debt > 0:
        required_bps = max(required_bps, borrow_bps[convert(p.tier_at_borrow, uint256) - 1])
    new_debt: uint256 = p.debt + amount
    assert new_debt <= MAX_AMOUNT, "position limit"
    assert self._value(p.collateral) * BPS >= new_debt * required_bps, "insufficient collateral"
    self.positions[msg.sender].debt = new_debt
    if p.debt == 0:
        self.positions[msg.sender].tier_at_borrow = tier
    assert extcall Token(debt_token).transfer(msg.sender, amount), "transfer failed"
    log Borrowed(wallet=msg.sender, amount=amount, tier=tier)

@external
@nonreentrant
def repay(amount: uint256):
    self._check_amount(amount)
    debt: uint256 = self.positions[msg.sender].debt
    assert amount <= debt, "exceeds debt"
    self.positions[msg.sender].debt = debt - amount
    if debt == amount:
        self.positions[msg.sender].tier_at_borrow = 0
    assert extcall Token(debt_token).transferFrom(msg.sender, self, amount), "transfer failed"
    log Repaid(wallet=msg.sender, amount=amount)

@external
@nonreentrant
def liquidate(wallet: address, amount: uint256):
    self._check_amount(amount)
    p: Position = self.positions[wallet]
    assert p.debt > 0, "no debt"
    assert self._value(p.collateral) * BPS < p.debt * liquidation_bps[convert(p.tier_at_borrow, uint256) - 1], "healthy loan"
    assert amount <= p.debt // 2, "exceeds close factor"
    price: uint256 = staticcall Price(price_oracle).price()
    seized: uint256 = amount * 10500 * UNIT // (BPS * price)
    assert seized > 0 and seized <= p.collateral, "invalid seizure"
    self.positions[wallet].debt = p.debt - amount
    self.positions[wallet].collateral = p.collateral - seized
    assert extcall Token(debt_token).transferFrom(msg.sender, self, amount), "transfer failed"
    assert extcall Token(collateral_token).transfer(msg.sender, seized), "transfer failed"
    log Liquidated(wallet=wallet, liquidator=msg.sender, repaid=amount, seized=seized)
