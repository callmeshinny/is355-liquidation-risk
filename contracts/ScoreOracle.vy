#pragma version 0.4.3

struct Score:
    tier: uint8
    version: uint256
    updated_at: uint256

owner: public(immutable(address))
oracle: public(address)
model_version: public(uint256)
model_hashes: public(HashMap[uint256, bytes32])
scores: public(HashMap[address, Score])

event ModelRegistered:
    version: indexed(uint256)
    model_hash: bytes32

event OracleUpdated:
    oracle: indexed(address)

event ScoreUpdated:
    wallet: indexed(address)
    tier: uint8
    version: uint256

@deploy
def __init__(oracle: address):
    assert oracle != empty(address), "zero address"
    owner = msg.sender
    self.oracle = oracle

@external
@nonreentrant
def register_model(model_hash: bytes32, version: uint256):
    assert msg.sender == owner, "owner only"
    assert model_hash != empty(bytes32), "empty hash"
    assert version > self.model_version, "version not increasing"
    self.model_version = version
    self.model_hashes[version] = model_hash
    log ModelRegistered(version=version, model_hash=model_hash)

@external
@nonreentrant
def set_oracle(oracle: address):
    assert msg.sender == owner, "owner only"
    assert oracle != empty(address), "zero address"
    self.oracle = oracle
    log OracleUpdated(oracle=oracle)

@internal
def _set(wallet: address, tier: uint8, version: uint256):
    assert version != 0 and version == self.model_version, "version mismatch"
    assert wallet != empty(address), "zero address"
    assert 1 <= tier and tier <= 3, "invalid tier"
    self.scores[wallet] = Score(tier=tier, version=version, updated_at=block.timestamp)
    log ScoreUpdated(wallet=wallet, tier=tier, version=version)

@external
@nonreentrant
def set_score(wallet: address, tier: uint8, version: uint256):
    assert msg.sender == self.oracle, "oracle only"
    self._set(wallet, tier, version)

@external
@nonreentrant
def set_scores_batch(wallets: DynArray[address, 100], tiers: DynArray[uint8, 100], version: uint256):
    assert msg.sender == self.oracle, "oracle only"
    assert 0 < len(wallets) and len(wallets) == len(tiers), "invalid batch"
    for i: uint256 in range(len(wallets), bound=100):
        self._set(wallets[i], tiers[i], version)

@external
@view
def get_tier(wallet: address) -> uint8:
    assert wallet != empty(address), "zero address"
    score: Score = self.scores[wallet]
    if score.tier == 0 or score.version != self.model_version or block.timestamp - score.updated_at > 30 * 86400:
        return 2
    return score.tier
