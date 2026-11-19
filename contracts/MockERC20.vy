#pragma version 0.4.3
# Local-only test token. Amounts use 18 decimals.
balanceOf: public(HashMap[address, uint256])
allowance: public(HashMap[address, HashMap[address, uint256]])
owner: immutable(address)

event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    amount: uint256

event Approval:
    holder: indexed(address)
    spender: indexed(address)
    amount: uint256

@deploy
def __init__():
    owner = msg.sender

@external
@nonreentrant
def mint(receiver: address, amount: uint256):
    assert msg.sender == owner, "owner only"
    assert receiver != empty(address), "zero address"
    self.balanceOf[receiver] += amount
    log Transfer(sender=empty(address), receiver=receiver, amount=amount)

@internal
def _transfer(sender: address, receiver: address, amount: uint256):
    assert receiver != empty(address), "zero address"
    assert self.balanceOf[sender] >= amount, "insufficient balance"
    self.balanceOf[sender] -= amount
    self.balanceOf[receiver] += amount
    log Transfer(sender=sender, receiver=receiver, amount=amount)

@external
@nonreentrant
def transfer(receiver: address, amount: uint256) -> bool:
    self._transfer(msg.sender, receiver, amount)
    return True

@external
@nonreentrant
def approve(spender: address, amount: uint256) -> bool:
    self.allowance[msg.sender][spender] = amount
    log Approval(holder=msg.sender, spender=spender, amount=amount)
    return True

@external
@nonreentrant
def transferFrom(sender: address, receiver: address, amount: uint256) -> bool:
    assert self.allowance[sender][msg.sender] >= amount, "insufficient allowance"
    self.allowance[sender][msg.sender] -= amount
    self._transfer(sender, receiver, amount)
    return True
