## 1.3 Smart contract interfaces

### State variables

| Contract | State variables and units |
| --- | --- |
| ScoreOracle | Immutable owner. Writer address, current model version, hash by version, and wallet score (tier, version, update block timestamp). Version must increase. Tiers 1, 2 and 3 are A, B and C. |
| PriceOracle | Immutable owner and collateral price in debt-token units scaled by 10¹⁸. This owner-set price is used on Anvil. |
| LendingPool | Immutable token and oracle addresses and borrow/maintenance ratio arrays in basis points. A wallet position stores collateral, debt and tier_at_borrow. Token quantities use 18 decimals. |
| MockERC20 | Test-token balances and allowances by account. The deployer mints local pilot balances. |

The tiered pool starts at 120% collateral for A and 150% for B. C is ineligible. Maintenance ratios are 110% and 130%. The uniform pool uses 125% at origination and approximately 121.2% maintenance for each tier [6]. The same constructor takes either set of ratios. The close factor is 50% and the liquidation bonus is 5% [4]. Outstanding debt keeps its original tier for maintenance and withdrawals. Additional borrowing must meet the stricter of the original and current borrowing ratios. Mock token transfer guards can also bubble up `insufficient balance` or `insufficient allowance`. State-changing entry points use a reentrancy guard.

### Functions

| Function | Role | Assert messages | State change | Event | EVM estimate | Anvil gas |
| --- | --- | --- | --- | --- | ---: | ---: |
| `register_model` | Owner | owner only, empty hash, version not increasing | Store hash and advance model version | ModelRegistered | 66,700 | 67,940 |
| `set_oracle` | Owner | owner only, zero address | Replace writer | OracleUpdated | 27,500 | 28,121 |
| `set_score` | Writer | oracle only, version mismatch, zero address, invalid tier | Store tier, version and timestamp | ScoreUpdated | 93,000 | 94,739 |
| `set_scores_batch` | Writer | oracle only, invalid batch, plus all per-score guards | Store up to 100 scores atomically | ScoreUpdated per row | 709,240 | 717,192 |
| `get_tier` | Anyone | zero address | Read tier. Falls back to B for missing, stale or old-version score | None | 29,400 | 30,237 |
| `deposit_collateral` | Wallet | invalid amount, position limit, transfer failed | Credit balance and pull collateral | CollateralDeposited | 84,600 | 83,813 |
| `withdraw_collateral` | Wallet | invalid amount, insufficient collateral, unsafe withdrawal, transfer failed | Debit balance and return collateral | CollateralWithdrawn | 75,900 | 53,668 |
| `borrow` | Wallet | invalid amount, tier cannot borrow, position limit, insufficient collateral, transfer failed | Increase debt and record the first borrow tier | Borrowed | 115,100 | 119,897 |
| `repay` | Wallet | invalid amount, exceeds debt, transfer failed | Reduce debt and clear snapshot tier on full payment | Repaid | 67,500 | 49,661 |
| `liquidate` | Anyone | invalid amount, no debt, healthy loan, exceeds close factor, invalid seizure, transfer failed | Reduce debt and transfer seized collateral to liquidator | Liquidated | 120,900 | 96,682 |
| `set_price` | Owner | owner only, invalid price | Update collateral price | PriceUpdated | 27,500 | 27,887 |

Table 9. Contract interface and gas pilot on 2026-11-19. get_tier uses eth_estimateGas for a transaction-equivalent quote. set_scores_batch uses the median 10-wallet receipt.

Estimates start with 21,000 gas per transaction. Each first nonzero storage write adds about 22,100 gas and a nonzero update adds about 5,000. Cold reads add about 2,100 each and each token movement is budgeted at 40,000. Logs and calldata add approximate overhead. Each fresh score batch entry is budgeted as three new storage slots, 1,500 gas for the event and 1,024 gas for two 32-byte calldata words. Exact gas varies with storage state and calldata bytes.

| Wallets per batch | Calls | Estimate | Median receipt gas | Median gas per wallet | Any receipt >2× |
| ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 10 | 89,824 | 96,378 | 96,378 | No |
| 10 | 10 | 709,240 | 717,192 | 71,719 | No |
| 100 | 10 | 6,903,400 | 6,925,200 | 69,252 | No |

Table 10. Fresh-wallet batch gas using deterministic synthetic inputs on 2026-11-19.

### State machine

![Loan state machine](figures/state_machine.png)

Figure 2. Loan state transitions at the current collateral price.

| From | Action or condition | To | Forbidden transition |
| --- | --- | --- | --- |
| Empty | Deposit collateral | Collateral only | Borrow without enough collateral or liquidate without debt |
| Collateral only | Borrow within the tier limit | Healthy debt | Borrow as C on the tiered deployment |
| Healthy debt | Price crosses below maintenance | Liquidation eligible | Liquidation at or above maintenance |
| Any debt position | Full repayment | Collateral only | Repayment exceeding outstanding debt |
| Liquidation eligible | Up to 50% debt repaid and 5% bonus seized | Debt remains, re-evaluate health | Seizure beyond remaining collateral or repayment above the close factor |
| Collateral only | Withdraw remaining collateral | Empty | Withdraw more collateral than deposited |

Table 11. Loan transitions and forbidden transitions. The health state is computed from debt, collateral and oracle price. Debt dust and positions where permitted seizure exceeds remaining collateral need a future bad-debt settlement design.

### Events

| Events | Fields | Reader |
| --- | --- | --- |
| ModelRegistered, OracleUpdated | Version and hash, or writer address | Deployment audit and operator |
| ScoreUpdated | Wallet, tier and model version | Score dashboard and upload reconciler |
| CollateralDeposited, CollateralWithdrawn, Borrowed, Repaid | Wallet and amount, plus tier on borrow | Position dashboard and test harness |
| Liquidated | Wallet, liquidator, repaid debt and seized collateral | Liquidation dashboard and audit |
| PriceUpdated | Scaled collateral price | Scenario runner and price history |

Table 12. Event consumers and reconciliation fields.

### Off-chain and on-chain boundary

The planned writer uses the Ape keystore account `oracle` for signatures. The private key stays out of source and result files. The local gas pilot uses Ape's synthetic funded test accounts. Before sending a batch, the writer verifies the model hash and version, checks wallet/tier counts and logs a local batch identifier. If a transaction is stuck pending after three blocks, the planned writer checks for a receipt and resends the same nonce with a 20% fee increase. Stop after three retries and log the nonce, transaction hashes and last receipt status for reconciliation. Retry behavior is planned, not yet run.

The blockchain can guarantee contract-enforced access, monotonic model version registration, atomic score batches and an auditable record of state changes. Model accuracy, raw input quality and the correctness of a tier submitted by the trusted writer depend on the off-chain process. A leaked oracle key allows accepted score updates until rotation. An unscored wallet receives B terms. Owners and writers are trusted roles, and the local price oracle accepts owner-set prices. Repeated scores intentionally update a wallet's existing record.
