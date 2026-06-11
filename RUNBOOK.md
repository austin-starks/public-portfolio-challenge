# Runbook: Walk-Forward Options Campaign → Deploy Live

> **Paste this whole file into a fresh LLM session** with the NexusTrade MCP server connected.
> Self-contained. Follow top to bottom. Do not ask clarifying questions; execute.
> Every runtime step uses MCP tools only, no repo checkout.

---

## Design philosophy

**This runbook prescribes WHAT must be true, never HOW to achieve it.**

- **Fixed:** the universe, the capital, the calendar, the gates, the live-monitoring rules,
  the capital-posture policy, the lockbox, and the deploy procedure.
- **Yours to design:** everything else, signals, structures, deltas, DTEs, cadence, breadth,
  filters, exits, sizing, regime switches. If a design clears the gates, it is valid.

## What this campaign optimizes for, and the one idea that drives it

"Best" = highest risk-adjusted return that is **real out of sample**, obeys the capital
posture, and survives walk-forward. A high backtest number over one window proves nothing.

**The method is walk-forward validation.** The history is tiled into sequential folds. Each
fold optimizes on its own in-sample development window and is then scored on a held-out
out-of-sample (OOS) window the optimizer never saw. Overfitting shows up directly: it is an
OOS aggregate that collapses, or a result carried by a single lucky fold.

Three things follow from this and shape the whole runbook:

1. **Two tools, two jobs.** _Standard optimization / variants / backtests_ are the SEARCH
   layer: you use them to invent and tune candidate designs fast and cheap. _Walk-forward_
   is the CERTIFICATION layer, the go/no-go on whether the design you converged on
   generalizes. Do not run walk-forward on every idea; run it on the design you're ready to
   defend.
2. **Walk-forward certifies a DESIGN, not a parameter set.** Each fold can pick a different
   optimized winner; that is information (winner stability), not the deliverable. Walk-forward
   does not hand you "the params." The book you deploy is a **separately assembled, fixed
   deploy-shape portfolio**; its right to deploy is earned by the walk-forward OOS aggregate,
   the lockbox confirmation, plus the reproducibility/parity checks on that exact assembled book.
3. **OOS is the only headline.** Training and validation are in-sample. Never present a train
   number as evidence the book generalizes. The per-fold OOS table and its aggregate are the
   result.

**Strategy intent:** a deliberately high-risk momentum book on my favorite names. Aggressive
is fine, leverage, convexity, concentration-in-time are on the table. The gates shape the
risk; they are not there to make the book timid.

## The watchlist (fixed universe, 20 names, do not change)

ANET, DUOL, HOOD, LLY, GS, META, TSM, AVGO, XOM, COP, OSCR, AMAT, ADI, DDOG, OKTA, NET, APP, GLD, MU, SNDK

> **Listing-date note.** SNDK began regular-way Nasdaq trading on 2025-02-24, so it has no data
> before the final fold and the lockbox. It is a valid 2025+ name, not a universe error. Its
> early-fold absence is governed by the **not-yet-listed rule in Gate 1** and must not be read as
> a defect. Before auditing breadth, verify every name's first-trade date against each fold's
> dev-window start **programmatically**, do not eyeball the list. SNDK is the only span violation
> in the current 20; the other 19 trade across the whole 2022 → now span.

## Capital posture (POLICY — gateable, not optional)

I do not want to be fully invested most of the time. I want dry powder deployed aggressively
when opportunity is rich, and a small book when it isn't.

Measured from each window's daily equity tape (deployment_t = positionValue_t / value_t;
regime from the SPY trailing-high ratio). Audit with `audit_backtest_posture`, one call per
backtest returns every number this policy gates on.

1. **Median daily deployment ≤ 55%** of NAV, per window.
2. **Deployment above 70% only on days when an objective opportunity regime is active.**
   Define the regime yourself, but it must be: (a) computed from data available at the time,
   (b) written into the strategy (conditions/indicators, not narrative), and (c) stated in
   the deliverable.
3. **Up to 100% is permitted in the strong/extreme version of that regime** (e.g. a major
   drawdown). The ceiling is full deployment; what is forbidden is being maxed out with no
   opportunity-regime signal active. Flag any such day.
4. Report per window: median, p90, % of days >70%, and whether every >70% day fell inside the
   declared regime. Never audit posture from optimizer statistics; only from full-window
   backtests / OOS segments.

