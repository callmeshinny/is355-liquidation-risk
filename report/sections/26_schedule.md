### 2.6. Test schedule

Hours below are planning allowances. Each row shows runs × time, preparation and analysis. Related runs share artifacts and parallel work is possible after the split and configuration freeze.

| Work | Weeks | Duration calculation (hours) | Owner | Depends on | Output |
| --- | --- | --- | --- | --- | --- |
| Implement and verify contract interface | 5 | 22 × 0.05 + 3 prep + 0.9 review = 5 | Ngoc | Local contract interface | M1, all T3 checks on Anvil |
| Freeze D5, model settings and manifests | 5–6 | 5 × 0.2 + 3 prep + 1 review = 5 | Khanh | Data checks and pilot manifests | M2, tagged configuration commit |
| Run T1/T2 and reuse Taiwan fits | 6–7 | 15 configuration batches × 0.25 + 2 prep + 2.25 analysis = 8 | Khanh | M2 | Seed-level AUC and Brier CSVs |
| Run T4 and local T5 gas | 6–7 | 40 gas receipts × 0.02 + 2 prep + 2.2 review = 5 | Ngoc | M1 | Guard checks and gas receipts |
| Collect Sepolia windows and complete T6 | 7–8 | 2 windows × 0.75 + 6 fresh runs × 0.25 + 2 prep + 1 analysis = 6 | Ngoc | M1, M2 and confirmed funding | Receipt timings and integration logs |
| Finish T7 and reconcile evidence | 8 | 4 shock batches × 0.5 + 2 prep + 2 analysis = 6 | Khanh | M2 and completed score runs | M3, run artifacts and documented gaps |
| Analyze and polish final draft | 8–9 | 2 review passes × 1 + 1 prep + 2 revision = 5 | Khanh and Ngoc | M3 | M4, analysis and final draft |
| Buffer | 9 | 10 reserved hours | Khanh and Ngoc | Release as needed | Reruns, RPC delays or review |

Table 20. Week 5–9 schedule by owner.

M1 means all T3 checks pass on Anvil. M2 freezes the configuration and leaves test for evaluation. M3 closes execution with raw results and explicit records of unavailable scenarios. M4 is the final analyzed draft. The plan allocates 40 working hours plus 10 buffer hours, so buffer is 10/50 = 20% of total capacity.

![Week 5 to Week 9 Gantt chart](figures/gantt.png)

Figure 3. Work windows, milestone deadlines and reserved time.
