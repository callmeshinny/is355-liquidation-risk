## 2.7 Risks and contingencies

| ID | Risk | Likelihood | Impact | Trigger | Backup |
| --- | --- | --- | --- | --- | --- |
| R1 | Sepolia faucet funding falls short | Medium | High | Balance below the planned budget in Section 2.4 | Verify funding before deployment. Stage the samples and report any shortfall in confirmation count. Keep functional and gas evidence on Anvil. |
| R2 | RPC throttling or unstable receipt collection | Medium | Medium | Repeated throttling or missing receipts across a window | Rate-limit polling, store transaction hashes and resume receipt checks. Reschedule a window with incomplete data. |
| R3 | Baseline reproduction misses the paper tolerance | High | Medium | Held-out AUC differs by more than 0.02 | Report the deviation. Audit split, eligible feature set and PCA. Keep the reproduced baseline and the paper figure available. |
| R4 | Prevalence shift degrades calibration | High | High | Positive calibration gaps or worse Brier in populated test quarters | Compare raw, isotonic and Platt. Use a later validation slice for any future prospective update and preserve the original test. |
| R5 | Two-person capacity is exceeded | Medium | High | Milestone slips or review exceeds its allowance | Use the Week 9 buffer. Share one run manifest and prioritize required local evidence. |
| R6 | Fixed D1 cutoffs overlap | Observed | High | Independent validation extrema are unordered | Mark the fixed outputs unavailable. Keep percentile sensitivity labelled and publish the feasibility evidence. |
| R7 | Wallet history lacks open-loan membership | Observed | High | Snapshot cannot reconstruct active positions at scoring time | Use the cohort proxy for retrospective evidence. Validate D2 on a timestamped open-loan fixture before integration. |

Table 21. Risk triggers and contingency actions.