## Fixed constants

| Parameter                                | Value                                                                  |
| ---------------------------------------- | ---------------------------------------------------------------------- |
| `initial_value`                          | 25000                                                                  |
| `interval`                               | Day                                                                    |
| Walk-forward span                        | 2022-01-01 → (run date − `lockbox_width_days`)                         |
| `lockbox_width_days`                     | 126 (~6 months), held out from ALL folds and ALL search (see Stage S2) |
| Lockbox window                           | (run date − 126d) → run date; finalist touches exactly once at S2      |
| `walk_forward_mode` (calendar)           | anchored                                                               |
| `mode` (study)                           | **validation** (adaptive/both are not executable yet — see S0)         |
| `fold_count`                             | 4 (minimum 3)                                                          |
| `oos_width_days`                         | 252 (~1y OOS per fold)                                                 |
| `baseline_symbol`                        | SPY                                                                    |
| Live deploy target                       | `69a7dc7acdb6bf6a4681d36c` — no writes until human sign-off            |
| Baseline A (equity B&H, 20 names)        | build at S1                                                            |
| Baseline B (naive LEAP ladder, 20 names) | build at S1                                                            |

Build both baselines on the current engine at S1 and record their IDs + per-fold OOS in
CAMPAIGN_LOG.md before designing anything. Do not reuse stale baseline runs.

Seed affordability note: any single-template ~$1k-per-name book structurally fails Gate 1.
Minimum defined-risk structures on the expensive tail (META/LLY/GS/TSM/ADI/AVGO) cost
$1.3–2.4k per contract. Every template set must end in a rung the most expensive name can fill
at the configured per-name allocation. Do not remove the cheapest rung when sweeping structures.

Baseline B definition: all 20 names, no rank, no filter, 14-day cadence, 8%-of-portfolio per
name under a 95% budget, structure = first affordable rung of [Δ0.50 call → Δ0.55/0.25 vertical
→ Δ0.55/0.40 vertical → Δ0.50/0.42 vertical], all 180–365 DTE, single exit at DTE ≤ 45. Naive
in mechanism, honest in participation. Baselines are benchmarks, not candidates.

**Baseline validity rule (applied per fold):**

- **Baseline A is a return bar only**, never a Sortino bar. Its Sortino reflects equity-rally
  smoothness a leveraged long-premium book cannot match; comparing to it is incoherent.
- **Baseline B is a return bar, and a Sortino bar in folds where it has ≥ 9/20 breadth**
  (`rollups.distinctNamesFilled` from `audit_backtest_breadth` on that OOS segment). Where B
  fails breadth in a fold, the absolute Sortino floor (Gate 2) is the only Sortino constraint
  there.

---

## Stage S0 — Engine sanity (MANDATORY; blocks everything)

Walk-forward is the entire methodology, so prove the engine before trusting a single number.

1. **Chat-portfolio support.** `create_portfolio` a trivial chat book (e.g. SPY > SMA50).
   `run_walk_forward_study` on it: `mode: validation`, `fold_count: 2`, `population_size: 3`,
   `num_generations: 1`. It MUST start (no "Cannot find portfolio" / PortfolioNotFoundError)
   and complete with per-fold OOS stats + an aggregate via `get_walk_forward_study_results`.
   If it errors on a chat portfolio → the engine build that resolves chat portfolios is not
   deployed → **STOP, report, do not proceed.**
2. **OOS fidelity + window disjointness.** Take one completed fold; note its OOS window
   `[start,end]` from the results. Run a manual `backtest_portfolio` of that same book over
   exactly that window. The fold's `oosStatistics` (return, maxDD, Sortino) MUST match the manual
   backtest within rounding. Mismatch = engine defect = **STOP, document, no campaign.**
   **Also assert window disjointness from the returned date ranges:** for that fold, confirm
   train ∩ validation, train ∩ OOS, and validation ∩ OOS are all empty, AND that
   `OOS.start > validation.end` (OOS is strictly later, not merely disjoint). Hard-fail the study
   on any overlap or ordering violation. OOS being disjoint-and-later is the property every gate
   depends on; this converts "disjoint by construction" into "disjoint, asserted every run," and
   guards against a future fold-scheduler regression silently aliasing the optimizer's validation
   set as OOS.
