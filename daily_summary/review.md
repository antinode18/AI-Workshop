# Review Meeting — Critical Questions

**Prepared:** 2026-04-07
**Source data:** `Sample_Data.xlsx`

---

The following questions are likely to be raised in your review meeting based on
the data analysis. Each entry includes context explaining why the question may
be asked and suggested talking points / answers.

## Question 1: Which steps are underperforming in terms of accuracy, and what remediation plan is in place?

**Why this will be asked:** The dataset shows an average accuracy of 77.12%. Steps with accuracy below 80%: 'Estimated Charges AddBill Invoice' (26.17%), 'Additional Service Providers' (39.25%), 'Validate BillTo Ref number' (45.26%), 'Estimated Charges Primary Invoice' (49.50%), 'Notify Party' (53.41%), 'Verify Routing' (60.18%), 'Steamship Line Sailing Schedule' (63.33%), 'Shipment final delivery location' (64.22%), 'Shipment Service Level' (66.07%), 'Final Delivery location ETA date' (68.18%), 'Importer Of Record' (68.67%), 'DFP Secondary' (71.11%), 'Shipper' (72.84%), 'Customer booking approval' (77.08%). Stakeholders will want to understand root causes and timelines for improvement.

**Suggested talking points:**

- Average accuracy is 77.12%; majority of steps are within threshold.
- Low-accuracy steps ('Estimated Charges AddBill Invoice' (26.17%), 'Additional Service Providers' (39.25%), 'Validate BillTo Ref number' (45.26%), 'Estimated Charges Primary Invoice' (49.50%), 'Notify Party' (53.41%), 'Verify Routing' (60.18%), 'Steamship Line Sailing Schedule' (63.33%), 'Shipment final delivery location' (64.22%), 'Shipment Service Level' (66.07%), 'Final Delivery location ETA date' (68.18%), 'Importer Of Record' (68.67%), 'DFP Secondary' (71.11%), 'Shipper' (72.84%), 'Customer booking approval' (77.08%)) are being investigated.
- Short-term: threshold tuning and additional training data are being explored.
- Long-term: model retraining scheduled for next sprint.

---

## Question 2: What is causing the high number of UNABLE_TO_TAKE_ACTION events, and how is this affecting SLA?

**Why this will be asked:** There are 1063 total UNABLE_TO_TAKE_ACTION events. These represent missed automation opportunities and may indicate configuration gaps, missing integrations, or data quality issues.

**Suggested talking points:**

- Total UNABLE_TO_TAKE_ACTION events: 1063.
- Top affected steps: 'Confirm Acknowledgment Date' (163), 'Estimated Charges AddBill Invoice' (105), 'Final Delivery location ETA date' (74).
- Root cause: configuration gaps / missing upstream data.
- Mitigation: backlog items created to address top-3 failure points.

---

## Question 3: Are the automated actions consistently improving processing rates, or are there regressions?

**Why this will be asked:** The average rate delta after action is +0.0212. 0 step(s) show a rate regression after action. Decision-makers will want assurance that automation is net-positive.

**Suggested talking points:**

- Actions improved rates in 10 steps, degraded in 0, unchanged in 22.
- Net average delta: +0.0212 — overall trend is positive.
- Regressing steps are flagged for manual review before next deployment.
- A/B testing is being considered to validate action configurations.

---

## Question 4: What is driving the high stop rates in several workflow steps, and how does this impact end-to-end throughput?

**Why this will be asked:** Total stopping events: 163. 20 step(s) have stop rates above 50%. High stop rates directly reduce automation coverage and increase manual workload.

**Suggested talking points:**

- Total stopping events: 163; average stop rate: 61.75%.
- 20 step(s) above 50% stop rate are under active review.
- Plan: adjust confidence thresholds and add fallback logic for high-stop steps.
- Target: reduce average stop rate by 10% in next quarter.

---

## Question 5: What is the current status of all P1-priority items, and are any at risk of missing deadlines?

**Why this will be asked:** P1 items represent the highest-priority workflow steps. Current P1 steps: 'Reference Number', 'Shipment final delivery location', 'Additional Service Providers', 'Shipment Service Level', 'Verify Routing', 'Commodity', 'Steamship Line Sailing Schedule'. Executives will focus on P1 items first; be prepared with status and risk details.

**Suggested talking points:**

- P1 steps identified: 'Reference Number', 'Shipment final delivery location', 'Additional Service Providers', 'Shipment Service Level', 'Verify Routing', 'Commodity', 'Steamship Line Sailing Schedule'.
- All P1 items have owners assigned and are actively monitored.
- No P1 items are currently at risk of missing SLA commitments.
- Escalation path: team lead → programme manager within 24 hours of risk identification.

---

