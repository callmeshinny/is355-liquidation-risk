#pragma version 0.4.3

owner: public(immutable(address))
price: public(uint256)
MAX_PRICE: constant(uint256) = 10**30

event PriceUpdated:
    price: uint256

@deploy
def __init__(price: uint256):
    owner = msg.sender
    self._set(price)

@internal
def _set(price: uint256):
    assert 0 < price and price <= MAX_PRICE, "invalid price"
    self.price = price
    log PriceUpdated(price=price)

@external
@nonreentrant
def set_price(price: uint256):
    assert msg.sender == owner, "owner only"
    self._set(price)
