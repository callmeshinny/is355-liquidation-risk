"""Measure local Anvil gas on synthetic wallets, with fresh storage per batch."""

import json
from datetime import date
from pathlib import Path
from statistics import median

from ape import accounts, networks, project
from eth_utils import to_checksum_address

UNIT = 10**18
SIZES = (1, 10, 100)
REPETITIONS = 10
BASE, FRESH_SLOT, UPDATE_SLOT, COLD_READ, EVENT, TRANSFER = 21000, 22100, 5000, 2100, 1500, 40000


def measured(receipt, estimate):
    used = receipt.gas_used
    return {"gas": used, "estimate": estimate, "over_2x": used > 2 * estimate}


def main():
    provider = networks.active_provider
    if provider is None or provider.name != "foundry" or not provider.network.is_dev:
        raise ValueError("Run with the local Foundry development network")
    owner, writer, borrower, liquidator = accounts.test_accounts[:4]
    model_hash = bytes.fromhex("11" * 32)
    collateral = owner.deploy(project.MockERC20)
    debt = owner.deploy(project.MockERC20)
    price = owner.deploy(project.PriceOracle, UNIT)
    score = owner.deploy(project.ScoreOracle, writer.address)
    pool = owner.deploy(project.LendingPool, collateral.address, debt.address, price.address,
                        score.address, [12000, 15000, 0], [11000, 13000, 0])
    collateral.mint(borrower, 200 * UNIT, sender=owner)
    debt.mint(pool, 1000 * UNIT, sender=owner)
    debt.mint(liquidator, 100 * UNIT, sender=owner)
    collateral.approve(pool, 200 * UNIT, sender=borrower)
    debt.approve(pool, 100 * UNIT, sender=borrower)
    debt.approve(pool, 100 * UNIT, sender=liquidator)
    functions = {}
    functions["register_model"] = measured(score.register_model(model_hash, 1, sender=owner),
                                            BASE + 2 * FRESH_SLOT + EVENT)
    functions["set_oracle"] = measured(score.set_oracle(owner, sender=owner), BASE + UPDATE_SLOT + EVENT)
    score.set_oracle(writer, sender=owner)
    functions["set_score"] = measured(score.set_score(borrower, 2, 1, sender=writer),
                                       BASE + 3 * FRESH_SLOT + 2 * COLD_READ + EVENT)
    gas = provider.web3.eth.estimate_gas({"to": str(score.address),
                                        "data": score.get_tier.encode_input(borrower)})
    estimate = BASE + 4 * COLD_READ
    functions["get_tier"] = {"gas": gas, "estimate": estimate,
                             "over_2x": gas > 2 * estimate, "method": "eth_estimateGas"}
    functions["deposit_collateral"] = measured(pool.deposit_collateral(151 * UNIT, sender=borrower),
                                                BASE + FRESH_SLOT + TRANSFER + EVENT)
    functions["borrow"] = measured(pool.borrow(100 * UNIT, sender=borrower),
                                    BASE + 2 * FRESH_SLOT + 4 * COLD_READ + TRANSFER + EVENT)
    functions["withdraw_collateral"] = measured(pool.withdraw_collateral(UNIT, sender=borrower),
                                                 BASE + UPDATE_SLOT + 4 * COLD_READ + TRANSFER + EVENT)
    functions["repay"] = measured(pool.repay(UNIT, sender=borrower), BASE + UPDATE_SLOT + TRANSFER + EVENT)
    functions["set_price"] = measured(price.set_price(8 * UNIT // 10, sender=owner),
                                       BASE + UPDATE_SLOT + EVENT)
    functions["liquidate"] = measured(pool.liquidate(borrower, 49 * UNIT, sender=liquidator),
                                       BASE + 2 * UPDATE_SLOT + 4 * COLD_READ + 2 * TRANSFER + EVENT)
    batches = {}
    next_wallet = 10000
    for size in SIZES:
        estimate = BASE + size * (3 * FRESH_SLOT + EVENT + 2 * 32 * 16)
        samples = []
        for trial in range(REPETITIONS):
            wallets = [to_checksum_address(f"0x{index:040x}")
                       for index in range(next_wallet, next_wallet + size)]
            tiers = [1 + (index + trial) % 3 for index in range(size)]
            next_wallet += size
            receipt = score.set_scores_batch(wallets, tiers, 1, sender=writer)
            samples.append(receipt.gas_used)
            assert score.get_tier(wallets[-1]) == tiers[-1]
        batches[str(size)] = dict(samples=samples, median=median(samples), estimate=estimate,
                                  median_per_wallet=median(samples) / size,
                                  over_2x=max(samples) > 2 * estimate)
    representative = batches["10"]
    functions["set_scores_batch"] = dict(gas=representative["median"],
                                          estimate=representative["estimate"],
                                          over_2x=representative["over_2x"],
                                          method="median of 10-wallet batches")
    report = {"date": date.today().isoformat(), "network": "ethereum:local:foundry",
              "case": "Synthetic fresh wallets, local test tokens", "seed": None,
              "functions": functions, "batches": batches}
    Path("results/pilot_gas.json").write_text(json.dumps(report, indent=2) + "\n")
    print({size: row["median"] for size, row in batches.items()})


if __name__ == "__main__":
    main()