3. **Engine coverage you intend to use.** If you will search with `engine_kind: sweep`, repeat
   step 1 once with `engine_kind: sweep` (tiny, 2 folds) and confirm it completes with per-fold
   OOS. GA and sweep are separate code paths; do not assume sweep works because GA did.
4. **No-data names do not poison the audit.** The fixed universe contains a name with no data in
   early folds (SNDK, first trade 2025-02-24). This is the loader path for a hardcoded watchlist,
   which is separate from point-in-time index membership; do not assume it behaves like the index
   path. Run a tiny `backtest_portfolio` of any book over a 2022 window and inspect how the dead
   name is handled. **What is acceptable:** SNDK appearing in `namesWithZeroResolutionAttempts` /
   `namesWithRejectionsAndZeroFills` is fine on its own, because the Gate-1 not-yet-listed rule
   filters it out by first-trade date. A name with no data showing up in those flag lists is the
   expected, benign case, not a defect. **What is a STOP condition:** the engine returns a real
   error/crash on the dead name, OR it fabricates a non-null value for it (a garbage indicator
   reading or price for a name that did not trade). A fabricated value is the actual risk here:
   filtering by listing date removes a name from the flag lists, but it does NOT remove a phantom
   price that has already leaked into a rank, a `weightIndicator`, or a gate computation. So the
   pass condition is: dead name produces **no data and no value** (absent or null), which
   first-trade-date filtering then cleanly removes. If the engine instead errors, or emits any
   non-null number for the dead name, **STOP, report**, that is the audit lying with fake data and
   it corrupts everything downstream. (This is S0.4's only real job: confirm the audit isn't
   fabricating. How to _read_ a legitimately-flagged not-yet-listed name is Gate 1's job, not this
   check's, and the two must not be confused: list membership is Gate 1, fabricated values are S0.4.)

Only after S0 passes do you design anything. Record S0 outcomes in CAMPAIGN_LOG.md.

> **Mode note:** this campaign runs `mode: validation`. `adaptive`/`both` (the stitched
> re-optimized curve) are not executable yet and the launcher rejects them; do not request them.

## Stage S1 — Baselines as OOS bars

Run a `run_walk_forward_study` (same fold calendar: anchored, `fold_count: 4`,
`oos_width_days: 252`, the walk-forward span 2022-01-01 → run date − `lockbox_width_days`,
`mode: validation`) on Baseline A and Baseline B. From `get_walk_forward_study_results` record,
per baseline: each fold's OOS return + Sortino + maxDD, the OOS aggregate (mean/median/min across
folds), and per-fold breadth (which folds give B ≥ 9/20). These are the bars every candidate's
aggregate must clear. Confirm Baseline B's per-fold breadth audit (`audit_backtest_breadth` on
each OOS segment) shows no `namesWithZeroResolutionAttempts` where an **eligible** name's signal
should have fired.

---

## Stage S2 — Lockbox confirmation (single touch, after design freeze)

The walk-forward span deliberately stops `lockbox_width_days` before the run date. That final
window is the lockbox: it is in no fold, no sweep, no backtest, no search of any kind. The
finalist is invented, tuned, and certified entirely on the walk-forward span. Only the single
assembled deploy-shape book that has **already passed every gate on the WF aggregate** is run over
the lockbox, exactly once, after all design is frozen.

Why it exists: gates frozen at S0 stop you from moving the bar, but you still iterate designs
against a fixed 4-fold calendar, and selecting the design that clears the gates on those exact OOS
years fits the calendar. Three-attempts-per-idea caps tuning within one idea; it does nothing
about selecting across ideas. The lockbox is the one window that selection pressure never touched.

**Pass conditions (frozen at S0, same status as the gates):**

- Lockbox OOS return ≥ the worst single-fold WF OOS return (the design already survived that fold;
  the lockbox must not be worse than its worst certified fold).
- Lockbox maxDD ≤ 55%.
- Posture clean over the lockbox (all four conditions, `audit_backtest_posture`).
- Breadth ≥ 9 **eligible** names over the lockbox (`audit_backtest_breadth`).

A lockbox failure is the calendar-fit signature: the design cleared the fixed fold OOS years but
not a window it never saw. Do not deploy on a lockbox failure except by a logged owner override
that names the lockbox, the same discipline as a gate override.

