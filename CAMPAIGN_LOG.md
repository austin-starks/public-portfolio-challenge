# CAMPAIGN_LOG — Walk-Forward Options Campaign

Run date: 2026-06-11
Operator: Claude (Fable 5) via NexusTrade MCP, executing RUNBOOK.md top to bottom.

## Fixed campaign parameters (frozen)

- Universe (20): ANET, DUOL, HOOD, LLY, GS, META, TSM, AVGO, XOM, COP, OSCR, AMAT, ADI, DDOG, OKTA, NET, APP, GLD, MU, SNDK
  - SNDK first regular-way trade 2025-02-24 (not-yet-listed rule applies in early folds).
- initial_value: 25000; interval: Day
- Walk-forward span: 2022-01-01 → 2026-02-05 (run date 2026-06-11 − 126d lockbox)
- Lockbox: 2026-02-05 → 2026-06-11, single touch at S2 only
- fold_count: 4, anchored, mode: validation, oos_width_days: 252
- baseline_symbol: SPY; live deploy target: 69a7dc7acdb6bf6a4681d36c
- Gates 1–8 + lockbox pass conditions: as written in RUNBOOK.md, frozen at S0. No changes permitted.

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

| Metric | Fold oosStatistics | Manual backtest, exact OOS window (`6a2b44bf8994c9832cda19f5`) |
|---|---|---|
| percentChange | **16.9914%** | **16.1990%** (Δ = 79 bps) |
| sortinoRatio | **2.3112** | **2.1796** |
| sharpeRatio | 1.7157 | 1.6198 |
| maxDrawdown | 4.97274% | 4.97271% |
| totalFees | 24.95542359506551 | 24.95542359506551 (exact) |
| dollarsSold | 0 | 0 |
| totalDividends | 152.2140 | 151.1824 |

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

| Fold | Window | A return | A Sortino | A maxDD | B return | B Sortino | B maxDD | B names/20 | SPY return |
|---|---|---|---|---|---|---|---|---|---|
| F0 | 2023-05-05→2024-01-11 | +44.27% | 3.599 | 10.22% | +81.66% | 2.635 | 33.86% | 16 ✓ | +16.8% |
| F1 | 2024-01-12→2024-09-19 | +41.46% | 2.625 | 19.67% | +54.66% | 1.878 | 39.51% | 14 ✓ | +20.5% |
| F2 | 2024-09-20→2025-05-29 | +31.89% | 1.667 | 34.47% | +48.45% | 1.788 | 37.68% | 10 ✓ | +4.5% |
| F3 | 2025-05-30→2026-02-05 | +102.81% | 4.438 | 13.76% | +22.33% | 1.073 | 29.99% | 12 ✓ | +15.6% |
| **Mean** | | **+55.11%** | 3.08 | worst 34.47% | **+51.78%** | 1.84 | worst 39.51% | all ≥9 | **+14.35%** |

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

