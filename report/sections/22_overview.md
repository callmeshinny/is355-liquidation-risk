### 2.2. Test scenario overview

| Group | Scenarios | Hypotheses | Environment and repetition |
| --- | --- | --- | --- |
| T1 | T1-01–06, model and policy comparisons | H1–H4, H6 | Python, five paired seeds or LR bootstrap |
| T2 | T2-01–05, ablations | H1–H4 | Python, five paired seeds per setting |
| T3 | T3-01–11, contract functions | H5 | Anvil, valid and guard cases per function |
| T4 | T4-01–08, safeguards and design reviews | H5 | Anvil and design review, plus generated borrowing cases |
| T5 | T5-01–02, gas and confirmation time | H5 | Anvil receipts and planned Sepolia confirmations |
| T6 | T6-01–02, integration | H4–H5 | Three fresh Anvil deployments per scenario |
| T7 | T7-01–03, robustness | H4, H6–H7 | Python, five seeds and planned paired shock draws |

Table 16. Scenario groups. Individual procedures and criteria are in Section 2.3.