**Single-touch is absolute.** If you look at the lockbox and then iterate the design, the lockbox
is burned: you have leaked it into the search and it can no longer certify anything. A burned
lockbox requires a fresh held-out tail (move the WF span back further) before any deploy.

---

## Gates — the ONLY constraints on design. The finalist must pass ALL.

Evaluated on the **walk-forward OOS aggregate and per fold**, on the assembled deploy-shape book
(the exact object that would be cloned to live).

1. **Breadth & anti-concentration** (per fold's development backtest AND the OOS segments, via
   `audit_backtest_breadth`):
   - **Not-yet-listed names.** A name whose first-trade date is after a fold's dev-window start is
     not eligible in that fold: it is neither a fill nor a miss. Exclude it from that fold's
     `namesWithZeroResolutionAttempts` and `namesWithRejectionsAndZeroFills`, and from any
     breadth-shortfall reasoning for that fold. The breadth thresholds stay **absolute counts**, so
     nothing about the denominator changes: you still need ≥ 9 real fills per OOS segment and ≥ 13
     cumulative across the study, both reachable from the 19 names live across the whole span. SNDK
     (first trade 2025-02-24) is absent in every fold whose dev window starts before that date and
     becomes eligible only in the late fold(s) and the lockbox; do not read its absence as the
     TSM-class defect. (A not-yet-listed name appearing in these flag lists is expected and benign;
     S0.4 has already confirmed the engine emits no data and no fabricated value for it, so list
     membership here is purely a listing-date artifact to filter out, never a STOP condition. The
     division of labor is fixed: S0.4 catches fabricated values, Gate 1 reads legitimately-flagged
     listing-date absences. Do not halt at Gate 1 on a not-yet-listed name.)
   - `gates.namesWithRejectionsAndZeroFills` is **empty** for eligible names (no cannot-afford
     rejections with zero fills — affordability must never pick the stocks).
   - Cumulative participation ≥ 13/20 across the study; ≥ 9/20 in each OOS segment.
   - Concentration (per fold dev): no single name > 25% of entry notional; top-5 ≤ 60%
     (`rollups.top1SharePct`, and `top_n: 5` for `rollups.topNSharePct`).
   - `gates.namesWithZeroResolutionAttempts` empty for any **eligible** name whose signal should
     have fired (the TSM-class defect → automatic kill; inspect `perUnderlying`). Not-yet-listed
     names per the rule above are not "eligible" here.
2. **OOS beats buy & hold:**
   - **Return:** aggregate OOS return beats Baseline A AND SPY, and OOS return beats both in a
     majority of folds. Worst single fold may trail, but the aggregate and the median fold must
     win with margin (≥ +10pp vs A and vs SPY on the aggregate).
   - **Sortino (absolute floor):** aggregate OOS Sortino ≥ 1.9, AND no fold below 0.9. Fixed
     floor, not a ratio against A. Never tune a mechanism whose only justification is nudging
     Sortino across the floor; if a book needs surgery to clear it, the search hasn't found an
     edge. (Floor calibrated against prior OOS evidence and expected Baseline B before the S0
     freeze; if Baseline B's own OOS Sortino lands near or below 1.9, revisit the floor BEFORE
     freezing, not mid-campaign.)
3. **OOS robustness (the overfitting gate):**
   - OOS return positive in ≥ `ceil(0.75 × fold_count)` folds.
   - Worst single-fold OOS return ≥ −15% (no fold blows up out of sample).
   - `winnerStableAcrossFolds` true, OR the dominant candidate key wins ≥ half the folds.
   - **A result carried by one fold fails this gate**, that is the overfit signature the old
     single-window protocol could only guess at.
4. **Beats Baseline B:** aggregate OOS return > B; OOS Sortino vs B where B qualifies per the
   baseline validity rule (outright with ≥ 5% margin on folds ≥ 12 months; ≥ 90% of B on
   shorter folds; the 90%-floor comparison is exempt from the 5% rule).
5. **Drawdown:** OOS maxDD ≤ 55% in every fold. No exceptions, no "~".
6. **Capital posture:** all four posture conditions, on every fold's development window AND OOS
   segment, via `audit_backtest_posture` (thresholds 55/70/100; regime `comparisonValue`
   trailing-high 252d, 0.92/0.82 — match your declared regime).