| Variant | Mechanism change | F0 | F1 | F2 | F3 | 2022 | Verdict |
|---|---|---|---|---|---|---|---|
| v1 `6a2b5608…2723` | anchor: top-10 rank, 45/50 budgets, TP150, BP-valve | (43.6) | — | — | — | +0.9, DD 57 | posture fail (2022 median 67) |
| v2 `6a2b568c…e7fd` | tiered 40/20/35, cadence 21 | 52.0 | — | — | — | +6.0 | >70 days out of regime (valve has no winners to close in drawdowns) |
| v3 `6a2b5744…29b4` | 30/15/45 + hard BP flatten | 33.0 | 5.0 | 37.5 | 18.5 | -9.9 | KILL: flatten churn destroys returns |
| v4a `6a2b57a8…ea2e` | **wide limit 20 (no rank rotation)** | 73.4 | 14.0 | 192.8 | 52.0 | +19.4 | KEY WIN: rotation churn was the return killer; posture: 17/4/3/0 days >70 OOR |
| v4b | TP 300 | identical to v4a | | | | | TP never reached — valve harvests first |
| v5 `6a2b57ff…2aff` | valve 0.31/0.26 + BP hard flatten | 4.3 | -19.7 | 102.9 | -0.7 | +19.4 | KILL: BuyingPower under/over-reads (0.085 at 80% dep; 0.505 at 62%) → flatten roulette |
| v6 `6a2b58d9…ec26` | graded BP valve + regime-scoped core, 40/12/38 | 105.3 | 64.1 | 157.5 | -9.2 | +30.5 | F1 win was BP-valve LUCK (accidental market timing); F3 killed by same noise |
| v7 `6a2b59b2…2de7` | all-calls ladder + OGEP valve 72/82/95 | 119.4 | 77.9 | 104.4 | 8.0 | -13.2, DD 63 | OTM-call rungs too fragile; multi-change, attribution muddy |
| v9 `6a2b5a04…ed8d` | v6 with OGEP valve 95/110/130 | 141.0 | -0.4 | 138.8 | 71.7 | -11.9 | valve never binds in F1 → rides into Aug-24 crash |
| v10 `6a2b5a9d…03a2` | + 20 per-name SMA100 trend-break exits | 52.6 | -29.8 | 24.0 | 65.0 | +0.8 | KILL: whipsaw destruction (runbook A/B done: trend exits rejected) |
| v11 `6a2b5aef…ef77` | v9 with **TP 100** | 88.8 | 114.5 | 142.0 | 41.2 | — | TP100 banks H1-24 gains pre-crash → F1 fixed; mean 96.6; posture fails in melt-ups (F0 med 67.7, ~100 d >70 OOR) |
| v12 `6a2b5b76…f042` | governor 78/88/100 close-all | -13.3 | -18.9 | -65.7 | -29.7 | +10.1 | KILL: perpetual sell-low machine |
| v13c `6a2b5c1f…3143` | quantity-limited trims (1-2 contracts/day) | -17.9 | — | — | — | — | KILL: quantity works ({type:"contracts",count:N}) but thresholds fire at dep 48-66 |
| **v14 `6a2b5d1e24b4b85b24a2f295`** | **v11 with budgets 28/10/30** | **59.9** | **43.5** | **170.2** | **73.3** | **+49.8** | **FINALIST** — see below |
| v15 `6a2b5db6…32d3` | v14 + 60%-band OOR harvest, 8/22 sleeves | 44.8 | -16.2 | 197.8 | 30.0 | +43.5 | KILL: +60 harvest re-amputates F1 |
| MLT-DV `6a2b5cb1…f20c` | all-verticals (defined-value cap) 45/15/22 | 56.7 | 3.0 | 115.8 | 105.1 | — | structurally posture-capped, but F1 Sortino 0.56 < 0.9 floor |

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
- Posture: OOS medians 45.8/29.0/28.9/27.0 (all ≤55 ✓); F2 zero >70-out-of-regime days ✓; **F0 12 days, F1 2 days, F3 14 days
  >70% with regime inactive (parabolic melt-up blocks Sep-Oct'23, May'24, Aug-Sep'25) — posture condition 2 NOT fully clean**;
  2022 stress: ZERO >70-OOR days ✓ but median 62.4 > 55 (in-regime year; rule 1 is unconditional) — flagged for dev windows.
- Backtests: F0 `6a2b5d29955c28672f64075c` F1 `6a2b5d2b24b4b85b24a2f2b7` F2 `6a2b5d2d955c28672f640778`
  F3 `6a2b5d30d39b9224ac2d3228` 2022 `6a2b5d3224b4b85b24a2f2d0`.

### Certification attempt 1/3 — **FAIL** (study `6a2b5e02d39b9224ac2d3371`, GA pop 6 × gen 2, fitness sharpe, 327.68 tokens)

| Fold | OOS return | OOS Sortino | OOS maxDD | Names traded |
|---|---|---|---|---|
| 0 | +4.49% | 0.349 | 17.4% | 9 |
| 1 | +50.96% | 1.634 | 23.2% | 13 |
| 2 | +18.38% | 1.374 | 51.9% | 14 |
| 3 | +1057.72% | 8.268 | 32.2% | 11 |
| Agg | mean 282.9 / **median 34.7** / min 4.5 | mean 2.91 / min 0.35 | worst 51.9 | |

- Gate 2 ✗: median fold (34.7) loses to A's median (42.9); only 2/4 folds beat A&SPY; fold-0 Sortino 0.349 < 0.9 floor.
- Gate 3 ✗: aggregate carried by fold 3 (+1057% = ~93% of the mean) — the one-lucky-fold signature; winnerStableAcrossFolds false.
- Gate 4 ✗: fold-0/fold-2 Sortino below 90%-of-B floors. Gates 5 ✓ (maxDD ≤ 51.9), 3-positivity ✓ (4/4 positive, worst +4.5).
- Diagnosis: NOT a market-behavior failure of the design (fixed-params book scored 59.9/43.5/170.2/73.3 on the same OOS
  windows) but GA selection pathology — pop 6 × gen 2 selecting on validation Sharpe rewards degenerate low-activity mutants
  (fold-0 winner traded 2 names in validation, participation 0.10, then did nothing OOS).

### Certification attempt 2/3 — **FAIL** (study `6a2b5edbd39b9224ac2d3485`, fitness [sortino, percentChange], pop 10 × gen 3, 807.2 tokens)

| Fold | OOS return | OOS Sortino | OOS maxDD | Names traded |
|---|---|---|---|---|
| 0 | **-41.01%** | -1.411 | 49.4% | 19 |
| 1 | +167.52% | 3.315 | 39.0% | 19 |
| 2 | +157.63% | 3.419 | 47.1% | 19 |
| 3 | +937.47% | 8.028 | 33.8% | 9 |
| Agg | mean 305.4 / median 162.6 / min -41.0 | mean 3.34 / min -1.41 | worst 49.4 | winnerStable: false |

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

