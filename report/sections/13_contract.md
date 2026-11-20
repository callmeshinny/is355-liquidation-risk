### 1.3. Smart contract specification

#### State variables

| Contract | State variables and units |
| --- | --- |
| ScoreOracle | Immutable owner. Writer address, current model version, hash by version, and wallet score (tier, version, update block timestamp). Version must increase. Tiers 1, 2 and 3 are A, B and C. |
| PriceOracle | Immutable owner and collateral price in debt-token units scaled by 10¹⁸. This owner-set price is used on Anvil. |
| LendingPool | Immutable token and oracle addresses and borrow/maintenance ratio arrays in basis points. A wallet position stores collateral, debt and tier_at_borrow. Token quantities use 18 decimals. |
| MockERC20 | Test-token balances and allowances by account. The deployer mints local pilot balances. |

Tiered borrowing/maintenance ratios are 120%/110% (A) and 150%/130% (B). C is ineligible. The uniform constructor uses 125%/121.2% [6]. The close factor is 50% and bonus 5% [4]. The original tier governs maintenance and withdrawals. Additional borrowing uses the stricter origination ratio. Token errors can include insufficient balance or insufficient allowance. State-changing entry points use a reentrancy guard.

#### Functions

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

Table 10. Contract interface and gas pilot on 2026-11-19. get_tier uses eth_estimateGas for a transaction-equivalent quote. set_scores_batch uses the median 10-wallet receipt.

Gas assumptions are 21,000 base, 22,100 per fresh slot, 5,000 per update, 2,100 per cold read and 40,000 per token transfer. Each batch entry budgets three fresh slots, 1,500 for logs and 1,024 for calldata.

| Wallets per batch | Calls | Estimate | Median receipt gas | Median gas per wallet | Any receipt >2× |
| ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 10 | 89,824 | 96,378 | 96,378 | No |
| 10 | 10 | 709,240 | 717,192 | 71,719 | No |
| 100 | 10 | 6,903,400 | 6,925,200 | 69,252 | No |

Table 11. Fresh-wallet batch gas using deterministic synthetic inputs on 2026-11-19.

#### State machine

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

Table 12. Loan transitions and forbidden transitions. The health state is computed from debt, collateral and oracle price. Debt dust and positions where permitted seizure exceeds remaining collateral need a future bad-debt settlement design.

| Forbidden transition | Revert message |
| --- | --- |
| Empty position to liquidation | `no debt` |
| Tier C to borrowing under tiered terms | `tier cannot borrow` |
| Healthy debt to liquidation | `healthy loan` |
| Debt position to overpayment | `exceeds debt` |
| Liquidation above the close factor | `exceeds close factor` |
| Debt position to an unsafe withdrawal | `unsafe withdrawal` |

Table 13. Forbidden transitions and exact revert messages.

#### Events

| Events | Fields | Reader |
| --- | --- | --- |
| ModelRegistered, OracleUpdated | Version and hash, or writer address | Deployment audit and operator |
| ScoreUpdated | Wallet, tier and model version | Score dashboard and upload reconciler |
| CollateralDeposited, CollateralWithdrawn, Borrowed, Repaid | Wallet and amount, plus tier on borrow | Position dashboard and test harness |
| Liquidated | Wallet, liquidator, repaid debt and seized collateral | Liquidation dashboard and audit |
| PriceUpdated | Scaled collateral price | Scenario runner and price history |

Table 13. Event consumers and reconciliation fields.

#### Off-chain and on-chain boundary

The planned Ape writer signs with keystore account `oracle`. Keep the private key outside source and results. Verify hash, version and wallet counts before sending. For a stuck transaction after three blocks, check the receipt and resend with the same nonce and 20% higher fee. Stop after three retries and log nonce, hashes and receipt status. Retry behavior is planned, not yet run. The gas pilot uses synthetic accounts.

The chain guarantees authorization enforcement and atomic updates to protect recorded state integrity. Account nonces prevent a transaction from executing twice, and the contract rejects reused model versions while permitting later score updates to the same wallet. Events provide an audit trail of accepted writes. The designated Ape oracle account submits scores, and the owner registers models, appoints the score writer and supplies the local price. The chain cannot verify the inputs or model, so a lying or compromised oracle can publish false tiers or prices that change eligibility or cause wrongful liquidations.
