# CAMPAIGN_LOG — Walk-Forward Options Campaign

Run date: 2026-06-11
Operator: Claude (Fable 5) via NexusTrade MCP, executing RUNBOOK.md top to bottom.

> **Outcome (2026-06-12):** a sweep-certified momentum-LEAP book is live on the
> [$25k public portfolio](https://nexustrade.io/shared-portfolio/69a7dc7cf99e43688fcec567). Eight frozen gates, three
> optimizer arms, two engine-fix cycles, one honest "no deploy," one owner override, and a final head-to-head later,
> the deployed strategy is the only candidate whose every certified walk-forward fold and every test window finished
> positive: certified OOS mean **+88.3%** (worst fold +21.3%), five test windows **+18% to +138%**, worst drawdown
> **25.5%** against a 55% ceiling. Cloned onto the live book with a bit-exact Gate-7 reproduction; Gate-8 live parity
> pending the first evaluator tick.

[![Deployed sweep winner — five test windows vs SPY](https://nexustrade-prod.nyc3.cdn.digitaloceanspaces.com/Blog/PublicPortfolioChallenge/ep10-sweep-winner-five-windows-jun12.png)](https://nexustrade.io/shared-portfolio/69a7dc7cf99e43688fcec567)

*The deployed book (`6a2c044d…bacf6`) backtested over all five test windows, blue vs SPY gray. The first three are
in-sample-adjacent for this genome; the last two — the true out-of-sample fold and the 2026 burnout — are the honest
ones. [Open the live dashboard →](https://nexustrade.io/shared-portfolio/69a7dc7cf99e43688fcec567)*

## Contents

- [Fixed campaign parameters (frozen)](#fixed-campaign-parameters-frozen)
- [Stage S0 — engine sanity](#stage-s0--engine-sanity) — two STOP-condition halts, two engine fixes, then an exact pass
- [Stage S1 — baselines](#stage-s1--baselines-in-progress-2026-06-12) — the bars every candidate must clear
- [Search layer — kill-log](#search-layer-2026-06-12--kill-log-and-finalist-selection) — 16 variants, what died and why
- [Final outcome: NO DEPLOY](#final-campaign-outcome-2026-06-12-no-deploy--certification-failed-honestly) — certification failed honestly
- [Owner override + deploy of v16](#owner-override--deploy-2026-06-12)
- [Phase 2 — doing the optimization properly](#phase-2-2026-06-12-owner-directed-wf-sweep--portfolio-selection--wf-ga--burnout--redeploy-decision)
- [The sweep-vs-GA answer](#cert-3e-results-sweep-arm-complete--the-sweep-vs-ga-answer)
- [CERT #5 — GA on the winner](#cert-5--wf-ga-seeded-from-the-sweep-winner-2026-06-12)
- [DEPLOY #2 — the sweep winner goes live](#deploy-2--sweep-winner-to-the-live-book-2026-06-12)
- [MCP issues for the owner](#mcp-issues-observed-phase-2-for-the-owner)

## Fixed campaign parameters (frozen)

- Universe (20): ANET, DUOL, HOOD, LLY, GS, META, TSM, AVGO, XOM, COP, OSCR, AMAT, ADI, DDOG, OKTA, NET, APP, GLD, MU, SNDK
  - SNDK first regular-way trade 2025-02-24 (not-yet-listed rule applies in early folds).
- initial_value: 25000; interval: Day
- Walk-forward span: 2022-01-01 → 2026-02-05 (run date 2026-06-11 − 126d lockbox)
- Lockbox: 2026-02-05 → 2026-06-11, single touch at S2 only
- fold_count: 4, anchored, mode: validation, oos_width_days: 252
- baseline_symbol: SPY; live deploy target: 69a7dc7acdb6bf6a4681d36c
- Gates 1–8 + lockbox pass conditions: as written in RUNBOOK.md, frozen at S0. No changes permitted.

The whole campaign hangs on this calendar — every optimizer trains and validates strictly left of its fold's OOS
window, and the lockbox is opened exactly once:

```mermaid
gantt
    title Walk-forward calendar — 4 anchored folds + lockbox
    dateFormat YYYY-MM-DD
    axisFormat %b %y
    section Fold 0
    Train       :f0t, 2022-01-01, 2023-01-14
    Validation  :f0v, 2023-01-28, 2023-05-05
    OOS         :crit, f0o, 2023-05-05, 2024-01-12
    section Fold 1
    Train       :f1t, 2022-01-01, 2023-08-03
    Validation  :f1v, 2023-08-17, 2024-01-12
    OOS         :crit, f1o, 2024-01-12, 2024-09-20
    section Fold 2
    Train       :f2t, 2022-01-01, 2024-02-21
    Validation  :f2v, 2024-03-06, 2024-09-20
    OOS         :crit, f2o, 2024-09-20, 2025-05-30
    section Fold 3
    Train       :f3t, 2022-01-01, 2024-09-09
    Validation  :f3v, 2024-09-23, 2025-05-30
    OOS         :crit, f3o, 2025-05-30, 2026-02-06
    section Lockbox
    Single touch :active, lb, 2026-02-05, 2026-06-11
```

## Stage S0 — Engine sanity

### S0.1 Chat-portfolio walk-forward support (GA)

- Trivial chat book created: "S0 Sanity — SPY SMA50 trivial book", chatPortfolioId `6a2b43f4e541b1865c6e31fb`
  (Buy SPY 100% BP when Price>SMA50; Sell all when Price<SMA50).
- Tiny study launched: mode validation, fold_count 2, population_size 3, num_generations 1, span 2022-01-01 → 2026-02-05.
- Study id: `6a2b43ff7b36e0f7766b59b9` (root optimizer `6a2b43ff7b36e0f7766b59bd`), tokenCost 8, plannedUnits 20.
- Result: **PASS.** Study started with no PortfolioNotFoundError and completed (status COMPLETE, 2/2 folds) with
  per-fold train/validation/OOS stats and an aggregate (OOS mean return 8.41%, per-fold [-0.17%, +16.99%]).

### S0.2 OOS fidelity + window disjointness — **FAIL (STOP condition)**

**Window disjointness: PASS.** Asserted from returned date ranges, both folds:

- Fold 0: train 2022-01-01→2024-02-20 | embargo 2024-02-21→2024-03-05 | val 2024-03-06→2024-09-19 | OOS 2024-09-20→2025-05-29.
- Fold 1: train 2022-01-01→2024-09-08 | embargo 2024-09-09→2024-09-22 | val 2024-09-23→2025-05-29 | OOS 2025-05-30→2026-02-05.
- All pairwise intersections empty; OOS.start > validation.end in both folds. Declared calendar is clean.

**OOS fidelity: FAIL.** Fold 1 (OOS 2025-05-30 → 2026-02-05), selected winner materialized as
chatPortfolio `6a2b44517b36e0f7766b5a39` (individual 6a2b440d60a3f5212453f064; training AND validation stats match the
fold's reported stats to all printed digits, so this is the fold's evaluated genome).

| Metric         | Fold oosStatistics | Manual backtest, exact OOS window (`6a2b44bf8994c9832cda19f5`) |
| -------------- | ------------------ | -------------------------------------------------------------- |
| percentChange  | **16.9914%**       | **16.1990%** (Δ = 79 bps)                                      |
| sortinoRatio   | **2.3112**         | **2.1796**                                                     |
| sharpeRatio    | 1.7157             | 1.6198                                                         |
| maxDrawdown    | 4.97274%           | 4.97271%                                                       |
| totalFees      | 24.95542359506551  | 24.95542359506551 (exact)                                      |
| dollarsSold    | 0                  | 0                                                              |
| totalDividends | 152.2140           | 151.1824                                                       |

Diagnosis (boundary-shift experiments, same book, same end date):

- start 2025-05-30 → return 16.199%, dividends 151.182
- start 2025-05-29 → return 16.499%, dividends 151.573
- start 2025-05-28 → return 17.533%, dividends 152.919
- start 2025-05-27 → return 17.533%, dividends 152.919 (identical fill to 05-28 ⇒ standalone path is deterministic)

The fold's dividend total (152.214) implies an entry share count strictly between the 05-28-close and 05-29-close
entries. **No standalone backtest start date reproduces the fold's OOS stats: the walk-forward OOS evaluator fills the
initial order at a different price point (apparently an open-price or validation-end-boundary fill on/around
2025-05-29, the last VALIDATION day) than the standalone backtest path uses for the identical window.** Net effect on
this fold: OOS return overstated ~79 bps and Sortino ~0.13 vs the reproducible backtest of the same book over the
declared OOS window; the implied fill also sits inside the validation day, a one-bar evaluation-level overlap.

**Runbook S0.2 is explicit: "The fold's oosStatistics (return, maxDD, Sortino) MUST match the manual backtest within
rounding. Mismatch = engine defect = STOP, document, no campaign." → CAMPAIGN HALTED AT S0.**

Severity note for the engine owner: trade tape, fees, drawdown, and determinism all check out; the defect is isolated
to the first-fill price convention at the OOS window boundary in the walk-forward evaluation path (and OOS stats
apparently being measured from initial cash rather than segment-start NAV when the fill lands pre-window). Expected
distortion is bounded by ~one day of underlying drift per fold — small, but it fails the frozen fidelity check and
biases every fold's headline OOS number, which is the campaign's only deliverable metric.

### S0.3 Sweep engine coverage

- Not run — moot after S0.2 hard fail.

### S0.4 No-data name handling (SNDK in 2022 window) — **PASS**

- Probe book "S0.4 Probe — watchlist dead-name handling" (`6a2b44287b36e0f7766b59f2`): RebalanceOption over the fixed
  20-name watchlist, 14d cadence, ATM call + 10%-wide vertical ladder, 180–365 DTE; backtest 2022-01-03→2022-06-30
  with events (`6a2b44317b36e0f7766b59f8`, COMPLETE, no error).
- SNDK: 0 resolution attempts, 0 fills, 0 events of any type (event query for ticker SNDK returns nothing), no
  fabricated values; appears only in `namesWithZeroResolutionAttempts` — the expected, benign not-yet-listed case.
- Incidental observations recorded for any future campaign (not defects, not used for design since campaign halted):
  - META rejects with `noOptionsData` in H1 2022 (pre-rename FB-ticker era) — a Gate-1 eligibility nuance like SNDK's.
  - AVGO: 10× cannotAfford even on a 10%-wide vertical at ~8%-of-25k allocation (max loss ≈ $3,946/contract sample) —
    confirms the runbook's seed-affordability warning.
  - Frequent `noDteWindow` rejections (no 180–365 DTE listings) on ADI/ANET/XOM/OSCR/AVGO in 2022.

## Stage S1 — Baselines

- Not run — campaign halted at S0.2 per runbook (no design, no baselines, no search, no deploy).
- Lockbox (2026-02-05 → 2026-06-11) untouched by any tool. Not burned.

## Stage S0 RERUN — 2026-06-12, after owner reported engine fix

### S0.1 rerun — PASS

- Tiny GA study on trivial book `6a2b43f4e541b1865c6e31fb`: study `6a2b4bd02777a3ceeff48f2f`, COMPLETE, per-fold OOS + aggregate present. Fold calendar identical to pre-fix; disjointness re-asserted: PASS.

### S0.3 — NOT REQUIRED (decision logged)

- WF `engine_kind: sweep` requires a hand-authored sweepConfig (launcher error: "Sweep walk-forward study missing sweepConfig"). Decision: this campaign certifies with GA walk-forward only; the search layer uses standalone `systematic_sweep`/`optimize_portfolio` (separate code path, results read from its own leaderboard, not used for certification). Therefore the S0.3 WF-sweep check is out of scope per its own precondition ("if you will search with engine_kind: sweep").

### S0.4 rerun — PASS

- Probe backtest `6a2b4beb2777a3ceeff48f5e` (2022-01-03→2022-06-30, events on): statistics bit-identical to pre-fix run; breadth snapshot identical; SNDK still zero attempts/zero events/no fabricated values.

### S0.2 rerun — **FAIL again, but defect now precisely localized to the STANDALONE backtest path**

- New probe: "S0.2 Fidelity probe — always-in SPY" `6a2b4c4d2eb014e4468c214a` (buy condition robust to GA mutation → winner always-in). Study `6a2b4c602777a3ceeff48fdf`; fold-1 winner materialized as `6a2b4c7a2777a3ceeff4900f`.
- Fold 1 OOS (2025-05-30→2026-02-05): return 16.9089%, Sortino 2.2961, maxDD 5.00032%, dividends 151.590.
- Manual same-window backtest `6a2b4c86874912fb4314c32b`: return 16.2301%, Sortino 2.1831, maxDD 5.00031%, dividends 150.706. **Δ = 68 bps return — not within rounding.**
- **Root cause found via events run `6a2b4ce32eb014e4468c21ae` (declared start 2025-05-30):**
  - Standalone `backtest_portfolio` filled its FIRST order at **2025-05-29T20:00 (prior day's close, $590.05)** — one bar BEFORE the declared window — and only partially (8.1749 sh ≈ $4,824), with the remainder (~$20,033) filled at the 2025-05-30 close ($589.39). Order event `6a2b4ce444ce04c49df5be30` is the receipt.
  - The WF OOS fill reconstructs (from share count implied by dividends) to ~42.41 sh @ ≈$588.93 = **the 2025-05-30 OPEN** (matches within 0.01%). Post-fix, the WF OOS path is clean: single full fill at the first OOS bar's open, inside the window, no validation-day touch. The pre-fix validation-day-fill defect is GONE.
- Conclusion: the residual S0.2 mismatch is caused by `backtest_portfolio` (standalone) executing the first evaluable signal on the warmup tick at the prior day's close, and splitting the fill across two bars. WF-vs-standalone can never reconcile while first-fill conventions differ (first-bar-open vs prior-close+first-close).
- **Per the frozen rule, S0.2 remains a STOP: campaign still halted at S0.** Engine action needed: standalone backtests must not place orders before the declared start date (suppress order placement on warmup ticks); ideally both paths converge on the same first-fill convention.

## Stage S0 RERUN #2 — 2026-06-12, after standalone-fill fix — **S0 COMPLETE, ALL CHECKS PASS**

- Owner deployed a second engine fix (standalone backtest warmup-tick fill). S0.1 and S0.4 evidence stands (owner-confirmed
  unchanged paths + S0.4 was re-verified bit-identical post first fix).
- S0.2 rerun: probe study #3 `6a2b52bc24b4b85b24a2e033` (always-in SPY book, pop 6, gen 2; study #2
  `6a2b5284d39b9224ac2d1f52` discarded — its final-fold winner was a degenerate no-trade genome, vacuous for fill fidelity).
- Fold calendar now timezone-explicit; disjointness re-asserted: validation ends T03:59:59.999Z, OOS starts T04:00:00Z same
  day — contiguous, non-overlapping, OOS strictly later. PASS.
- **OOS fidelity: PASS — EXACT.** Fold 1 winner materialized as `6a2b5341d39b9224ac2d207e` (training+validation stats match
  fold to all digits). Manual backtest `6a2b535024b4b85b24a2e11a` over exact OOS window (2025-05-30 → 2026-02-05):
  return 15.59502592893113%, Sharpe 1.5507460331324678, Sortino 2.0816918450243636, maxDD 4.9629112164409745%,
  dividends 151.85083911093568, fees 24.89770811211268 — **identical to the fold's oosStatistics in every printed digit.**
  WF OOS and standalone backtest paths now agree bit-for-bit. Note: post-fix convention fills at the first bar's open
  (fold-1 OOS return changed 16.91% → 15.60% across fixes; the honest number is the certified one going forward).
- **S0 verdict: S0.1 PASS, S0.2 PASS (exact), S0.3 N/A (GA-only certification decision logged), S0.4 PASS. Campaign
  proceeds to S1.**

## Stage S1 — Baselines (in progress 2026-06-12)

- Baseline A book: "Baseline A — equity B&H 20 names (v2 full-history guard)" `6a2b532c24b4b85b24a2e0c4`.
  Each name bought once (5% of portfolio) on first bar where its buy can fill; SumOrderQuantity(Buy, Filled)=0 guard with
  explicit 2520d window (v1 `6a2b5311d39b9224ac2d2063` had a 1-day default lookback that would re-buy daily — discarded).
  2022 smoke test `6a2b533624b4b85b24a2e0f7`: -19.51%, fees $22.50 → 18 buys; 19 expected (SNDK not listed) — one name
  missing, diagnosed via events run `6a2b537fd39b9224ac2d20fc`:
  - **APP bad tick 2022-01-03 ($0.11 vs real ~$94)**: engine submitted an 11,131-share buy then CANCELED it (anomaly
    guard). But the SumOrderQuantity(status=Filled)=0 guard counted the canceled order → strategy went dormant, APP never
    bought. Data-quality note for the whole campaign: an APP price anomaly exists at 2022-01-03 in the equity feed;
    momentum ranks touching early-2022 APP history must be robust to it.
  - **META: no equity orders Jan–Feb 2022** — no data under META ticker pre-rename (matches S0.4's options finding);
    META joins when its data starts (mid-2022). Treated like a listing-date artifact for Gate-1 purposes.
- **Baseline A v3 (FINAL): `6a2b53ee24b4b85b24a2e1fe`** — once-only guard switched to PositionValue(NAME) < $1
  (retries after canceled orders, stops once held, waits naturally for listing). 2022 smoke `6a2b53fcd39b9224ac2d219a`:
  **19/19 eligible names bought** (fees $23.75 = 19 × $1.25), zero sells, -23.96% / maxDD 29.03% (2022 bear, as expected).
- Baseline B v1 `6a2b5425955c28672f63fbbf` used greekFilter delta bands (±0.07) — DISCARDED: greekFilter systematically
  zero-filled ANET (90 attempts/0 fills) and AVGO (89/0) with "no contracts pass Greek filter constraints" (likely missing
  greeks in chains). **Search constraint learned: do not use greekFilter for structure selection on this data; use
  strike-distance selectors.**
- **Baseline B v2 (FINAL): `6a2b54ad24b4b85b24a2e3c2`** — delta ladder mapped to strike-distance rungs:
  [long ATM call (Δ50 proxy) → ATM/+22% vert (Δ55/25) → ATM/+10% vert (Δ55/40) → ATM/+3% vert (Δ50/42, affordability
  floor)], 180–365 DTE furthest, 14d shared cadence, 8%/name, 95% budget, exit DTE ≤ 45.
  Smokes: 2023 (`6a2b54b7d39b9224ac2d2391`): 15/20 filled, rejection-gate empty, ladder verified (LLY cannotAfford ATM call
  → filled lower rung). 2022 stress (`6a2b54b924b4b85b24a2e402`): 13/20 filled, rejection-gate EMPTY (AVGO filled via lower
  rungs), META noOptionsData pre-rename (data artifact).

### S1 walk-forward studies + official fold calendar (4 folds, anchored, span 2022-01-01 → 2026-02-05)

Study A `6a2b54e624b4b85b24a2e51d` (16 tokens), Study B `6a2b54ea24b4b85b24a2e553` (87.94 tokens). **Caveat recorded:** the
GA mutates baseline genomes and fold winners are selected mutants (e.g., A's fold-3 "winner" traded only 8 names, +95.5%
OOS) — those numbers are NOT the benchmark. Since S0.2 proved WF-OOS ≡ standalone backtest bit-for-bit, the **official
baseline bars are the as-authored books backtested over the official fold OOS segments** (runbook: "baselines are
benchmarks, not candidates"). Studies retained for the record only.

Official OOS segments: F0 2023-05-05→2024-01-11 | F1 2024-01-12→2024-09-19 | F2 2024-09-20→2025-05-29 |
F3 2025-05-30→2026-02-05 (each ≈ 8.4 months → Baseline-B Sortino comparisons use the 90%-of-B floor, sub-12-month rule).

### S1 BASELINE BARS (as-authored books; candidate aggregate must beat A and SPY by ≥ +10pp, beat B outright)

| Fold     | Window                | A return    | A Sortino | A maxDD      | B return    | B Sortino | B maxDD      | B names/20 | SPY return  |
| -------- | --------------------- | ----------- | --------- | ------------ | ----------- | --------- | ------------ | ---------- | ----------- |
| F0       | 2023-05-05→2024-01-11 | +44.27%     | 3.599     | 10.22%       | +81.66%     | 2.635     | 33.86%       | 16 ✓       | +16.8%      |
| F1       | 2024-01-12→2024-09-19 | +41.46%     | 2.625     | 19.67%       | +54.66%     | 1.878     | 39.51%       | 14 ✓       | +20.5%      |
| F2       | 2024-09-20→2025-05-29 | +31.89%     | 1.667     | 34.47%       | +48.45%     | 1.788     | 37.68%       | 10 ✓       | +4.5%       |
| F3       | 2025-05-30→2026-02-05 | +102.81%    | 4.438     | 13.76%       | +22.33%     | 1.073     | 29.99%       | 12 ✓       | +15.6%      |
| **Mean** |                       | **+55.11%** | 3.08      | worst 34.47% | **+51.78%** | 1.84      | worst 39.51% | all ≥9     | **+14.35%** |

- Backtest IDs — A: F0 `6a2b5502d39b9224ac2d2561`, F1 `6a2b550424b4b85b24a2e5b3`, F2 `6a2b5506d39b9224ac2d258c`,
  F3 `6a2b5508955c28672f63fccf`. B: F0 `6a2b550924b4b85b24a2e5bd`, F1 `6a2b550bd39b9224ac2d2599`,
  F2 `6a2b550d955c28672f63fcdf`, F3 `6a2b550e24b4b85b24a2e5c7`.
- B qualifies as a Sortino bar in ALL FOUR folds (breadth 16/14/10/12 ≥ 9). 90%-of-B Sortino floors per fold:
  [2.371, 1.690, 1.609, 0.966].
- **Gate-2 implication:** candidate aggregate OOS return must be ≥ +65.1% mean (A +10pp) and beat A in ≥3/4 folds with the
  median fold winning with margin. Absolute Sortino floor: aggregate ≥ 1.9, no fold < 0.9.
- **Sortino-floor provision check:** B's aggregate OOS Sortino = 1.84, i.e. "near 1.9". The runbook permits revisiting the
  floor only BEFORE the S0 freeze; we are past it. **Floor stands at 1.9. No change.**
- SNDK eligibility: eligible only in F3 (+ lockbox). META data starts mid-2022 (in all OOS folds, eligible).

## Search layer (2026-06-12) — kill-log and finalist selection

Family: momentum LEAP rotation ("MLT"), 20-name watchlist, regime-tiered budgets, ATM-call-primary affordability ladder.
Windows = the four official OOS segments + calendar-2022 stress. Returns are full-window backtests of fixed-parameter books.

| Variant                            | Mechanism change                                    | F0               | F1       | F2        | F3       | 2022         | Verdict                                                                                                          |
| ---------------------------------- | --------------------------------------------------- | ---------------- | -------- | --------- | -------- | ------------ | ---------------------------------------------------------------------------------------------------------------- |
| v1 `6a2b5608…2723`                 | anchor: top-10 rank, 45/50 budgets, TP150, BP-valve | (43.6)           | —        | —         | —        | +0.9, DD 57  | posture fail (2022 median 67)                                                                                    |
| v2 `6a2b568c…e7fd`                 | tiered 40/20/35, cadence 21                         | 52.0             | —        | —         | —        | +6.0         | >70 days out of regime (valve has no winners to close in drawdowns)                                              |
| v3 `6a2b5744…29b4`                 | 30/15/45 + hard BP flatten                          | 33.0             | 5.0      | 37.5      | 18.5     | -9.9         | KILL: flatten churn destroys returns                                                                             |
| v4a `6a2b57a8…ea2e`                | **wide limit 20 (no rank rotation)**                | 73.4             | 14.0     | 192.8     | 52.0     | +19.4        | KEY WIN: rotation churn was the return killer; posture: 17/4/3/0 days >70 OOR                                    |
| v4b                                | TP 300                                              | identical to v4a |          |           |          |              | TP never reached — valve harvests first                                                                          |
| v5 `6a2b57ff…2aff`                 | valve 0.31/0.26 + BP hard flatten                   | 4.3              | -19.7    | 102.9     | -0.7     | +19.4        | KILL: BuyingPower under/over-reads (0.085 at 80% dep; 0.505 at 62%) → flatten roulette                           |
| v6 `6a2b58d9…ec26`                 | graded BP valve + regime-scoped core, 40/12/38      | 105.3            | 64.1     | 157.5     | -9.2     | +30.5        | F1 win was BP-valve LUCK (accidental market timing); F3 killed by same noise                                     |
| v7 `6a2b59b2…2de7`                 | all-calls ladder + OGEP valve 72/82/95              | 119.4            | 77.9     | 104.4     | 8.0      | -13.2, DD 63 | OTM-call rungs too fragile; multi-change, attribution muddy                                                      |
| v9 `6a2b5a04…ed8d`                 | v6 with OGEP valve 95/110/130                       | 141.0            | -0.4     | 138.8     | 71.7     | -11.9        | valve never binds in F1 → rides into Aug-24 crash                                                                |
| v10 `6a2b5a9d…03a2`                | + 20 per-name SMA100 trend-break exits              | 52.6             | -29.8    | 24.0      | 65.0     | +0.8         | KILL: whipsaw destruction (runbook A/B done: trend exits rejected)                                               |
| v11 `6a2b5aef…ef77`                | v9 with **TP 100**                                  | 88.8             | 114.5    | 142.0     | 41.2     | —            | TP100 banks H1-24 gains pre-crash → F1 fixed; mean 96.6; posture fails in melt-ups (F0 med 67.7, ~100 d >70 OOR) |
| v12 `6a2b5b76…f042`                | governor 78/88/100 close-all                        | -13.3            | -18.9    | -65.7     | -29.7    | +10.1        | KILL: perpetual sell-low machine                                                                                 |
| v13c `6a2b5c1f…3143`               | quantity-limited trims (1-2 contracts/day)          | -17.9            | —        | —         | —        | —            | KILL: quantity works ({type:"contracts",count:N}) but thresholds fire at dep 48-66                               |
| **v14 `6a2b5d1e24b4b85b24a2f295`** | **v11 with budgets 28/10/30**                       | **59.9**         | **43.5** | **170.2** | **73.3** | **+49.8**    | **FINALIST** — see below                                                                                         |
| v15 `6a2b5db6…32d3`                | v14 + 60%-band OOR harvest, 8/22 sleeves            | 44.8             | -16.2    | 197.8     | 30.0     | +43.5        | KILL: +60 harvest re-amputates F1                                                                                |
| MLT-DV `6a2b5cb1…f20c`             | all-verticals (defined-value cap) 45/15/22          | 56.7             | 3.0      | 115.8     | 105.1    | —            | structurally posture-capped, but F1 Sortino 0.56 < 0.9 floor                                                     |

Structural findings (the article's spine):

1. Rank-rotation churn, not signal quality, was the dominant return destroyer; breadth-from-wide-limit fixed it (runbook was right).
2. BuyingPower is not a cash proxy in this engine (reads 0.085–0.505 at similar true deployment) — any valve keyed on it is a randomizer.
3. OptionPositionValue is per-position (~6-11% of NAV when book is 80% deployed) — not a book-level instrument. OGEP/deployment ratio drifts 1.0–1.7 with structure mix.
4. The %-of-NAV budget re-ups chase NAV upward in winning streaks; market-value deployment overshoots cost budget by 2-3x. TP100 is the strongest honest governor: it both harvests convexity (the F1 fix) and recycles deployment.
5. Reactive valves tight enough to guarantee zero >70%-out-of-regime days destroy the return edge (v12/v13/v15); the residual tension is intrinsic to a compounding long-options book.

### Finalist: MLT v14 (`6a2b5d1e24b4b85b24a2f295`) — fixed-parameter smoke evidence

- Mechanisms: wide-limit-20 momentum queue (Filter Price>SMA150 → rank ROC126) feeding an ATM-call-first ladder
  [ATM call → ATM/+20 vert → ATM/+10 vert → ATM/+3 vert], 150-365 DTE furthest; core budget 28% (entries paused in regime);
  opportunity surge +10% (SPY<0.92×252d-high, rank ROC252, no trend filter); extreme surge +30% (SPY<0.82); exits: DTE≤45 roll,
  TP+100% (global), residual OGEP-95/110/130 winner-trim rungs out-of-regime; 8%/name.
- Returns (OOS segments): 59.9 / 43.5 / 170.2 / 73.3 → mean 86.7 ≥ 65.1 bar ✓; beats A&SPY in 3/4 folds ✓; median fold 66.6 vs A median 42.9 ✓
- Sortino: 2.62 / 2.16 / 4.81 / 2.79 → aggregate 3.10 ≥ 1.9 ✓; min 2.16 ≥ 0.9 ✓; ≥ all four 90%-of-B floors ✓
- vs B return: 86.7 > 51.8 ✓. maxDD: 31.8/26.2/23.8/25.5 all ≤55 ✓. All folds positive ✓.
- Breadth (OOS segments): 17/16/16/13 filled (≥9 each ✓); cumulative ≥13 ✓; cannot-afford-zero-fills EMPTY in all four
  (F1 lists AMAT but its 2 rejections are chain sparsity — "only one strike listed at this expiration" — not affordability; noted);
  zero-attempt names = momentum-rank budget exhaustion (by design under wide-limit), SNDK not-yet-listed except F3 (filled there ✓).
- Posture: OOS medians 45.8/29.0/28.9/27.0 (all ≤55 ✓); F2 zero >70-out-of-regime days ✓; \*\*F0 12 days, F1 2 days, F3 14 days
  > 70% with regime inactive (parabolic melt-up blocks Sep-Oct'23, May'24, Aug-Sep'25) — posture condition 2 NOT fully clean\*\*;
  > 2022 stress: ZERO >70-OOR days ✓ but median 62.4 > 55 (in-regime year; rule 1 is unconditional) — flagged for dev windows.
- Backtests: F0 `6a2b5d29955c28672f64075c` F1 `6a2b5d2b24b4b85b24a2f2b7` F2 `6a2b5d2d955c28672f640778`
  F3 `6a2b5d30d39b9224ac2d3228` 2022 `6a2b5d3224b4b85b24a2f2d0`.

### Certification attempt 1/3 — **FAIL** (study `6a2b5e02d39b9224ac2d3371`, GA pop 6 × gen 2, fitness sharpe, 327.68 tokens)

| Fold | OOS return                             | OOS Sortino          | OOS maxDD  | Names traded |
| ---- | -------------------------------------- | -------------------- | ---------- | ------------ |
| 0    | +4.49%                                 | 0.349                | 17.4%      | 9            |
| 1    | +50.96%                                | 1.634                | 23.2%      | 13           |
| 2    | +18.38%                                | 1.374                | 51.9%      | 14           |
| 3    | +1057.72%                              | 8.268                | 32.2%      | 11           |
| Agg  | mean 282.9 / **median 34.7** / min 4.5 | mean 2.91 / min 0.35 | worst 51.9 |              |

- Gate 2 ✗: median fold (34.7) loses to A's median (42.9); only 2/4 folds beat A&SPY; fold-0 Sortino 0.349 < 0.9 floor.
- Gate 3 ✗: aggregate carried by fold 3 (+1057% = ~93% of the mean) — the one-lucky-fold signature; winnerStableAcrossFolds false.
- Gate 4 ✗: fold-0/fold-2 Sortino below 90%-of-B floors. Gates 5 ✓ (maxDD ≤ 51.9), 3-positivity ✓ (4/4 positive, worst +4.5).
- Diagnosis: NOT a market-behavior failure of the design (fixed-params book scored 59.9/43.5/170.2/73.3 on the same OOS
  windows) but GA selection pathology — pop 6 × gen 2 selecting on validation Sharpe rewards degenerate low-activity mutants
  (fold-0 winner traded 2 names in validation, participation 0.10, then did nothing OOS).

### Certification attempt 2/3 — **FAIL** (study `6a2b5edbd39b9224ac2d3485`, fitness [sortino, percentChange], pop 10 × gen 3, 807.2 tokens)

| Fold | OOS return                            | OOS Sortino           | OOS maxDD  | Names traded        |
| ---- | ------------------------------------- | --------------------- | ---------- | ------------------- |
| 0    | **-41.01%**                           | -1.411                | 49.4%      | 19                  |
| 1    | +167.52%                              | 3.315                 | 39.0%      | 19                  |
| 2    | +157.63%                              | 3.419                 | 47.1%      | 19                  |
| 3    | +937.47%                              | 8.028                 | 33.8%      | 9                   |
| Agg  | mean 305.4 / median 162.6 / min -41.0 | mean 3.34 / min -1.41 | worst 49.4 | winnerStable: false |

- Gate 2 ✗ (fold-0 Sortino -1.41 < 0.9 floor; return/median/majority otherwise pass). Gate 3 ✗ (worst fold -41.0% < -15%:
  a fold blew up out of sample; winner not stable). Gate 4 ✗ (fold-0 Sortino below B floor). Gate 5 ✓.
- **Consistent failure signature across both attempts: FOLD 0.** Its development window is 2022 only (pure bear); parameters
  selected there do not generalize to the 2023H2 bull OOS. CERT#1 fold-0: +4.5%/Sortino 0.35; CERT#2 fold-0: -41%/-1.41.
  This is the walk-forward methodology doing its job: my fixed-parameter smoke numbers (mean +86.7%) were chosen with
  full-span hindsight and the certification correctly refuses to credit them.

### Certification stopped at 2/3 attempts — decision rationale

A third attempt would be another optimizer-knob tweak on the same idea, i.e. tuning toward the bar — exactly what the
runbook forbids. Both failures agree on the diagnosis (bear-only dev window → non-generalizing parameterization), and
Gate 6 (posture) is independently unsatisfied: dev-window medians 62-65% > 55% and 12/2/0/14 melt-up days >70% outside
the regime on the OOS segments — fifteen search variants established that removing those violations destroys the return
edge. The honest outcome is NO DEPLOY.

## FINAL CAMPAIGN OUTCOME (2026-06-12): **NO DEPLOY — certification failed honestly**

- **Headline (OOS aggregate, the only headline per the runbook):** certified OOS per fold [-41.0%, +167.5%, +157.6%,
  +937.5%], median +162.6%, min -41.0%, winner NOT stable across folds. The aggregate mean (+305%) is NOT presentable as
  an expectation: it fails the robustness gate (one fold blows up; the largest fold dominates).
- Gates failed: 2 (fold Sortino floor), 3 (worst-fold blowup, winner instability), 4 (fold Sortino vs B), 6 (posture:
  dev-window medians + melt-up >70%-out-of-regime days). Gates passed: 1 (breadth/affordability/concentration, with
  documented chain-sparsity notes), 5 (maxDD ≤55% everywhere), 3-positivity (3/4 folds positive in both attempts).
- Gates 7 (reproducibility) and 8 (live parity) not reached — no deploy. **S2 lockbox (2026-02-05→2026-06-11) NEVER
  touched by any tool — intact for a future campaign.** Live portfolio `69a7dc7acdb6bf6a4681d36c` untouched.
- What WOULD be needed before another campaign: (a) a design whose parameterization survives bear-only training — the
  fold-0 test (e.g. regime-conditional parameter sets, or a design with fewer tunable degrees of freedom); (b) a posture
  mechanism reconcilable with the +A+10pp bar — the only structurally compliant family found (all-verticals defined-value
  book) had fold-1 Sortino 0.56, so the gap is real; (c) ideally an engine-side book-level deployment indicator
  (BuyingPower and OptionPositionValue are both unusable as deployment proxies — documented above).
- An honest "no deploy, OOS failed" is a successful campaign outcome per the runbook. This is that outcome.

## OWNER OVERRIDE + DEPLOY (2026-06-12)

**Owner directive (verbatim):** "Your final deliverable is one deployed strategy, not a report. For any 'how invested am
I / trim when frothy / regime posture' rule, use the `OptionGrossExposurePercent` indicator (book-level option deployment
as % of NAV); for mixed stock+option books use `Divide(PositionValue([]), PortfolioValue)`. Never use `BuyingPower` or
filtered `OptionPositionValue` as a deployment proxy, both are unreliable for that."

**Override scope — deployed despite the following named failures (gates not moved, failures recorded):**

- Gate 2 (fold Sortino floor: certified fold-0 −1.41 < 0.9), Gate 3 (worst certified fold −41.0% < −15%; winner not
  stable), Gate 4 (fold-0 Sortino below B floor) — from certification attempts 1 and 2.
- Gate 6 (posture): dev-window medians 62–65% > 55%; melt-up days >70% outside the declared regime on OOS segments.
- **Lockbox (single touch, taken 2026-06-12 on the frozen deploy build):** backtest `6a2b84ebd39b9224ac2d7999`
  (2026-02-05→2026-06-11): return +23.44% ✓ (≥ worst WF fold −41.0%), maxDD 25.99% ✓ (≤55%), Sortino 1.77, SPY +7.3%
  (excess +22.4pp). **Posture ✗** (median 10.6% ✓ but 13 days >70% out-of-regime, Feb-27→Mar-15 melt-up block).
  **Breadth ✗** (6/20 eligible filled < 9; cannot-afford-zero-fills empty; concentration top1 46.8% MU — the 4-month
  window concentrated in the memory-supercycle names). Lockbox FAILED conditions 3–4; deploy proceeds by this override.

**Deploy build: MLT v16 `6a2b8434955c28672f64373b`** = certified-design family (v14) with the posture valves re-anchored
to the owner-blessed `OptionGrossExposurePercent` book-level deployment semantics: out-of-regime trims close winners
≥+50% above OGEP 68, ≥+20% above 74, ≥0% above 80. v16 validation: F2 +139.0% (Sortino 4.18, maxDD 33.9,
`6a2b844024b4b85b24a32c5f`), F3 +85.7% (3.18, 20.2, `6a2b844a955c28672f643773`; F3 median deployment 16.5%, Aug-Sep'25
violation block eliminated, Dec'25 melt-up block remains ~10 days).

**Live target pre-clone audit:** `69a7dc7acdb6bf6a4681d36c` ("Public Portfolio Challenge", live) held a prior book
(8 strategies incl. weekly LaunchAgent, deployed 2026-06-11) + 5 open long LEAP calls (ANET/XOM/HOOD/OSCR/COP Jan-Mar
2027, ≈$14.2k) + $14,692 cash. Clone REPLACES the strategy set (prior strategies archived, system orders cancelled);
open positions remain and are managed by v16's exits (DTE≤45, TP+100%, OGEP valves — all five names in universe).

**DEPLOY EXECUTED 2026-06-12 (explicit owner "Deploy"):**

1. Clone: v16 `6a2b8434955c28672f64373b` → live `69a7dc7acdb6bf6a4681d36c`; 8 strategies replaced 8 (prior book archived).
2. **Gate 7 (reproducibility on target): PASS.** Target backtest `6a2b86c8d39b9224ac2d7c32` (2025-05-30→2026-02-05,
   events on) vs chat-book run `6a2b844a955c28672f643773`: `compare_backtests tolerance_bps:0` → identical: true,
   zero tape divergence (return 85.66516774673401%, fees 128.70 — every digit equal).
3. Weekly monitor attached via `edit_portfolio addStrategies` (LaunchAgent: Monday OR CrossBelow(SPY, SMA200)=1,
   cooldown 1440, google/gemini-3-flash-preview ×2, maxIterations 15, brief = four kill-thresholds + per-spread P&L/DTE,
   owner-approval-only). **Verified by get_portfolio: 9 strategies live** — core/surge/extreme rebalancers (budgets
   28/10/30), DTE≤45 exit, TP+100, OGEP valve rungs confirmed 68/74/80 closing ≥+50/≥+20/≥0% winners, + monitor.
   Open positions intact (5 LEAPs).
4. **Gate 8 (live parity): PENDING-SAFE.** Live evaluator has not ticked since the clone (latest condition audits are the
   prior book's, 2026-06-11 19:54 UTC). Orders require manual approval, so nothing can fill pre-parity. REQUIRED before
   approving the first pending orders: pull `query_portfolio_events include_condition_audit:true` after the first
   post-deploy evaluation and compare every entry/regime indicator value (SPY 252d max ratio, per-name SMA150/ROC126,
   OGEP) against a same-day backtest of the target; material mismatch = decline all pending orders and report.
5. Live kill-thresholds in force per runbook: posture pause (median ≤55%, >70% only in regime), two-stage drawdown brake
   (pause ≥30%, owner review ≥55%), 12-week SPY-excess review (−15pp, review-only), order-health pause. Weekly monitor
   findings to be appended here.

**Deployed book — plain-English rules (MLT v16):**

- Universe: the fixed 20-name watchlist. All entries are long call structures, 150–365 DTE (furthest), first affordable
  rung of [ATM call → ATM/+20% vertical → ATM/+10% vertical → ATM/+3% vertical], 8% of portfolio per name.
- Core (out of regime only, every 14d): names above their 150d SMA, queued by 126d momentum, budget 28% of NAV.
- Opportunity surge (SPY < 0.92 × 252d high, every 7d): queued by 252d momentum, no trend filter, +10% budget.
- Extreme surge (SPY < 0.82 × 252d high, every 7d): same, +30% budget (≈68% max cost basis, crashes only).
- Exits: roll out at DTE ≤ 45; take profit at +100%; out-of-regime posture valves trim winners ≥+50% when
  OptionGrossExposurePercent > 68, ≥+20% above 74, ≥0% above 80. Declared opportunity regime: SPY/max252 < 0.92
  (extreme < 0.82) — matches the audit convention (252d trailing high, 0.92/0.82).

## PHASE 2 (2026-06-12, owner-directed): WF SWEEP → portfolio selection → WF GA → burnout → redeploy decision

Owner: the GA-only certification decision was wrong; do it properly. Plan: (1) walk-forward SWEEP optimization seeded
from the deployed v16; (2) pick a good portfolio from it; (3) walk-forward GA optimization; measure whether sweep
selection actually improves validation-set performance vs GA; (4) OOS burnout testing; (5) deploy unless a STRONG
reason not to (orders still gated on manual approval).

- Honesty note on (4): the lockbox (2026-02-05→2026-06-11) was single-touched by v16 at S2 and the design is now being
  iterated again → per the frozen rules that window is BURNED as a pristine certifier. No fresher tail exists (it ends
  at the run date), so burnout testing will use the WF OOS folds as primary evidence and the 2026 window as a
  disclosed second-touch check, not a clean lockbox.
- WF sweep config: compiled via `systematic_sweep preview_only + gene_intents` (the WF launcher has no gene_intents
  path — MCP friction noted). 5 genes seeded at v16's values: TP [75,100,150,200], cadence [10,14,21], budget
  [22,28,34], rank ROC window [none,63,126,189], OGEP valve [none,60,68,76]; 576 combos, generational, fitness
  [sortino, percentChange, maxDrawdown]. Compiler caveat: selectors are scope-All (uniform across strategies/sleeves) —
  winners must be inspected via their materialized portfolios.
- **CERT #3 launched:** study `6a2b94ecb932c3f68d9289bb` (engineKind Sweep, 4-fold anchored, same calendar as CERT #1/#2,
  148 units, 5,112.8 tokens). **DEAD ON ARRIVAL** — root optimizer went status ERROR with no error message while the
  study stayed RUNNING/PENDING (my config had stripped `form` blocks and lacked selectionPolicy/generationPolicy/
  exhaustiveThreshold). Superseded by #3b.
- Standalone exec probe `6a2b95f98d968d476f5cc9e7` (systematic_sweep, same gene_intents, 48 evals): RUNNING — proved the
  server-compiled config shape executes; its persisted config (with form blocks + policies) was lifted verbatim.
  **Probe's TP gene is tainted** (compiler bug below) — its results are not used for selection.
- **CERT #3b (the real sweep arm):** study `6a2b96a68d968d476f5ccac1`, root optimizer `6a2b96a68d968d476f5ccad8`
  confirmed RUNNING. Config = probe's persisted config with the TP gene hand-repaired (proper `Option position P&L % ≥
75/100/150/200` conditions), fitness [sortino, percentChange, maxDrawdown], 5,117.12 tokens.
- **CERT #4 (GA comparison arm):** study `6a2b9546b932c3f68d928a26`, GA pop 12 × gen 8, same seed/calendar/fitness as
  #3b — isolates engine choice for the sweep-vs-GA validation-transfer question. 1,156 units, 2,560.4 tokens.

- **Owner deployed WF-sweep fixes (`8528cafc94`):** generational billing (~6× cheaper), gene_intents accepted by the WF
  launcher, pre-charge validation, zombie studies now go ERROR. Old in-flight studies keep old billing.
- **CERT #3c (sweep arm, post-fix):** study `6a2ba29ad60148c60b2ed662`, gene_intents direct (geneWarnings []), 388 units,
  **859.52 tokens** (vs 5,117 pre-fix — billing fix confirmed). Same 4-fold calendar.
- **CERT #4 (GA arm) COMPLETE:** per-fold OOS [-8.05%, +40.45%, +248.36%, +276.47%], mean +139.3 / median +144.4,
  Sortinos [-4.05, 1.53, 4.22, 4.68] (agg 1.60), maxDD worst 43.1%, winnerStable false. Best GA result so far (bigger
  search + 3-fitness helped: fold-0 damage shrank from -41% to -8%), but still fails the fold-Sortino floor (-4.05 < 0.9),
  aggregate Sortino (1.60 < 1.9), and majority-folds vs A (F1 +40.45 just misses A's +41.46). Fold-0 selection pathology
  unchanged in kind: its winner had validation Sortino 7.03 on 3 names / 100% win rate, then went -8% OOS.

### Phase-2 outcome (2026-06-12, ~06:20 UTC)

- **Sweep arm: BLOCKED BY ENGINE BUG.** Four consecutive sweep executions died with root-optimizer status ERROR and an
  empty error field: CERT #3 (hand config), standalone probe `6a2b95f98d968d476f5cc9e7` (server-compiled, was RUNNING
  then flipped ERROR), CERT #3b (verbatim-lifted config), and post-fix CERT #3c `6a2ba29ad60148c60b2ed662` (pure
  gene_intents, root `6a2ba29ad60148c60b2ed669`). #3c's study doc also still says RUNNING (zombie-status fix did not
  propagate). Conclusion: the sweep EXECUTOR crashes on this options book regardless of config provenance; the
  sweep-vs-GA validation-transfer experiment cannot be completed until that is fixed. No further retries (owner's rule:
  don't re-feed an engine fault).
- **GA arm (CERT #4) delivered the candidate.** Fold-3 winner-equivalent materialized as chatPortfolio
  **`6a2ba33a229da6a48e74103c`** ("…opt 6a2b9546b932c3f68d928a3d #0", individual 6a2b97256e0c7568ec1d0127; resolved
  params: selectTopLimit 20, rollTriggerDte 35; train +68.7%/Sortino 1.59 over 2022→2024-09 incl. the bear; validation
  +73.0%/Sortino 4.81 with 18 names — first non-degenerate winner of the campaign).
- **Materialization parity caveat (MCP issue):** this book's standalone run over fold-3's exact OOS window returns
  +249.86%/Sortino 4.63/maxDD 31.2 (`6a2ba3671f9473b74e23c0ae`) vs the fold's certified +276.47% — train/val stats match
  the fold to all digits but OOS does not, and the fold's selectedIndividualId (…1d0052) differs from the leaderboard
  row (…1d0127). Materialized books may not carry every resolved gene. All deploy-relevant numbers below are measured
  DIRECTLY on `…103c`.
- **Burnout battery on `…103c`** (F0/F1/F2 are in-sample for this genome; last two rows are the honest ones):

| Window                                     | Return                  | Sortino | maxDD | Status                                                           |
| ------------------------------------------ | ----------------------- | ------- | ----- | ---------------------------------------------------------------- |
| 2023-05→2024-01 `6a2ba3601f9473b74e23c094` | +116.85%                | 2.98    | 32.7% | in-sample                                                        |
| 2024-01→2024-09 `6a2ba362229da6a48e74107b` | +143.25%                | 2.81    | 42.2% | in-sample                                                        |
| 2024-09→2025-05 `6a2ba364229da6a48e741091` | +136.33%                | 2.88    | 38.2% | validation-adjacent                                              |
| 2025-05→2026-02 `6a2ba3671f9473b74e23c0ae` | **+249.86%**            | 4.63    | 31.2% | **true OOS**                                                     |
| 2026-02→2026-06 `6a2ba36ad60148c60b2ed74b` | **+111.84%** (SPY +9.2) | 3.53    | 39.1% | **never seen by its optimizer** (2nd touch of window, disclosed) |

- Burnout-window audits: posture median 52.3% ✓, 11 days >70% out-of-regime (the known melt-up residual), breadth 15/20 ✓,
  top-1 SNDK 33.0% (memory-squeeze concentration on a 4-month window; concentration gate formally applies to fold devs).
- **Deploy decision:** no STRONG reason against; `…103c` dominates the live v16 on every honest window. Clone attempt
  blocked by the permission layer pending the owner naming the book explicitly. AWAITING OWNER CONFIRMATION.

- **CERT #3d (post executor-fix sweep):** owner shipped a sweep-executor fix; relaunched with identical gene_intents →
  study `6a2ba56ed60148c60b2eda8a`, root `6a2ba56fd60148c60b2eda91`, 388 units, 859.52 tokens, geneWarnings [].
  Outcome: dead (pre-deserialization-fix launch); superseded.

### Sweep-bug isolation ladder → RESOLVED (2026-06-12 ~07:55 CDT)

- DIAG A (trivial SPY stock book): executor fine (12 evals, leaderboard) → bug was options-specific.
- DIAG B1 (v16, 1 Integer gene, pre-deser-fix): ERROR, 0 evals → template DESERIALIZATION at fault, not gene type.
- DIAG B2 (post-deser-fix): 3/3 evals ran, then ERROR with empty leaderboard → crash moved to FINALIZE/persist step.
- DIAG B3 (`6a2c0142306e9cf756ede651`, post-finalize-fix): **COMPLETE, 3/3 evals — first options sweep ever to finish.**
  Both owner fixes verified end-to-end. Dead artifacts to ignore: CERT #3/#3b/#3c/#3d studies, probe `6a2b95f9…`,
  B1 `6a2ba62b…`, B2 `6a2bac25…`.
- **CERT #3e launched (the live sweep arm):** study `6a2c026599fc925d9b7ba685` (root `6a2c026699fc925d9b7ba68c`),
  engineKind Sweep, 5 gene axes via gene_intents, fitness [sortino, percentChange, maxDrawdown], 4-fold anchored
  validation on the standard calendar, 388 units, 859.52 tokens. Awaiting fold results; then sweep-vs-GA comparison
  (GA arm `6a2b9546b932c3f68d928a26`; GA candidate `6a2ba33a229da6a48e74103c` is the deploy bar: OOS +249.9%,
  2026 burnout +111.8%).

### CERT #3e RESULTS (sweep arm, COMPLETE) + the sweep-vs-GA answer

| Fold | Sweep OOS | Sweep Sortino | Sweep maxDD | names | GA OOS | GA Sortino |
| ---- | --------- | ------------- | ----------- | ----- | ------ | ---------- |
| 0 | **+21.27%** | 1.208 | 21.3% | 11 | **-8.05%** | -4.047 |
| 1 | +101.99% | 7.157 | 15.2% | 13 | +40.45% | 1.527 |
| 2 | +97.57% | 3.879 | 43.7% | 15 | +248.36% | 4.225 |
| 3 | +132.41% | 4.159 | 17.6% | 7 | +276.47% | 4.678 |
| Agg | mean +88.3 / med +99.8 / **min +21.3** | mean 4.10 / **min 1.21** | worst 43.7 | | mean +139.3 / min -8.05 | mean 1.60 / min -4.05 |

**Owner's question answered: YES — sweep selection materially improves validation→OOS transfer.** Deterministic grid
selection eliminated the degenerate-winner pathology entirely: every fold winner is a broad real book (7–15 names OOS),
all four folds positive, min-fold Sortino 1.21 vs GA's -4.05. Fold 0 — fatal in all three GA runs — transferred
faithfully (val Sortino 0.99 → OOS 1.21). GA buys higher peaks (folds 2-3) at the cost of catastrophic fold-0 tails;
sweep buys consistency. winnerStableAcrossFolds false in both (4 distinct sweep keys — regimes prefer different TP/budget).

### Sweep deploy pick + burnout

The fold-3 winner materialized as **`6a2c044d99fc925d9b7bacf6`**. Before trusting the leaderboard's genome labels we
pulled the actual book with `get_portfolio` — and they disagreed (the same materialization-parity class of MCP issue
seen with the GA pick, this time in the metadata rather than the results). What the book actually is:

- **Core sleeve** (SPY ≥ 0.92× 252d-high): fire every ≥14d, rank/select the full 20-name universe by 126-day ROC,
  limit 20, per-name 22% of buying power, sleeve budget 28% NAV, affordability ladder [ATM call → vert ATM/+20 →
  +10 → +3] at 150-365 DTE.
- **Dip sleeve** (SPY < 0.92×high): every ≥7d, select by 252-day ROC, budget 10% NAV.
- **Crash sleeve** (SPY < 0.82×high): every ≥7d, budget 30% NAV.
- **Exits:** roll at DTE ≤ 45; take-profit at **+100%** (the leaderboard claimed 150); froth valves intact but at
  **OGEP 95/110/130** (the display name still says 68/74/80), trimming winners ≥50/≥20/≥0% in-regime. No entry-side
  OGEP gate — the one genome label that was right.

The discrepancies change nothing downstream — every burnout number was measured on this exact book — but the lesson
repeats: only the deployable object is the truth.

Burnout, both honest windows:

- F3 standalone `6a2c047199fc925d9b7bad81`: **+137.51%** / Sortino 4.35 / maxDD 17.4 — within noise of the certified
  +132.4, so this candidate materialized faithfully.
- 2026 burnout `6a2c047699fc925d9b7bad9c`: **+107.37% vs SPY +9.2** / Sortino 5.99 / maxDD 25.5. Posture: median
  deployment 0% (sits in cash, then strikes), 30 days >70% out-of-regime during its Mar-Apr burst (same melt-up
  residual class as v16, lumpier since entries are ungated), and only 4 distinct names in the short window.

### Head-to-head for deploy (both measured directly on the deployable object)

| | Sweep pick `6a2c044d…bacf6` | GA pick `6a2ba33a…103c` |
| --- | --- | --- |
| Certification character | all 4 folds positive, min +21.3% | fold-0 negative in every GA run |
| F3 window | +137.5 / So 4.35 / DD 17.4 | +249.9 / So 4.63 / DD 31.2 |
| 2026 burnout | +107.4 / So 5.99 / DD 25.5 | +111.8 / So 3.53 / DD 39.1 |
| Breadth (F3/burnout) | 7 / 4 names (22% budget) | 15 / 15 names |
| Posture | median 0-low, lumpy >70 bursts | median 52.3, 11 >70-OOR days |

- Full 5-window battery on the sweep pick (first three are in-sample/validation-adjacent for this genome; last two honest):
  F0 +18.39%/So 1.31/DD 14.1 (`6a2c053499fc925d9b7bafa2`), F1 +37.34%/2.58/12.2 (`6a2c053792d9ca9c8d3b947d`),
  F2 +122.57%/7.06/11.3 (`6a2c0544306e9cf756edf1ad`), F3 +137.51%/4.35/17.4, 2026 +107.37%/5.99/25.5.
  Worst drawdown across ALL five windows: 25.5%. The book never breaches even half the 55% DD ceiling anywhere.

Held against the frozen gates, the sweep pick is not a clean pass — nothing in this campaign was. It clears the
return bar (Gate 2: +88.3% aggregate, beats Baseline A and SPY in 3 of 4 folds), the all-folds-positive test
(Gate 3), and the drawdown ceiling with room to spare (Gate 5: worst 25.5% vs a 55% limit). It misses on three
fronts: breadth thins out in recent windows (~7 distinct names in the F3 OOS, ~4 in the 2026 burnout, against a
≥9 bar that the 2023-24 windows do clear), fold-0's Sortino of 1.21 sits under the 2.37 Baseline-B floor, and no
single configuration won more than one fold. Posture is a half-miss: the median is fine, but deployment bursts
past 70% outside the declared regime because entries are ungated.

The breadth miss turned out not to be a miss at all. When asked directly, the owner's intent was eligibility, not
spread: every name should be *able* to participate, and they do — all 20 compete in the momentum rank at every
firing. The 4-7 name windows are just persistent 2025-26 leadership winning that rank repeatedly; in 2023-24 the
same book rotated through 9-10 names. Concentration into leaders is the design working as the owner wants it, so
the strict per-window distinct-name bar is waived. That removes the main structural objection.

**RECOMMENDATION: deploy the sweep pick `6a2c044d99fc925d9b7bacf6`.** Near-identical burnout return to the GA pick
at ~2/3 the drawdown and nearly double the Sortino, and it is the only candidate in the campaign whose certification
produced zero negative folds. What remains true and accepted: ~22% of buying power per position makes single-name
risk the dominant risk (it is where the 25.5% drawdown comes from), and its weakest regime is chop (fold-0: +21%,
Sortino 1.21 — positive, but it earns its keep in trends). The GA pick stays on file as the higher-upside,
higher-risk alternative. Awaiting the owner to name the book for the clone.

### CERT #5 — WF GA seeded from the sweep winner (2026-06-12)

Before deploying, the owner asked for one more arm: a walk-forward GA seeded from the sweep pick itself
(`6a2c044d99fc925d9b7bacf6`), to see whether GA mutation on top of the sweep-resolved genome finds anything better —
and which of the two we then want live. Launched with parameters identical to CERT #4 so the seed is the only
difference: 4-fold anchored, 2022-01-01 → 2026-02-05, pop 12, gen 8, fitness [sortino, return, maxDD], OOS width 252d,
Day interval. Study `6a2c0858089682c7acb1eb38`, root optimizer `6a2c0859089682c7acb1eb3f`, fold calendar verified
identical to the frozen one. Cost 2,562.56 tokens.

**Result: the GA degraded the winner in 3 of 4 folds.** OOS per fold: **-1.16%** (So -2.86, 2 names),
**-0.80%** (So -1.61, 2 names), **+153.06%** (So 3.68, but maxDD 48.0% — at the 55% ceiling's doorstep, 20 names),
**-26.52%** (So -0.86, 4 names). Aggregate mean +31.1% / median **-0.98%**, three negative folds,
winnerStableAcrossFolds false. The seed itself certified [+21.3, +102.0, +97.6, +132.4] on the same calendar.

The pathology is the same one documented in CERT #1/#2/#4, now reproduced a third time with the best possible seed:
folds 0, 1 and 3 selected low-activity mutants with 1-3 name, 100%-win-rate validation windows that promptly went
negative in OOS — fold-3's pick turned a +33.5%/Sortino 9.6 validation into **-26.5%** true OOS. Mutation found
validation luck, not alpha; the deterministic grid remains the only optimizer here whose validation performance
transfers. No candidate from this study merits burnout: the fold-3 winner (the deploy-relevant one) is an OOS loser.

**CERT #5 verdict: do not GA-polish the sweep winner. The deploy candidate stands: `6a2c044d99fc925d9b7bacf6` as-is.**

![Certified walk-forward OOS returns by optimizer](https://nexustrade-prod.nyc3.cdn.digitaloceanspaces.com/Blog/PublicPortfolioChallenge/ep10-sweep-vs-ga-oos-jun12.png)

*The three optimizer arms on the same frozen calendar. The deterministic sweep (blue) is the only one with no
negative fold; both GA arms (orange, red) buy taller peaks at the cost of catastrophic tails — even when seeded from
the proven winner.*

### DEPLOY #2 — sweep winner to the live book (2026-06-12)

On the owner's word ("let's deploy the sweep winner"), the certified book replaced v16 on the live target:

1. **Clone:** `6a2c044d99fc925d9b7bacf6` → `69a7dc7acdb6bf6a4681d36c` ("Public Portfolio Challenge", live). 9 prior
   strategies archived (v16 set + old monitor), 8 strategies copied. Open positions (5 LEAP calls) and cash
   (~$14.7k) untouched. The clone receipt echoed stale pre-sweep display names (the known MCP label issue);
   post-clone `get_portfolio` shows the correct resolved labels (TP +100%, valves ≥50/≥20/≥0%).
2. **Gate-7 repro: PASS, bit-exact.** Target backtest `6a2c0b84dd9e9fb055815995` (2025-05-30 → 2026-02-05, $25k,
   Day, events on): +137.5075% / Sortino 4.3499 / maxDD 17.351 — `compare_backtests` tolerance 0 vs the chat book's
   F3 run `6a2c047199fc925d9b7bad81`: identical=true, zero delta on every stat, zero tape divergence.
3. **Monitor re-attached:** weekly LaunchAgent (Monday OR SPY CrossBelow SMA-200, cooldown 1440, gemini-3-flash,
   maxIterations 15), prompt updated to the new book's mechanics (sleeves 28/10/30, TP +100%, valves 95/110/130,
   no entry OGEP gate) and adds a single-name concentration flag (any position whose loss would exceed 20% NAV).
4. **Verified:** live book = 9 strategies (8 certified + monitor), isActive, orders remain manual-approval.

**Gate-8 live parity: PENDING.** After the first live evaluator tick, pull `query_portfolio_events` with
`include_condition_audit` and compare indicator values against a same-day backtest BEFORE approving any pending
orders. The campaign's final deliverable is now live: the only candidate whose every certified fold and every test
window finished positive, deployed with a bit-exact reproduction proof.

## PHASE 3 (2026-06-12, post-deploy): the owner fixes the engine, and we ask the question again

Hours after DEPLOY #2, the owner shipped the engine work this campaign's failures pointed at, in a parallel session
(full trace: `NexusTrade/designs/optimization/cert6-ga-retest-live-log.md`). Three changes landed on the optimizer:

1. **The GA fold-winner bug is fixed.** Root cause of every degenerate winner in CERT #1–#5: `select_validation_winner`
   hardcoded validation-Sharpe ranking and ignored the configured fitness/constraints entirely. Fold selection now
   runs through the same constrained, degradation-penalized policy the sweep leaderboard uses.
2. **CERT #6** (that session, study `6a2c16476fe8883ed248c3a1`) retested CERT #4 with activity constraints
   (≥9 names, ≥35% participation). The constraints worked — every winner broad (11–15 names), no mutants — and the
   cert *still* got worse where it matters: fold-0 OOS −23.2% vs CERT #4's −8.1%, mean down to +99.5. Diagnosis
   unchanged from CERT #5: the degenerates were a symptom; the disease is short-validation-window noise against a
   huge genome space, and honest broad winners overfit it too. The fix is right to ship; it does not make GA WF a
   certifier.
3. **`backtest_only` certification mode now exists** — fixed book, train/val/OOS backtests per fold, no inner
   optimizer, `winnerStableAcrossFolds: true` by construction. Its maiden run certified an unrelated H10 book and
   honestly FAILED it (OOS +93.8 / **−33.2** / +117.7 / **−24.3**, worst DD 42%) for 12 units of compute. This is
   the certification instrument the runbook's design always wanted.

**Tape regression on the new image: PASS, bit-exact.** The deploy shares a binary with the backtest path, so before
anything else the live book's F3 window was re-run on the new image (`6a2c3039e495d50d8418d639`):
+137.5075198730467% / Sortino 4.349855707416185 / fees 29.90 — every digit equal to the pre-deploy Gate-7 run. The
deployed book's evidence chain survives the engine update.

On the owner's word ("we can try again"), two arms launched (~16:25 UTC):

- **CERT #3f** `6a2c32669b8c4fff97dfc97c` (root `6a2c32679b8c4fff97dfc984`, 388 units, 859.52 tokens) — byte-for-byte
  rerun of the CERT #3e config (same v16 seed, same 5 gene_intents, same calendar) on the new engine. Purpose:
  the unified-selection refactor touches the sweep WF path that certified the DEPLOYED book; this checks that path
  still produces ≈ [+21.3, +102.0, +97.6, +132.4]. Pre-registered expectation: reproduce.
- **SWEEP v2** `6a2c329fe7f9f85975da89f3` (root `6a2c32a0e7f9f85975da89fa`, 1300 units, 2881.88 tokens) — the
  genuinely new search: seeded from the deployed winner `6a2c044d…bacf6`, five axes the first sweep never explored
  (per-name allocation 10/14/22, cooldown 14/21/30, roll DTE 35/45/60, rank window 126/189/252/keep, TP 100/150/200),
  with a constrained selection policy (participation ≥0.25, validation return ≥0, Sortino primary). If its fold-3
  winner beats the deployed book on certification AND the burnout battery, it becomes a redeploy candidate;
  otherwise the live book stands.

- **CERT #7** `6a2c343dc400a53b0a4c6c75` (root `6a2c343dc400a53b0a4c6c7e`, 1156 units, 2562.56 tokens) — launched
  once the owner deployed the MCP `fold_selection_policy` field. GA on the v16 seed, CERT #4 parameters, full
  certification quality gates (participation ≥0.35, names ≥9, validation return ≥0, validation Sortino ≥0.5,
  degradation penalty 0.5). Pre-registered prediction: fold-0 improves vs CERT #6's −23% because the gates exclude
  its negative-validation winner, but the arm stays below deploy grade — a fold-0 `NoEligibleCandidate` hard fail
  is a live possibility and would itself be the correct, informative outcome.

Methodology note, logged before results: these are the seventh through ninth studies scored on the same four OOS
windows. The folds are no longer pristine — fine for engine regression and search, but any redeploy decision will
lean on the 2026 burnout window and live performance, not the increasingly-seen calendar.

### Phase-3 results (~16:45 UTC): all three arms resolved, live book stands

**CERT #3f — not a reproduction, a semantic change (as the refactor intended).** Same grid, same seed, same
calendar as CERT #3e, but the unified selector picked a different winner in every fold — fold winners were
previously raw validation-Sharpe argmax; they now go through the configured policy. New OOS:
[+31.6, +63.6, +90.9, **+1016.9**] vs #3e's [+21.3, +102.0, +97.6, +132.4]. All folds positive, min fold improved,
all winners broad (14–16 names). Implication for the record: CERT #3e's numbers are an artifact of the OLD selector
and are not reproducible on the new engine — but the deployed book's own evidence (standalone backtests, burnout
battery, Gate-7 bit-exact repro) is book-level and unaffected.

**The +1017% wild card: killed by burnout, spectacularly.** Fold-3's winner materialized faithfully as
`6a2c36249b8c4fff97dfce71` (F3 standalone `6a2c36439b8c4fff97dfcea6`: +1028.8% / Sortino 9.45 / DD 32.5 — parity ✓).
Then the 2026 burnout (`6a2c3644e7f9f85975da9261`): **−35.6%, maxDD 49.0%** — a third of NAV gone in four months,
brushing the 55% kill ceiling, on the same window where the deployed book made **+107.4% at DD 25.5**. This is the
campaign's single cleanest proof that certified fold returns — even from an honest, constraint-selected,
deterministic grid — can be pure regime fit. The burnout window is not optional.

**SWEEP v2 — stabler, broader, and not better.** OOS [+17.9, +13.4, +90.6, +97.1], all positive, drawdowns the
lowest of any arm (worst 32.7%, fold-0 only 8.5%), and a campaign first: one candidate (`b8cd2099…`) won BOTH
folds 0 and 1 — the first repeated fold winner in nine studies. But the fold-3 winner certifies at +97.1% vs the
deployed book's +132.4%, failing the pre-registered redeploy condition at the first hurdle. No burnout needed;
the family is a lower-octane cousin of the live book, worth remembering if the owner ever wants a calmer variant.

**CERT #7 — GA's third strike, delivered by the engine itself.** Fold-0 selected a winner that passed every
quality gate (14 names, 0.70 participation, validation +4.6% / Sortino 1.37) and still went **−14.7%** OOS
(DD 45.4%). Fold-1 then hard-failed with the new enriched error: *"no individual passes fold selection constraints
on validation statistics (every candidate violated at least one configured floor)"* — the `NoEligibleCandidate`
outcome working exactly as designed, and the honest answer: in that window the GA bred nothing worth certifying.
GA fold-0 has now failed under three selectors — buggy (−8%), activity-constrained (−23%), fully gated (−15%).
The pathology is structural, not a selection bug. Engine notes for the owner: the error message now propagates
properly (vs the empty-error zombie era — fixed and verified), but the study charged its full 2,562.56 tokens
while completing 577/1156 units before the hard fail; partial-failure billing may deserve a look. Also: CERT #3f's
leaderboard rows display zeroed validation stats and stale-looking parameter labels (same display-layer issue class
as before; the materialized objects are correct).

**Phase-3 verdict: the deployed book survives its third gauntlet.** Re-asked with a fixed engine, wider genes,
constrained selection, and three optimizer arms, the answer is unchanged — nothing produced a candidate that beats
`6a2c044d99fc925d9b7bacf6` on certification AND burnout. The strongest challengers each failed exactly one of the
two, which is precisely why both are required. Live book stands; Gate-8 live parity remains the only open item.

### CERT #8 — the validation-window hypothesis, tested (owner-directed, engine QA only)

Every post-mortem in this log blamed the same suspect: GA selection overfits because the fold validation windows
are short (8–14 weeks under the default 80/20 dev split). CERT #8 tests exactly that and nothing else: identical
to CERT #7 (v16 seed, pop 12 × gen 8, frozen OOS calendar, full quality gates, degradation 0.5) except
`validation_percent: 50` — fold validation windows stretch to 8–20 months, spanning regime changes instead of
sitting inside one. The OOS windows are unchanged, so fold-for-fold comparison is clean. Study
`6a2c50e575bb49474ae1e87b` (root `6a2c50e575bb49474ae1e884`, 1156 units, 2,562.56 tokens).

**Result: hypothesis confirmed — this is the best certification of the entire campaign, from either engine.**

| Fold-0 OOS across GA arms | selector | result |
|---|---|---|
| CERT #4 | buggy (val-Sharpe argmax) | −8.1% |
| CERT #6 | activity constraints | −23.2% |
| CERT #7 | full quality gates | −14.7% (then fold-1 NoEligibleCandidate) |
| **CERT #8** | full gates + **50% validation** | **+66.3%** |

Full CERT #8 OOS: **[+66.3, +137.7, +124.5, +366.7]** — all four folds positive, mean +173.8 / median +131.1,
Sortinos [1.89, 2.84, 3.33, 5.76], worst maxDD 33.7%, every fold winner broad (10–20 names, participation
0.5–1.0). Fold-for-fold it beats the sweep cert (CERT #3e: +21/+102/+98/+132) everywhere. Selection noise — not
GA breeding, not gate strictness — was the binding constraint all along: give the selector a validation window
long enough to contain a regime change and validation→OOS transfer appears, even for GA.

Honest caveats, logged with the result: (a) winnerStableAcrossFolds is still false; (b) fold-0's Sortino 1.89
still sits under Baseline B's 2.37 floor; (c) the 50% split halves the training window (fold-0 trains on 7.5
months of pure bear), so this trades breeding data for selection honesty; and (d) this is the tenth study scored
on these OOS folds, and the 50% idea was itself motivated by watching the previous nine fail — a researcher
degree of freedom the folds have now absorbed. Per the owner's instruction this was engine QA only: **no
redeploy**. If any CERT #8 winner is ever considered for deployment, the bar is unchanged — materialize the book,
verify parity, and survive the 2026 burnout window that just executed the +1017% pretender.

### CERT #8 burnout + the bestiary: what every version of this strategy actually does

The owner asked the right question — strip the study IDs and say what each book *does*. Every materialized
candidate was pulled with `get_portfolio` and read condition-by-condition (labels lie; objects don't). They are
all one organism: the **MLT skeleton** — 20-name universe, three regime sleeves (core: market near highs, every
14d, top names by 126-day momentum; dip: SPY <0.92× its 252d high, every 7d, by 252-day momentum, +10% budget;
crash: <0.82×, +30% budget), an affordability ladder of 150–365 DTE ATM calls → call verticals, budgets ~28/10/30%
of NAV, and exits (roll near expiry, take profit, OGEP froth valves). Every optimizer arm just moved three levers:
**per-name size, take-profit level, roll timing.**

| Book | The three levers (verified on the object) | Personality | F3 window | 2026 burnout |
|---|---|---|---|---|
| **v16** (deploy #1, override) | 8%/name of portfolio, TP +100, roll 45, valves 68/74/80 | the balanced template | +85.7 / DD 20.2 | lockbox +23.4 |
| **Sweep winner (LIVE)** `6a2c044d` | **22%/name of buying power**, TP +100, roll 45, valves loosened to 95/110/130 | concentrated conviction — 1-2 leaders at a time, sits in cash between strikes | +137.5 / DD 17.4 | **+107.4 / DD 25.5 / So 5.99** |
| GA pick (CERT #4) `6a2ba33a` | 8%/name, roll 35, top-20 | broad v16, slightly faster recycling | +249.9 / DD 31.2 | +111.8 / DD 39.1 |
| CERT #3f wild card `6a2c3624` | 28%/name of BP, 63-day rank, **all exits gated by "P&L ≥ 75%"** — losers can never be closed (gene-compiler cross-talk ANDed the TP gene onto every CloseOption incl. the DTE roll) | ride-or-die: winners run, losers ride to zero | +1028.8 / DD 32.5 | **−35.6 / DD 49.0** |
| SWEEP v2 winner `6a2c5428…f010` | **14%/name of BP**, TP +150, roll 35-60 (didn't bind) | the live book, diversified — more names, calmer path | +97.1 cert / DD 15.1 | not run (lost cert head-to-head) |
| **CERT #8 winner** `6a2c539b…ef0e` | 8%/name of portfolio, **TP +185**, **roll 33**, valve triggers GA-mutated (+179/30d-hold, +38/4-DTE, +43) | broad and patient — 17-19 names, lets winners nearly triple, recycles expiring options early | **+194.6 / DD 27.1** | **+132.6 / DD 36.5 / So 3.48** |

**CERT #8 winner: the first challenger to survive every test.** The full five-window battery, measured directly
on the deployable object (`6a2c539b75bb49474ae1ef0e`), head-to-head with the live book:

| Window | CERT #8 winner | Live book (deployed) |
| --- | --- | --- |
| F0 2023-05 → 2024-01 | **+97.6%** / So 2.80 / DD 27.4 / 16 names (`6a2c574e75bb49474ae1f53c`) | +18.4% / So 1.31 / DD 14.1 |
| F1 2024-01 → 2024-09 | **+208.2%** / So 3.74 / DD 34.5 / 19 names (`6a2c575075bb49474ae1f552`) | +37.3% / So 2.58 / DD 12.2 |
| F2 2024-09 → 2025-05 | **+226.2%** / So 4.01 / **DD 54.3** / 20 names (`6a2c5753957d1c9f1ef4fa84`) | +122.6% / So 7.06 / DD 11.3 |
| F3 2025-05 → 2026-02 | **+194.6%** / So 4.26 / DD 27.1 / 19 names (`6a2c53b675bb49474ae1ef87`) | +137.5% / So 4.35 / DD 17.4 |
| 2026-02 → 2026-06 burnout | **+132.6%** / So 3.48 / DD 36.5 / 17 names (`6a2c53b83eb2e9a34a1ec80d`) | +107.4% / So 5.99 / DD 25.5 |

It out-returns the live book in **every window** — often by 2–5× — with 16–20 names participating everywhere,
the best breadth of the campaign. A milestone no other candidate reached: its window Sortinos
(2.80 / 3.74 / 4.01 / 4.26) clear **all four 90%-of-Baseline-B floors** [2.37, 1.69, 1.61, 0.97] — the gate that
killed every previous candidate, including the live book (fold-0). Held against the frozen gates this is the
cleanest pass the campaign has produced: Gate 1 breadth ✓ (16–20 ≥ 9 everywhere), Gate 2 returns ✓ (smashes every
bar), Gate 3 all-folds-positive ✓ (certified [+66, +138, +125, +367]), Gate 4 Sortino-vs-B ✓ (first ever),
Gate 5 drawdown ✓ — **by 0.73pp** (F2 window maxDD 54.27% vs the 55% ceiling). Gate 6 posture: not yet audited
(open item).

**The flag, stated plainly:** the F2 window's 54.3% drawdown is an already-observed path, not a tail hypothesis.
Live, that path trips the 30% drawdown brake mid-decline and asks the owner to keep approving orders while the
book is cut in half — it finished that window +226%, but only for someone who held. The owner has stated the risk
is accepted. The trade on offer vs the live book: roughly double the return for roughly double the drawdown, far
more breadth (single-name risk largely gone — 8%/name vs the live book's 22%-of-BP), lower Sortino.

**Recommendation: deploy `6a2c539b75bb49474ae1ef0e` on the owner's explicit word** (permission layer requires the
book named). Pre-deploy items pending: owner is fixing the exit-gene compiler bug first; after that engine deploy,
re-verify the tape (tolerance-0 repro of this book and the live book on the new image) and run the Gate-6 posture
audit before the clone. Caveats carried into the decision: exits are GA-mutated values (TP +185%, quirky valve
triggers) — unprincipled but mechanically verified sane and empirically robust across all five windows; the
certified +366.7% belongs to the genome, the deployable object's own numbers are the table above.

Engine notes from this round (for the owner): (1) **GA materialization parity gap recurs** — fold-3 certified
+366.7% but the leaderboard book (validation stats identical to all digits) scores +194.6% standalone;
selectedIndividualId ≠ leaderboard individualId, GA arms only — sweep books have materialized faithfully every
time. The honest number is always the deployable object's. (2) **GA `resolvedParameters` under-report** — the
display showed only {selectTopLimit, rollTriggerDte} while the actual object also carried mutated TP (+185) and
valve triggers. (3) **The CERT #3f wild card exposed real gene-compiler cross-talk**: the take-profit gene ANDed
`Option position P&L % ≥ 75` onto every exit strategy's condition — including the DTE-45 roll — creating a book
that structurally cannot cut losers. Any sweep whose exit gene compiles this way will look like a genius in
melt-ups and a disaster everywhere else; this is the single most dangerous silent failure found all campaign.

The arc of the whole campaign in one sentence: every optimizer, given honest selection, rediscovers the same
trade-off — concentration buys Sortino, breadth buys return, exits decide survival — and the only books that died
were the ones whose exits were broken.

**Contamination audit after the owner's exit-gene fix (object-level, `6a2c542875bb49474ae1f010`):** SWEEP v2's
results STAND — its exit operands compiled to benign `AND always`, exits reachable for losers. But the audit
surfaced that the TP axis has been dead or poisoned in every sweep ever run (CERT #3e no-op, CERT #3f poisoned,
SWEEP v2 no-op): **no sweep has ever honestly tested take-profit on this family.** It also caught two more shapes
of the same applicator flaw — the roll gene sprays its DTE trigger onto every CloseOption, and genes STACK on
re-swept seeds ("Entry cooldown AND Entry cooldown") — both benign here, both added to the fix-verification list.
Post-fix plan (research, not a deploy gate): one small clean sweep on the CERT #8 seed, TP {100, 150, 185, 200} ×
roll {33, 45}, which simultaneously validates the owner's fix end-to-end and gives the first honest answer to
whether the deploy candidate's GA-mutated TP +185 is load-bearing or incidental.

## DEPLOY #3 AND THE GATE-8 CATCH (2026-06-12 evening): the names were lying to everyone

The CERT #8 winner was deployed and reverted within three hours, and the failure taught the campaign its deepest
lesson. Full sequence, honestly:

**The deploy (19:31–19:45 UTC).** Owner accepted the risk profile and gave the word. Pre-deploy checks all green:
tape regression bit-exact on the post-fix engine, Gate-6 posture audited (burnout window clean; F2 crash-window
median 67% acknowledged and accepted by the owner), chain cache verified live (the old book's SNDK signal resolved
into a real Mar-2027 vertical at 19:31 after an afternoon of `OPTION_CHAIN_EMPTY_FOR_REQUESTED` — a server-side
cache outage that had silently blocked all order generation). Cloned `6a2c539b…ef0e` → live at ~19:35, Gate-7
bit-exact, monitor attached.

**The catch (19:45).** The new book's first live tick fired BOTH regime sleeves simultaneously — impossible with
sane logic — and the condition audit showed why: the evaluated conditions were `DaysSinceFired ≠ 141` and
`SPY ≠ 95.26 × 1634-day max`, trivially true garbage. Gate-8 failed on the first tick, orders were quarantined in
manual approval, nothing filled.

**The root cause (after two wrong theories).** Not the live-trading deploy; not a corrupted clone. The candidate's
conditions were GA-mutated AT BIRTH — CERT #8's optimizer legitimately mutates comparators, constants, and window
lengths (that is what open-ended GA search is), and the fold's statistics gates measure performance, not genome
sanity. The killer: **the display names never regenerate after mutation.** Every layer — leaderboard strings,
strategyNames, and the `condition.name` fields inside the stored objects — still read `≥ 14 / 0.92 / 252` while
the actual `comparison`/`value`/`window` fields underneath read `≠ 141 / 95.26 / 1634`. This log's own "verified
on the object" claims for the CERT #8 genome were fooled: the verification script printed condition *names*, not
fields. (The trigger values — TP +185.2, roll 33 — were real fields and remain correct.)

**What that makes of the CERT #8 evidence — the strangest finding of the campaign.** Decoded at field level, the
mutated genome is a coherent accidental strategy: always-true entry gates, dead crash sleeve, dead valves —
i.e. "buy top-20 momentum daily within ~38% budget, TP +185%, roll at 33 DTE, no regime machinery at all."
**Every number in the five-window battery above was honestly measured on exactly those semantics** (Gate-7's
bit-exact source≡target proof guaranteed we always measured the stored logic — it just wasn't the logic the names
described). So the battery stands as data about a strategy nobody designed; the strategy everyone THOUGHT was
deployed has never been tested.

**Also resolved: the +366.7% certified fold winner is unreachable by design.** The leaderboard materializes the
root optimizer's final population (12 individuals, checked exhaustively) — the per-fold `selectedIndividualId`s
are never among them. Certified GA numbers and deployable GA books were systematically different objects all day
(+366.7 vs +194.6 here; +276.5 vs +249.9 for the CERT #4 pick).

**The owner shipped fixes the same evening (`b650f78d31` + follow-ups):** GA mutation now clears stale names and
materialization regenerates labels; `get_walk_forward_study_results` now materializes each fold's actual
`selectedIndividualId` (returns `selectedChatPortfolioId`); `get_optimization_results` adds a per-row
`conditionFieldAudit`. New protocol, permanent: **Gate-7/Gate-8 verification reads `comparison`/`value`/`window`
fields, never names.**

**RE-CORRECTION to the sweep-pick record above:** the same stale-name trap claimed an earlier victim in this log.
The morning "CORRECTION" asserting the deployed sweep winner's valves sat at OGEP 95/110/130 was itself read from
stale names — the raw fields say **68/74/80** (the display name "OGEP posture 68/74/80" was right all along), and
the cooldown fields are 14∧21 / 7∧21 / 7∧21, i.e. effectively 21 days everywhere — matching the leaderboard's
reported genes, which were never wrong for this book. The sweep materialization pipeline was honest; only the GA
one mutated under stale labels.

**REVERT (DEPLOY #4, ~20:45 UTC): the sweep winner is back on the live book, verified at field level.**

1. Source `6a2c044d99fc925d9b7bacf6` audited on raw fields: core ≥14 ∧ ≥21 ∧ SPY ≥ 0.92×252d-max; dip < 0.92;
   crash < 0.82; roll DTE≤45 unconditional; TP pnl≥100 unconditional; valves OGEP 68/74/80 trims ≥50/≥20/≥0. Clean.
2. Cloned → `69a7dc7acdb6bf6a4681d36c`; target re-audited on raw fields: **identical, field for field** (the new
   clone path even strips the legacy no-op `1=1` operands).
3. Gate-7: target backtest `6a2c70dd4d76579261903285` vs the original deploy-day baseline `6a2c0b84dd9e9fb055815995`
   at tolerance 0: **identical=true, zero tape divergence** — same book, same evidence chain as this morning's
   DEPLOY #2.
4. Monitor re-attached with a new fifth kill-threshold: **condition integrity** — the weekly audit now verifies
   raw fields against the expected genome and treats any deviation as pause+alert.
5. Orphaned pending orders: none remain — strategy replacement auto-cancels pending orders (owner-confirmed),
   so the CERT #8 book's OSCR/MU set and the pre-clone SNDK pair died with their strategies. Gate-8 live parity
   re-check runs at the next market tick (Monday open), reading evaluated condition FIELDS.

**Postscript — the +366.7% genome is gone forever.** With the owner's materialization fix live,
`get_walk_forward_study_results` on CERT #8 now attempts to materialize each fold's `selectedIndividualId` — and
every fold returns `materializationError: "selectedIndividualId not found in individuals collection"`. The
per-fold winners were never persisted; only the final-generation population survived the run. The number that
headlined CERT #8 belongs to a genome that no longer exists anywhere, which is the materialization-parity gap's
final form: pre-fix GA certifications are unfalsifiable history. Future GA studies on the fixed engine persist
their fold winners; for this one, the book of record is and will remain the leaderboard sibling (`6a2c539b…`)
and its honestly-measured +194.6%.

The day ends where it began — the sweep winner live, now with its conditions proven at the only layer that
trades. The CERT #8 family goes back to research: the owner can extract true fold winners via the new
`selectedChatPortfolioId` path, and the "accidental always-on book" remains a genuinely interesting data point
that earned its five-window numbers fairly and was deployed under a name that described a different strategy.

### Fix validation round (late evening): the TP axis finally exists, and the audit instrument works

With the owner's naming/materialization/TakeProfitPct fixes live, three validation runs closed out the night:

- **FIX-VAL d** `6a2c73654d765792619034a2` (TakeProfitPct × RollTriggerDte on the accidental CERT #8 seed,
  hand-authored config with the correct `scope: Action`): the TP gene **works** — all 8 cells real and distinct,
  the first live take-profit axis in any sweep. The new per-row `conditionFieldAudit` immediately exposed the
  seed's poisoned conditions (`notEqual 141`, `≠ 95.26 × 1634d max`) right in the leaderboard — the instrument
  this morning's incident was missing. Fold-1's `NoEligibleCandidate` hard fail was verified HONEST: all 8 cells
  had negative validation returns in that window, and the `percentChange ≥ 0` floor correctly refused them all.
  Lesson recorded: earlier "invalid target field" rejections were this operator hand-authoring the wrong scope
  (`Strategy` instead of `Action`) — the supported path is `gene_intents`, where the compiler and validator do the
  field discovery (and now explicitly redirect P&L-exit intents to TakeProfitPct).
- **One persistence gap remains, now with a clean repro:** this brand-new post-fix study STILL reports
  `materializationError: "selectedIndividualId not found in individuals collection"` on its completed fold —
  the fold-winner persistence fix is not reaching sweep studies. (CERT #8's missing winners are unrecoverable
  history; this one is a fresh, fixable case.)
- **TP-HONEST** `6a2c7420aab6fc246d750efb` — the experiment that matters: TP {75, 100, 150, 200} × roll {33, 45}
  on the CLEAN live book (`6a2c044d`), gene_intents path, val 50%. The first honest answer to "is the live book's
  TP +100 the right take-profit" in campaign history.

**TP-HONEST results: the live book's TP +100 survives its first honest challenge.** Study COMPLETE, all four
folds positive: OOS [+22.2, +37.6, +111.7, +99.4], mean +67.7, worst fold maxDD 24.8. The `conditionFieldAudit`
on every variant shows clean fields (≥14 / 0.92 / 252) — the clean seed propagated correctly through the fixed
applicator, no spray, no stacking. Two findings:

1. **TP 75% won folds 1 AND 3** (dominant candidate, the first time any config repeated in a sweep with the TP
   axis alive) — but its fold-3 OOS of +99.4% sits well BELOW the incumbent TP-100 book's +137.5% on the same
   window. The sweep preferred TP 75 on validation (−15.3 vs −17.7 in a window where every variant scored
   negative) and the preference did not pay out-of-sample. Verdict: no TP variant produced evidence to displace
   the live book's +100; the incumbent stands, now with the first honest TP reading behind it instead of a
   dead axis.
2. Oddity flagged for the owner, not chased tonight: every cell's fold-3 validation return was negative
   (−15 to −18) over 2023-09→2025-05, a span where this book family gained strongly in standalone backtests —
   worth a look at how fold-validation evaluation seeds its starting state.

**Persistence gap, third clean repro:** all four folds of this brand-new gene_intents study also report
`materializationError: "selectedIndividualId not found in individuals collection"` — sweep WF fold winners are
still not persisted post-fix.

### Verification round after the full-stack persistence deploy (owner workflow followed exactly)

New tooling exercised end-to-end on a fresh study (**PERSIST-VAL** `6a2c7cf74024704b66dcdf89`, TP {100,150} ×
roll {35,45} on the clean live-book seed, gene_intents, val 50%):

- `get_sweep_surface` ✓ — full field catalog, default genes, and the TakeProfitPct/Action rule stated in guidance.
- `preview_only` ✓ — compiled genes (correct scope/field) and cost returned before any billing.
- **Fold-winner persistence: PARTIAL.** Folds 0 and 3 returned `selectedChatPortfolioId` (`6a2c7de2fc767c83e41150bb`
  — same winner key won both, correctly deduped). Folds 1 and 2 still `materializationError`: their shared winner
  individual (`…d4b2`) is absent while folds 0/3's (`…d4b4`) persisted. One study, both behaviors — clean repro
  for the owner.
- **Field audit of the persisted winner** (`6a2c7de2…`, TP150/roll35): conditions clean (≥14 / 0.92 / 252),
  TakeProfitPct correctly wrote the pnl trigger (150). **But RollTriggerDte still sprays**: its `dte ≤ 35`
  trigger was appended to the TP strategy and ALL THREE valves, not just the roll — the applicator-scope flaw
  flagged this afternoon survives the fix wave.

**And the big one — fold-validation evaluation is unfaithful (S0.2-class defect, now proven).** The live book
itself IS the TP100/roll45 cell of these sweeps. Standalone backtest over fold-3's exact validation window
(2023-09-16 → 2025-05-29): **+195.86%** / Sortino 2.31 / 17 names (`6a2c7cc4fc767c83e4114ee1`). The fold
evaluation reports that identical genome over that identical declared window at **−17.71%** — reproduced in BOTH
TP-HONEST and PERSIST-VAL. A 213-point gap on the same object and window means sweep-WF fold-winner selection is
currently driven by numbers that do not describe the declared validation segment. Consequences: TP-HONEST's
"TP 75 preferred" verdict is VOID (selection noise on corrupted stats — consistent with its OOS underperforming
the incumbent); any sweep-WF certification's winner CHOICE is suspect until fixed, though the OOS measurement
path appears intact (CERT #3e fold OOS matched standalone within window-boundary tolerance, S0.2-style). The
live book is unaffected: its standing evidence is standalone-measured.

**Forensic box for the validation defect (three measurements, one corner):** for the identical genome
(live book ≡ TP100/roll45 cell) over fold-3's declared validation window 2023-09-16 → 2025-05-29:

1. Fresh-start standalone: **+195.86%** (`6a2c7cc4fc767c83e4114ee1`) — rules out "evaluation is honest".
2. Continuation of the training run, measured over the same sub-span (`6a2c7e419b5374cbeb807c9e`, full
   2022-01-01 → 2025-05-29 run, equity 51,430.92 → 98,613.08 across the sub-span): **+91.74%** — rules out
   "validation inherits training state".
3. Reported validation: **−17.71%** — and identically −17.71 for TP100, TP150, AND TP200 at BOTH roll values
   (only TP75 differs, at −15.29). Identical stats across six genomes that differ in roll timing and TP level
   means the evaluated span is one where (a) no position ever reaches +100% (so TP 100/150/200 never separate)
   and (b) no position ever ages into its roll trigger (so roll 33 vs 45 never separate) — i.e. a SHORT window,
   and a negative one. The evaluator is scoring some short negative sub-span, not the declared 20-month segment.
   Owner has the code; the campaign has the receipts.

### THE VALIDATION FIX LANDS (`faadf93005`) — and the fixed engine re-elects the live book

The owner's diagnosis matched the forensic box exactly: sweep fold scoring had been using `trainingPercent` on the
GLOBAL range with a truncated holdout (`training_windows.count` instead of `validation_windows.count`) — the
"short, wrong sub-span" in person. Fixes deployed: fold-calendar dates for sweep scoring, full validation window,
OosScoring with proper earliest_date, fold-winner individuals protected from batch-save overwrites, plus a
permanent E2E gate (`make walk-forward-sweep-e2e`). Trust boundary declared: post-deploy sweep studies trusted;
pre-deploy sweep studies' validation-driven winner choices are not (CERT #3e and SWEEP v2 winner SELECTIONS
included — their OOS measurements stand, the choices among cells do not).

**PERSIST-VAL-2** (`6a2c8f559b5374cbeb809443`, identical config to PERSIST-VAL, post-fix engine) — every check:

- **Validation scoring: FIXED.** Fold-3 winner's validation is +232.4% over the real 20-month window (was −17.71
  garbage). Fold validation numbers now look like the windows they claim to describe.
- **Persistence: FIXED.** 4/4 folds returned `selectedChatPortfolioId` (`…9538`, `…953c`, `…9540`, `…9544`).
- **Materialization + field audit: PASS.** Fold-3's winner book audits clean at field level (≥14/0.92/252,
  TP trigger 100, roll 45). The roll-spray gap remains (dte triggers appended to TP/valves — owner-acknowledged,
  behaviorally inert here since the value equals the seed's own roll).
- **The poetry: with honest validation stats, the sweep's fold-3 winner IS the live book's exact configuration**
  (TP 100 / roll 45). Its fold OOS: +132.408 / Sortino 4.159 / DD 17.6, dollarsSold 240,847.998 — the identical
  trade tape as the live book's standalone F3 run (the small return delta vs +137.51 is the known OOS-boundary
  day). The deployed configuration, whose original CERT #3e selection ran on corrupted validation numbers, has
  now been re-selected by the repaired engine on honest ones — the live book's certification lineage is restored,
  this time on arithmetic that checks out.

Post-fix open list (owner-acknowledged): RollTriggerDte trigger spray, gene stacking on re-sweep, GA
materialization parity, partial-fail billing, zeroed mid-run leaderboard stats, E2E gate not yet in CI.

### CERT #3g — CERT #3e's FULL grid re-run on the fixed engine: the pristine record does not survive

This is the honest one. PERSIST-VAL-2 re-elected the live book, but it only swept TP × roll on a narrow grid where
the deployed config (TP100/roll45) was the obvious winner. CERT #3g re-runs CERT #3e's **entire original 5-gene
grid** (TP, cooldown, budget, ROC window, OGEP gate — 388 units, same calendar) on the corrected validation
engine — the real test of whether the deployed book's certification reproduces. Study `6a2cbd479b5374cbeb80cbf5`.

**It does not.** Side by side:

| | CERT #3e (corrupted validation) | CERT #3g (fixed validation) |
| --- | --- | --- |
| Fold-0 OOS | +21.27% | **−1.59%** |
| Fold-1 OOS | +101.99% | +58.71% |
| Fold-2 OOS | +97.57% | +115.79% |
| Fold-3 OOS | +132.41% | +89.13% |
| Aggregate | mean +88.3, **min +21.3, all positive** | mean +65.5, **min −1.59, one negative** |
| Fold-3 winner | TP100 / 22%-name / no-OGEP-gate = **the deployed book** | TP75 / 28%-name / OGEP-gated = **a different book** (field-audited, clean) |

Two hard conclusions, stated without spin:

1. **CERT #3e's headline — "all four folds positive, min +21.3%, the only campaign candidate with zero negative
   folds" — was partly an artifact of corrupted validation selection.** On honest validation, the same grid with
   the same (no-constraint) selection policy picks a thin 5-name, 0.25-participation, −8.4%-validation winner at
   fold-0 that goes −1.59% OOS. The pristine record that justified DEPLOY #2's "most robust candidate" framing
   does not reproduce on the fixed engine.
2. **The full grid no longer re-selects the deployed book at fold-3.** Honest validation prefers a TP75/28%
   variant (validation +130.5%) whose OOS is +89.1% — lower than the deployed book's own +137.5%. The selector,
   now honest, is choosing a worse-transferring cell: a clean live demonstration that validation-optimal ≠
   OOS-optimal, which is the entire reason walk-forward exists.

**What this does and does not change:**
- The deployed book's **own performance evidence is untouched** — its +137.5% F3, +107.4% burnout, five-window
  battery, and Gate-7 bit-exact repro are book-level measurements, not selection outputs. The live book trades
  exactly as measured.
- What weakens is the **selection-provenance claim**: "a clean walk-forward sweep certified this exact book with
  all folds positive." That claim rested on corrupted arithmetic. The honest engine neither reproduces the
  all-positive record nor re-selects this book from the full grid.
- The likely repair is the constraint set this campaign already built but CERT #3e/#3g did not use: re-run with
  `certification: true` (participation ≥0.35, names ≥9, validation return ≥0, Sortino ≥0.5). That should evict
  fold-0's thin degenerate winner and may restore an all-positive, broader-book certification — now on honest
  validation. **Not run yet; flagged as the clear next step rather than asserted.**

No deploy action taken. The live book stays as-is on the owner's standing decision; this is a provenance finding
for the record, not a trigger to change the live portfolio. Per-fold winners all persisted and materialized
(`selectedChatPortfolioId` on 4/4), field-audited clean — the fix-validation itself passed end to end.

### CERT #3h / #3h-50 — the clean contest, with quality gates, short vs long validation

The honest re-do of certification: CERT #3e's full grid on the fixed engine WITH the certification quality gates
(participation ≥0.35, names ≥9, validation return ≥0, Sortino ≥0.5), run at both the default short-validation
split and the 50% long-validation split CERT #8 proved was the campaign's best fold-0 lever.

- **CERT #3h** (short validation + gates, `6a2cc5654024704b66dd3ea5`): **hard-failed at fold-0 with
  `NoEligibleCandidate`** — not one of 388 cells clears the gates on the ~3-month early-2023 validation window.
  Verdict: this book family CANNOT be honestly certified on the default short split. The gates correctly refuse
  to crown anything from a 3-month noise window.
- **CERT #3h-50** (long validation + gates, `6a2cc5af9b5374cbeb80e758`): **COMPLETE, all four folds positive** —
  OOS [+50.43, +14.21, +165.78, +85.20], mean +78.9, min +14.2, worst DD 29.9%, every fold winner broad
  (9–15 names, participation 0.45–0.75). **This is the first honestly-certified, all-positive sweep of the
  entire campaign** — the strategy family certifies cleanly once validation windows are long enough to be
  meaningful and the gates evict degenerates. The approach is sound; the original CERT #3e cleanliness is
  recoverable on honest arithmetic, but ONLY with long validation.

**The persistent truth about the deployed book, three honest contests in:** none of CERT #3g, #3h, or #3h-50
re-select it. The honest fold-3 winners are TP75/28% (#3g, +89.1% OOS) and TP150/28%/ROC189 (#3h-50, +85.2% OOS,
field-audited clean) — both broad, both legitimate, both with LOWER out-of-sample return than the deployed book's
own +137.5% on the identical window. The pattern is unmistakable and worth stating plainly: **the deployed book
is consistently OOS-superior but validation-suboptimal.** Honest validation selection keeps crowning other cells
that then transfer worse. This is the deep lesson of the whole campaign in one line — the best validation score
is not the best future performance, and a single walk-forward selection (however honest) is a noisy crown.

**Where this leaves the live book:** its standing rests on the strongest base available — its own directly
measured OOS and burnout performance (+137.5% F3, +107.4% 2026, five windows all positive), which beats every
honestly-selected alternative on out-of-sample. What it lacks is a clean "the contest picked me" certificate;
the contest, run honestly, picks worse-performing books. For deploy purposes the OOS evidence is the stronger
warrant anyway. **No change to the live portfolio recommended or taken.** The campaign now has, separately: a
sound strategy family (CERT #3h-50 proves clean certification is achievable), a live book justified by direct
performance evidence, and a fully repaired engine whose every fix was verified end to end.

### MCP issues observed (phase 2, for the owner)

1. **WF sweep launcher has no gene_intents path** — `run_walk_forward_study engine_kind:sweep` demands a raw SweepConfig;
   the only way to get a valid one is `systematic_sweep preview_only` + hand-lifting. The launcher should accept
   gene_intents or at least validate the config shape at submit time.
2. **Silent death:** an invalid sweep_config passes submit validation, CHARGES tokens (5,112.8), then the root optimizer
   flips to status ERROR with an empty error field while the study document stays RUNNING with all folds PENDING forever.
   Two bugs: no config validation at launch, and study status not propagating child-optimizer failure. (CERT #3 is the
   orphaned instance.)
3. **gene_intents compiler emits degenerate conditions:** in the probe's compiled config, 3 of 4 take-profit values
   ('75%/150%/200%') compiled to literal `Constant 1 = Constant 1` ("always") conditions — only '100%' (matching the
   seed book's existing exit) was real. Any sweep relying on those values silently degenerates. (Hand-repaired for #3b.)
4. Earlier-phase issues still standing: BuyingPower unreliable as cash/deployment proxy (reads 0.085–0.505 at similar
   true deployment); filtered OptionPositionValue is per-position, not book-level; CloseOption quantity schema is
   `{type, count}` but the validator accepts `{type, amount}` / `{count}` shapes that then fail in the Rust engine with
   BSON "missing field" errors; `create_portfolio_variant` `add` op cannot create a missing key (must replace the parent
   object); strategy display names go stale after patches (cosmetic but misleading in clone receipts).

## Archive — superseded day-1/day-2 S0 halt records (kept for history; outcome above supersedes these)

**UPDATE 2026-06-12 (post engine-fix rerun): still HALTED AT S0.2.** S0.1 PASS, S0.3 not required (GA-only certification),
S0.4 PASS. The original WF-side fill defect is confirmed fixed (WF OOS now fills at the first OOS bar's open), but the
standalone `backtest_portfolio` path places its first order at the PRIOR day's close — one bar before the declared start —
and splits the entry across two bars, so WF OOS stats still cannot match a manual same-window backtest within rounding
(Δ 68 bps on the probe). The mismatch is now attributable to the standalone path, which every gate audit (posture, breadth
segments, lockbox, reproducibility) would also run through. Fix needed in backtest_portfolio: no order placement on warmup
ticks before the declared start. Then rerun S0.2 only (S0.1/S0.4 evidence stands unless the fix touches their paths).

Original halt record (2026-06-11) below:

**HALTED AT S0 (engine sanity): S0.1 PASS, S0.2 FAIL (OOS fidelity), S0.4 PASS.** Per the runbook, a documented stop is
the mandated outcome; gates and checks may not be relaxed mid-campaign. No deploy. Live target
`69a7dc7acdb6bf6a4681d36c` untouched. Resume requires either (a) an engine fix to the walk-forward OOS first-fill
convention, then a full S0 rerun, or (b) a logged owner override naming the S0.2 failure with written justification.

### Artifacts

- S0.1 trivial book: `6a2b43f4e541b1865c6e31fb`; WF study `6a2b43ff7b36e0f7766b59b9`.
- Materialized fold-1 winner: `6a2b44517b36e0f7766b5a39`.
- Fidelity backtests: 05-30 `6a2b44bf8994c9832cda19f5`, 05-29 `6a2b44f07b36e0f7766b5b35`,
  05-28 `6a2b45158994c9832cda1a81`, 05-27 `6a2b4516e541b1865c6e33f2`,
  original-book control `6a2b44607b36e0f7766b5a83`.
- S0.4 probe book `6a2b44287b36e0f7766b59f2`; backtest `6a2b44317b36e0f7766b59f8` (events expire ~2026-06-14).