7. **Reproducibility:** re-fire the finalist's assembled-book backtest on one OOS window with
   identical params; `compare_backtests {tolerance_bps: 0}` → `identical: true`. Mismatch =
   engine defect = stop, document, no deploy.
8. **Live parity:** after cloning to the live book and BEFORE approving any orders, pull the live
   evaluator's condition audit (`query_portfolio_events` with `include_condition_audit: true`)
   and compare every indicator value in the entry/regime conditions to the same-day values from a
   fresh backtest of the live target. Material mismatch (e.g. a long-window SMA or trailing max
   off by more than the day's move) = engine defect = stop, decline all pending orders, report.

If any gate fails: iterate the **design** (see Process). Gates and the lockbox pass conditions are
frozen at S0 and never moved.

---

## Process (stages are scaffolding, not prescriptions)

- **S0 Engine sanity** → **S1 Baselines** (above), both recorded before any design work.
- **Search (the cheap layer).** Invent candidate designs and tune them with the fast tools:
  `create_portfolio` for a new family anchor, `create_portfolio_variant` for single-change
  variants, `backtest_portfolio` + `compare_backtests` to score, and `systematic_sweep` /
  `optimize_portfolio` to tune parameters **over the walk-forward span only, never the lockbox**.
  This is where you spend most iterations; it is fast and cheap. Keep a kill-log (mechanism →
  stats → verdict → why). Use standard optimize to FIND and tune candidates; do not walk-forward
  every idea.
- **Assemble the finalist.** Build the deploy-shape book with structured `create_portfolio`
  (exact validated strategy objects; no NL re-authoring). Posture must be encoded in the book
  (regime conditions, budgets), not in a comment.
- **Certify with walk-forward (the go/no-go).** `run_walk_forward_study` on the assembled
  finalist (anchored, `fold_count: 4`, `mode: validation`). Read per-fold + aggregate via
  `get_walk_forward_study_results`. Gate 1 per fold via `audit_backtest_breadth`; posture per
  fold via `audit_backtest_posture`; Gates 2–6 from the OOS aggregate + per-fold table. Log the
  per-fold table and breadth/posture audits in CAMPAIGN_LOG.md as each completes.
- **Iterate the design, not the gates.** If a gate fails, change a mechanism and re-search;
  re-certify only when you have a new design worth defending. Three certification attempts on the
  same idea is the ceiling; after that, widen the search instead of tuning toward the bar.
- **Lockbox confirmation (Stage S2).** After certification passes and the design is frozen, run
  the single assembled finalist over the lockbox exactly once. Pass → proceed to sign-off.
  Fail → calendar-fit signal, no deploy without a logged override. Looking at the lockbox and then
  iterating burns it.
- **Sign-off + live deploy.** Present the deliverable. On explicit human "deploy" (or logged
  override): `get_portfolio 69a7dc7acdb6bf6a4681d36c` (audit open positions) →
  `clone_strategies_to_portfolio` (source = finalist chat portfolio) → re-backtest the live
  target to confirm the port (Gate 7 on the target) → run the **Gate-8 live parity check** before
  approving any orders → attach the weekly monitor (below) via `edit_portfolio addStrategies` →
  verify it appears in `get_portfolio` → log everything. (Live portfolios require manual order
  approval, so the parity check happens while orders are safely queued.)
  **The clone REPLACES the live book's entire strategy set and archives any monitor already on
  it. Re-attaching the monitor after every clone is mandatory; verify it in `get_portfolio`
  before declaring the deploy complete. Keep the monitor OUT of the finalist chat portfolio so
  the study/backtests stay clean of LaunchAgent noise.**

---

## Deploy timing + live monitoring (no paper stage)

**When a finalist passes all gates and the lockbox, it deploys LIVE** after sign-off. Risk is
managed in production:

- Gates and lockbox pass conditions are fixed at S0. Rewriting/relaxing/re-deriving any of them
  mid-campaign to convert a failure into a pass invalidates the whole campaign.
- **Human override is allowed but never silent.** A human may "deploy" a book that fails a
  specific gate (or the lockbox) ONLY by naming the failed gate with a written justification
  recorded verbatim in CAMPAIGN_LOG.md and stated in the deliverable ("failed Gate X, deployed by
  owner override because …"). The override is logged; the gate is not moved.
- No strategy edits after deploy without a new campaign.
- **Live kill thresholds** (breach action per item):
  1. **Posture (pause + alert).** Median deployment ≤ 55%; no day > 70% outside the declared
     regime. Breach pauses entries and alerts owner.
  2. **Drawdown brake, two-stage (staged).** On the live equity tape, drawdown =
     1 − PortfolioValue / running-peak(PortfolioValue since deploy). **Pause entries at ≥ 30%
     drawdown; full owner review and possible unwind at ≥ 55%** (the Gate-5 ceiling). High-risk
     book by intent, but a 30% pause stops a 55% loss from arriving silently.
  3. **SPY-excess review trigger (review only, NOT a pause).** After **12 weeks** live, if excess
     return vs SPY < **−15pp**, flag for owner review. Short-horizon SPY tracking error on a
     leveraged convexity book is mostly noise (the book is built to bleed in chop and pull away in
     trends), so this is a prompt to look, not a brake to pull. Where a live Baseline-B proxy is
     available, prefer comparing to B over SPY.
  4. **Order health (pause + alert).** Every rebalance pass with eligible signals produces fills;
     zero cannot-afford rejections; no unexplained rejected/stuck orders.
- **Weekly agent monitor (mandatory part of deploy):** a `LaunchAgent` strategy on the live book,
  condition `Day = Monday OR CrossBelow(SPY, SMA200(SPY)) = 1`, `cooldownMinutes: 1440`,
  `continueExisting: true`, `google/gemini-3-flash-preview` for both planning and execution,
  `maxIterations: 15`, whose brief audits the four thresholds plus per-spread P&L/DTE and proposes
  actions for owner approval. The drawdown brake (#2) and posture (#1) are mechanical pauses; the
  SPY-excess check (#3) is a review prompt only. Findings logged in CAMPAIGN_LOG.md weekly.

---

## Tooling

- **`run_walk_forward_study`** — the certification engine. Inputs: `chat_portfolio_id` (or
  `portfolio_id`), `global_start_date`/`global_end_date`, `fold_count` (2–8), `walk_forward_mode`
  (anchored), `mode` (validation), `engine_kind` (ga/sweep), GA knobs, `oos_width_days`,
  `validation_percent`, `embargo_days`. Charges research tokens once up front. Cost scales with
  folds × evaluations × span × interval × options usage; certify designs, don't sweep with it.
- **`get_walk_forward_study_results`** — per-fold train/validation/OOS stats, the aggregate, and
  child optimizer ids. Zero cost. This is the source for Gates 2–6.
- **`audit_backtest_breadth`** — Gate-1 breadth/concentration in one call on a `backtest_id`
  (`top_n` default 5). `rollups` + `gates` lists; written at finalize, works with
  `generateEvents:false`. `status:"unavailable"` → re-fire on the current engine; never infer
  zeros.
- **`audit_backtest_posture`** — posture/drawdown in one call (thresholds 55/70/100; regime 252d
  0.92/0.82). Median/p90/max, day counts per threshold, per-day violation list, maxDD with
  peak/trough/recovery. Gates 5/6. Never hand-parse tapes for posture.
- **`create_portfolio_variant`** — single-change candidates by JSON-Pointer `patches` off a
  `source_chat_portfolio_id`; immutable result. Always check the `before` echo. Use for every
  variant after the first authored family anchor.
- **`compare_backtests`** — N-way (2–10, same window) vs a baseline, with first-divergence date.
  Reproducibility (`tolerance_bps:0`), variant-batch scoring (the table is the kill-log entry),
  and forensics.
- **`backtest_portfolio`** / **`optimize_portfolio`** / **`systematic_sweep`** — the search layer.
  Standard optimize/sweep to find and tune candidates over the walk-forward span; full-window
  backtests to spot-check. (Optimizer rolling-window stats mask full-window drawdowns; gate only on
  walk-forward OOS and full-window backtests of the assembled book, never on optimizer stats.)

---

## Search constraints (follow these; override only with an A/B pair that disproves them)

- **No stop-losses on hold-to-expiry LEAP/spread books.** Exits = DTE-based closes plus
  regime-gated profit-taking, unless a matched with/without pair proves a stop-loss helps over the
  full span.
- **No narrow ranked rotation (top-K ≤ 5 with a shared cadence).** Rank shuffle rotates membership
  every pass and turnover destroys the book. Breadth comes from a wide limit + an affordability
  ladder, not concurrent slots.
- **Keep `totalBudget` ≥ K × `perNameAllocation`** within each tier/strategy, or a different subset
  fills every pass and turnover explodes.
- **Ship a template ladder so every name has an affordable unit**, including the expensive tail at
  current prices. Cheap structures as the _primary_ template (far-OTM calls, ultra-tight spreads on
  everything) are an automatic kill path; tight rungs are for the expensive tail only.
- **Budgets cap cost basis, not market value.** Market deployment runs above the budget once
  positions appreciate. Size the base budget so posture medians hold on the tape; verify on the
  tape, not the budget number.
- **One mechanism change per candidate.** Decompose multi-change assemblies into single-change
  variants; `compare_backtests` first-divergence dates attribute the effect.
- **`CloseOption` pnl semantics:** `minPnlPercent: 100` = take-profit at +100%;
  `maxPnlPercent: -50` = stop-loss at −50%.
- **`DaysSinceLastRebalanceOptionOrder` / `DaysSinceOrder` read `null` on fresh books, and
  `null >= N` is TRUE**, cadence-gated strategies fire at the first evaluation after deploy. The
  cadence clock is SHARED across all RebalanceOption strategies in the book.
- **Dollar-amount budgets do not de-risk as the book bleeds** the way %-of-NAV sizing does. If you
  use fixed dollars, something else must shed risk.

---

## Indicator vocabulary (materials, not prescriptions; full list in the `create_portfolio` schema, ~90 types)

Inside RebalanceOption pipelines, rank `weightIndicator`s, and template `eligibility` conditions, an
indicator with an **empty `targetAsset` (`{"symbol": ""}`) evaluates per candidate name**, that is
how one rank/filter applies across the universe. Named `targetAsset`s (e.g. SPY) make it a
market-level reading.

- **Price & trend:** `Price`, `SimpleMovingAverage`, `ExponentialMovingAverage`,
  `MaximumPrice`/`MinimumPrice`, `MaxDrawdown`/`MaxDrawup`, `PriceRateOfChange`,
  `PriceStandardDeviation`, `AverageTrueRange`, `RelativeStrengthIndex`, `BollingerBand`, `VWAP`,
  `Volume`.
- **Composition:** `Plus`/`Minus`/`Multiply`/`Divide`/`Max`/`Min`/`AbsoluteValue`/`Log`/
  `Exponentiation`, build custom ratios and z-score-like ranks (e.g. ROC / (ATR/price)).
- **Meta-indicators (windows over indicators):** `IndicatorWindowAgo`,
  `IndicatorSimpleMovingAverage`/`IndicatorExponentialMovingAverage`, `IndicatorStandardDeviation`/
  `IndicatorMeanAbsoluteDeviation`, `IndicatorRateOfChange`, `TrailingSum`.
- **Events & persistence:** `CrossAbove`/`CrossBelow`, `ConsecutiveTrue`/`CountTrue`.
- **Market & macro:** `Index` (`VIX`/`SPX`), `Economic` (`UNRATE`); the regime ratio is
  `Price(SPY)` vs `Multiply(k, MaximumPrice(SPY, 252d))`.
- **Fundamentals:** `Fundamental` (`peRatioTTM`, `marketCap`, `dividendYield`, `freeCashFlow`),
  `CompoundAnnualGrowthRate(metric, years)`.
- **Book & position state:** `OptionGrossExposurePercent` (sum of abs leg marks over NAV, often
  several hundred % on spreads; not a deployment proxy; read its actual values before thresholding),
  `OptionPositionCount`, `OptionUnrealizedPnL`, `OptionDaysToExpiration`, `PositionPercentChange`,
  `PositionMaxDrawdown`, `UnderlyingMaxDrawdown`, `PortfolioValue`, `BuyingPower`, the `DaysSince*`
  family.
- **Calendar:** `Day`/`Month`/`Date`.

Calibrate every threshold against observed values (condition audits, equity tapes), never against
intuition.

### Composed-indicator recipes (copy, modify, or ignore — per-name unless noted)

- **Momentum acceleration:** `ROC(21) − IndicatorWindowAgo(ROC(21), 21d)`.
- **Momentum smoothness (Sharpe-like rank):** `ROC(63) / PriceStandardDeviation(63)`.
- **Vol compression (squeeze):** `ATR(14) / IndicatorSMA(ATR(14), 100d)`, below ~0.8 the name is
  coiled.
- **Pullback depth in ATR units:** `(MaximumPrice(252) − Price) / ATR(14)`.
- **Parabolic-extension guard:** `(Price − SMA(20)) / ATR(14)`, skip the blowoff / take profit.
- **Trend persistence:** `CountTrue(Price > SMA(50), 63d)` (graded, less whipsaw than a binary
  gate; works for the SPY market brake too).
- **Relative strength vs market:** `ROC(63, name) − ROC(63, SPY)`.
- **Upside/downside asymmetry:** `MaxDrawup(63) / MaxDrawdown(63)`.
- **Volume thrust:** `Volume / IndicatorSMA(Volume, 50d)`.
- **Adaptive vol regime (market):** `Index(VIX) / IndicatorSMA(Index(VIX), 20d)`.

### Searches worth running (suggestions)

- **Per-template `eligibility` gates**, structure-by-name-state (long calls only above 200d SMA,
  spreads otherwise).
- **Structure-by-regime**, different template sets per regime tier (separate RebalanceOption
  strategies per tier).
- **Underlying-state exits**, one CloseOption per name keyed on its own state (e.g.
  `Price(ANET) < SMA200(ANET)`); trend-based exits without a mark stop-loss. Search this before any
  mark-based stop.
- **Exposure-keyed de-risk**, CloseOption on `OptionGrossExposurePercent`; read actual values from
  an events run with `include_condition_audit:true` before thresholding.
- **Entry-condition gates**, regime ratios, drawdown, vol filters; hand-author, or sweep with
  explicit `gene_intents`.

---

## Deliverable (present at sign-off)

Per-fold table + aggregate row + lockbox row:

| Fold          | Dev window | OOS window                   | OOS return      | OOS maxDD | OOS Sortino     | Names filled /20 | Median deploy | %days >70% (in regime?) | vs A | vs B | vs SPY |
| ------------- | ---------- | ---------------------------- | --------------- | --------- | --------------- | ---------------- | ------------- | ----------------------- | ---- | ---- | ------ |
| 1 … N         |            |                              |                 |           |                 |                  |               |                         |      |      |        |
| **Aggregate** |            |                              | mean/median/min | worst     | mean / min-fold |                  |               |                         |      |      |        |
| **Lockbox**   | (held out) | (run date − 126d) → run date |                 |           |                 | (eligible)       |               |                         |      |      |        |

Plus: the walk-forward study id; full strategy rules in plain English; the declared opportunity
regime; the kill-log; finalist chatPortfolioId; OOS-robustness summary (folds positive, worst fold,
winner stability); per-fold breadth audit (`audit_backtest_breadth`: names filled /20, both gate
lists, top-1 and top-5 shares); the **lockbox confirmation result** (return vs worst fold, maxDD,
posture, breadth) PASS/FAIL; reproducibility PASS/FAIL; the Gate-8 live parity result; any logged
owner override; and (post-deploy) the weekly monitor reports appended to CAMPAIGN_LOG.md.

**The headline characterization is the OOS aggregate. Never lead with a single-window or in-sample
number.**

## Working rules

- Keep CAMPAIGN_LOG.md current at every stage; it is the article's spine, and S0/S1 outcomes are
  recorded before any design work.
- Search with standard optimize/variants/backtests; certify with walk-forward. Don't conflate them.
- The lockbox is held out from ALL search and ALL folds and is touched exactly once, by the
  assembled finalist, at S2. Any earlier touch by any tool burns it.
- Compare every certified candidate against both baselines on the same fold calendar.
- An honest "no deploy, OOS failed" is a successful campaign outcome. Do not torture the search
  until something squeaks past the gates; **three certification attempts on one idea is the
  ceiling**, then widen the search. (This methodological ceiling stands regardless of token cost;
  it is the only brake on grinding the same idea against the fixed calendar.)
- Gates and the lockbox pass conditions are fixed at S0. Override only with a logged, named-gate
  owner justification.
- Deploy only after explicit human "deploy" (or a logged owner override on a named gate/lockbox).
