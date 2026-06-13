# Runbook: Walk-Forward Options Campaign → Deploy Live

> **Paste this whole file into a fresh LLM session** with the NexusTrade MCP server connected.
> Self-contained. Follow top to bottom. Do not ask clarifying questions; execute.
> Every runtime step uses MCP tools only, no repo checkout.

---

## Design philosophy

**This runbook prescribes WHAT must be true, never HOW to achieve it.**

- **Fixed:** the universe, the capital, the calendar, the gates, the selection method, the
  live-monitoring rules, the capital-posture policy, the lockbox, and the deploy procedure.
- **Yours to design:** everything else — signals, structures, deltas, DTEs, cadence, breadth,
  filters, exits, sizing, regime switches. If a design clears the gates, it is valid.

### The hard-won lesson that shapes everything (read twice)

A previous run of this campaign deployed a strong book, then discovered the thing that made it
"win" was not reproducible. The lessons below are not theory; they are paid for. They override
intuition wherever they conflict with it.

1. **Validation score is a noisy proxy for out-of-sample. Maximizing it does not find the
   OOS-best book.** Picking the single highest-validation candidate per fold is a high-variance
   bet that, in practice, selects books that transfer *worse* than ones it passed over. **You do
   not select the argmax. You select the candidate that is robust across all folds** (see
   "Selection method" — this is mandatory, not advisory).
2. **The value lives in the DESIGN, not the optimizer.** Empirically, optimization never beat a
   well-designed strategy family on OOS — it either degraded it or circled back to it. Treat the
   optimizer as a modest, robust knob-setter that confirms a design's neighborhood, never as a
   discoverer of magic. Spend your effort on the family; ask the optimizer for little.
3. **Only the deployable object is real. Verify it at the FIELD level, never by name.** Strategy
   and condition *display names* can be stale or wrong; the `comparison`/`value`/`window` fields
   are what trade. Every certification, reproducibility, and parity check reads
   `conditionFieldAudit` (raw fields), never `strategy.name` or `condition.name`. A book whose
   name says "≥ 14" while its field says "≠ 141" is a different strategy than it claims.
4. **Reproducibility is a property of the PROCESS, not a backtest number.** A backtest-selected
   strategy is one draw from one history. The asset worth building is a *process that reliably
   produces robust-enough books, verified forward.* Make the process deterministic, field-verified,
   and bug-checked; accept that live performance is the only true out-of-sample.

### What this campaign optimizes for

"Best" = highest risk-adjusted return that is **real out of sample**, obeys the capital posture,
and is **robust across folds** (not carried by one). A high backtest number over one window proves
nothing; a high validation number on one fold proves nothing.

**The method is walk-forward validation.** History is tiled into sequential folds. Each fold
optimizes on its own in-sample development window and is scored on a held-out OOS window the
optimizer never saw. Overfitting shows up directly: an OOS aggregate that collapses, a result
carried by a single lucky fold, or a winner that changes every fold.

Three operating principles follow:

1. **Two tools, two jobs.** _Standard optimization / variants / backtests_ are the SEARCH layer:
   invent and tune candidate designs fast and cheap. _Walk-forward_ is the CERTIFICATION layer:
   the go/no-go on whether the design generalizes. Run walk-forward on the design you're ready to
   defend, not on every idea.
2. **Walk-forward certifies a DESIGN, then names a robust parameterization.** Each fold can pick a
   different optimized winner — that is the noise signal (see principle 1 of the hard-won lesson).
   The deploy book is a **separately assembled, fixed deploy-shape portfolio** chosen by the
   cross-fold selection method below; its right to deploy is earned by the WF OOS aggregate, the
   lockbox confirmation, and field-level reproducibility/parity on that exact assembled book.
3. **OOS is the only headline.** Training and validation are in-sample. Never present a train or
   validation number as evidence the book generalizes. The per-fold OOS table and its aggregate
   are the result.

**Strategy intent:** a deliberately high-risk momentum book on my favorite names. Aggressive is
fine — leverage, convexity, concentration-in-time are on the table. The gates shape the risk; they
are not there to make the book timid.

## The watchlist (fixed universe, 20 names, do not change)

ANET, DUOL, HOOD, LLY, GS, META, TSM, AVGO, XOM, COP, OSCR, AMAT, ADI, DDOG, OKTA, NET, APP, GLD, MU, SNDK

> **Listing-date note.** SNDK began regular-way Nasdaq trading on 2025-02-24, so it has no data
> before the final fold and the lockbox. It is a valid 2025+ name, not a universe error. Its
> early-fold absence is governed by the **not-yet-listed rule in Gate 1** and must not be read as a
> defect. Before auditing breadth, verify every name's first-trade date against each fold's
> dev-window start **programmatically**; do not eyeball the list. SNDK is the only span violation in
> the current 20; the other 19 trade across the whole 2022 → now span.

## Capital posture (POLICY — gateable, not optional)

I do not want to be fully invested most of the time. I want dry powder deployed aggressively when
opportunity is rich, and a small book when it isn't.

Measured from each window's daily equity tape (deployment_t = positionValue_t / value_t; regime
from the SPY trailing-high ratio). Audit with `audit_backtest_posture`; one call per backtest
returns every number this policy gates on.

1. **Median daily deployment ≤ 55%** of NAV, per window.
2. **Deployment above 70% only on days when an objective opportunity regime is active.** Define the
   regime yourself, but it must be: (a) computed from data available at the time, (b) written into
   the strategy (conditions/indicators, not narrative), and (c) stated in the deliverable.
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
| `mode` (study)                           | validation                                                             |
| `engine_kind` (certification)            | **sweep** (bounded, typed search — see "Engine choice")                |
| `fold_count`                             | 4 (minimum 3)                                                          |
| `oos_width_days`                         | 252 (~1y OOS per fold)                                                 |
| `validation_percent`                     | **50** (long validation windows — mandatory, see "Why 50")            |
| `certification`                          | **true** (activity + quality floors on fold-winner selection)         |
| `baseline_symbol`                        | SPY                                                                    |
| Live deploy target                       | `69a7dc7acdb6bf6a4681d36c` — no writes until human sign-off            |
| Baseline A (equity B&H, 20 names)        | build at S1                                                            |
| Baseline B (naive LEAP ladder, 20 names) | build at S1                                                            |

**Why `validation_percent: 50` is mandatory.** The default short split gives the early bear-only
fold a ~3-month validation window, which is statistically meaningless for a convexity book: it is
too short to contain a regime change, so selection on it is pure noise and the quality floors can
become impossible to satisfy (no eligible candidate). Long validation windows (8–20 months) are the
single biggest lever for honest fold-0 selection. Use 50 unless you have a specific, logged reason.

**Why `certification: true`.** It applies activity and quality floors (participation ≥ 0.35,
distinct names ≥ 9, validation return ≥ 0, validation Sortino ≥ 0.5) to fold-winner selection,
which evicts the degenerate thin-book winners that otherwise dominate short validation windows. If
a fold returns `NoEligibleCandidate` under these floors, that is honest information — the design
cannot be cleanly certified on that window — not a bug to work around.

Build both baselines on the current engine at S1 and record their IDs + per-fold OOS in
CAMPAIGN_LOG.md before designing anything. Do not reuse stale baseline runs.

Seed affordability note: any single-template ~$1k-per-name book structurally fails Gate 1. Minimum
defined-risk structures on the expensive tail (META/LLY/GS/TSM/ADI/AVGO) cost $1.3–2.4k per
contract. Every template set must end in a rung the most expensive name can fill at the configured
per-name allocation. Do not remove the cheapest rung when sweeping structures.

Baseline B definition: all 20 names, no rank, no filter, 14-day cadence, 8%-of-portfolio per name
under a 95% budget, structure = first affordable rung of [Δ0.50 call → Δ0.55/0.25 vertical →
Δ0.55/0.40 vertical → Δ0.50/0.42 vertical], all 180–365 DTE, single exit at DTE ≤ 45. Naive in
mechanism, honest in participation. Baselines are benchmarks, not candidates.

**Baseline validity rule (applied per fold):**

- **Baseline A is a return bar only**, never a Sortino bar. Its Sortino reflects equity-rally
  smoothness a leveraged long-premium book cannot match; comparing to it is incoherent.
- **Baseline B is a return bar, and a Sortino bar in folds where it has ≥ 9/20 breadth**
  (`rollups.distinctNamesFilled` from `audit_backtest_breadth` on that OOS segment). Where B fails
  breadth in a fold, the absolute Sortino floor (Gate 2) is the only Sortino constraint there.

---

## Engine choice: sweep, not GA (fixed)

Certification uses `engine_kind: sweep` — a bounded, typed grid over a small number of knobs.
Free-form GA is not used for deploy-grade certification. Reason, paid for in a prior run: GA mutates
the genome structure itself (comparators, constants, window lengths), which produces degenerate
thin-book winners, scrambled conditions, and selection that does not transfer. A bounded sweep can
only move the knobs you name, so every candidate is a sane member of your designed family. If you
believe a continuous parameter needs GA, lock the genome shape and bound the ranges; never run
open-ended GA into a deploy.

**Authoring a sweep (the only supported path):**

1. `get_sweep_surface` on the seed portfolio first — it lists the valid `scope`/`field` pairs,
   default gene templates, and authoring controls. Do not hand-guess field names.
2. Build genes with **`gene_intents`** (plain English, one per axis). The server compiles and
   validates them into correct `scope`/`field` targets. Prefer this over hand-authored
   `sweep_config` JSON, which is where field-name typos cause `invalid target field`.
   - Take-profit is `TakeProfitPct` on **Action** scope. Never sweep take-profit as an
     `ExitCondition` / `OptionPositionPercentChange` — that path does not move the take-profit
     trigger.
3. `run_walk_forward_study` with `preview_only: true` first — it compiles the genes and estimates
   cost without billing. Confirm the compiled `scope`/`field` and value labels are what you meant,
   then launch for real.

---

## Selection method (fixed — this is the core of the methodology)

When the study completes, you do **not** deploy the per-fold validation argmax. You select the
parameterization that is **robust across the whole calendar**:

1. From `get_walk_forward_study_results`, read every fold's `selectedChatPortfolioId` and the full
   per-fold OOS table. Confirm winners persisted and materialized (a real `selectedChatPortfolioId`
   per fold, not a `materializationError`).
2. **Prefer a configuration that is good across folds over one that spikes on a single fold.** If
   one resolved parameterization is a fold winner (or near-winner) in a majority of folds — the
   `dominantCandidateKey` winning ≥ half the folds — that is your candidate. A different winner
   every fold (`winnerStableAcrossFolds: false` with no dominant key) is the explicit signal that
   the surface is noise: deepen the search or widen validation, do not just grab fold-3's winner.
3. **Assemble the deploy book from the robust parameterization**, not by cloning a single fold's
   materialized winner. Build it deploy-shape with structured `create_portfolio` (validated
   strategy objects), posture encoded in conditions/budgets.
4. **Measure the assembled book directly.** Backtest it on each fold's OOS window and the aggregate.
   The deploy decision rests on *the assembled object's measured OOS*, never on the study's
   certified numbers for a fold winner (those describe a different object and can diverge).
5. If you want to reduce single-pick variance further, deploy the **centroid of the top cluster**
   (the parameter values most common among the top-ranked cells), not the single argmax. The center
   of the good region reproduces; the lucky point does not.

---

## Stage S0 — Engine sanity (MANDATORY; blocks everything)

Walk-forward is the entire methodology, so prove the engine before trusting a single number. These
checks are written to catch the specific failure classes that have bitten this campaign before.
Record every S0 outcome in CAMPAIGN_LOG.md.

1. **Chat-portfolio support.** `create_portfolio` a trivial chat book (e.g. SPY > SMA50).
   `run_walk_forward_study` on it: `mode: validation`, `fold_count: 2`, `engine_kind: sweep`, one
   gene × 3 values. It MUST start (no PortfolioNotFoundError) and complete with per-fold OOS stats +
   an aggregate via `get_walk_forward_study_results`. Error on a chat portfolio → **STOP, report.**
2. **OOS fidelity + window disjointness.** Take one completed fold; note its OOS window from the
   results. `backtest_portfolio` of that same book over exactly that window. The fold's
   `oosStatistics` (return, maxDD, Sortino) MUST match within rounding. Also assert disjointness from
   the returned date ranges: train ∩ validation, train ∩ OOS, validation ∩ OOS all empty, AND
   `OOS.start > validation.end`. Any mismatch or overlap = **STOP, document, no campaign.**
3. **VALIDATION fidelity (not just OOS).** Take the same fold; note its *validation* window. Backtest
   the materialized fold winner over exactly that validation window. The fold's
   `validationStatistics` return/Sortino MUST match the standalone backtest within rounding. This is
   the check that catches a scorer reading the wrong/truncated window — a tell is *identical*
   validation stats across genomes that should differ, or a validation number that cannot be
   reproduced by any standalone window. Mismatch = **STOP, document, no campaign.**
4. **Field-level integrity (names lie).** Materialize any fold winner; pull `get_portfolio` /
   `conditionFieldAudit` and confirm the raw `comparison`/`value`/`window` fields match the seed
   design. Confirm the entry sleeves are NOT all simultaneously satisfiable (e.g. core and dip
   regimes are mutually exclusive on a given day). If condition fields are scrambled relative to the
   names, or mutually-exclusive sleeves all evaluate true → **STOP, report.**
5. **Materialization parity.** Backtest the materialized fold winner over that fold's OOS window;
   it MUST reproduce the fold's certified `oosStatistics` within rounding. If the certified number
   and the deployable object diverge → the selected individual ≠ the materialized object → **STOP,
   report** (and in any case, always make deploy decisions on the directly-measured object).
6. **Persistence.** Confirm `get_walk_forward_study_results` returns a real `selectedChatPortfolioId`
   for every completed fold (no `materializationError`). If fold winners do not persist → **STOP,
   report**; selection cannot be trusted without them.
7. **No-data names do not poison the audit.** The fixed universe contains a name with no data in
   early folds (SNDK, first trade 2025-02-24). Run a tiny `backtest_portfolio` over a 2022 window
   and inspect handling. **Acceptable:** SNDK in `namesWithZeroResolutionAttempts` /
   `namesWithRejectionsAndZeroFills` (the Gate-1 not-yet-listed rule filters it by first-trade date).
   **STOP condition:** the engine errors/crashes on the dead name, OR fabricates any non-null value
   (a price/indicator reading for a name that did not trade). A fabricated value leaks into ranks and
   gates even after listing-date filtering removes the name from flag lists. Pass = dead name
   produces **no data and no value** (absent or null). (S0.7 catches fabricated values; how to *read*
   a legitimately-flagged not-yet-listed name is Gate 1's job. Do not conflate.)

Only after S0 passes do you design anything.

---

## Stage S1 — Baselines as OOS bars

Run a `run_walk_forward_study` (same fold calendar: anchored, `fold_count: 4`, `oos_width_days: 252`,
`validation_percent: 50`, `mode: validation`, the walk-forward span) on Baseline A and Baseline B.
From `get_walk_forward_study_results` record, per baseline: each fold's OOS return + Sortino + maxDD,
the OOS aggregate (mean/median/min), and per-fold breadth (which folds give B ≥ 9/20). These are the
bars every candidate's aggregate must clear. Confirm Baseline B's per-fold breadth audit
(`audit_backtest_breadth` on each OOS segment) shows no `namesWithZeroResolutionAttempts` where an
**eligible** name's signal should have fired.

---

## Stage S2 — Lockbox confirmation (single touch, after design freeze)

The walk-forward span deliberately stops `lockbox_width_days` before the run date. That final window
is the lockbox: in no fold, no sweep, no backtest, no search of any kind. The finalist is invented,
tuned, and certified entirely on the walk-forward span. Only the single assembled deploy-shape book
that has **already passed every gate on the WF aggregate** is run over the lockbox, exactly once,
after all design is frozen.

Why it exists: gates frozen at S0 stop you moving the bar, but selecting the design that clears the
gates on a fixed 4-fold calendar still fits the calendar. The lockbox is the one window selection
pressure never touched.

**Pass conditions (frozen at S0, same status as the gates):**

- Lockbox OOS return ≥ the worst single-fold WF OOS return.
- Lockbox maxDD ≤ 55%.
- Posture clean over the lockbox (all four conditions, `audit_backtest_posture`).
- Breadth ≥ 9 **eligible** names over the lockbox (`audit_backtest_breadth`).

A lockbox failure is the calendar-fit signature. Do not deploy on a lockbox failure except by a
logged owner override that names the lockbox.

**Single-touch is absolute.** If you look at the lockbox and then iterate the design, the lockbox is
burned — you have leaked it into the search. A burned lockbox requires a fresh held-out tail (move
the WF span back further) before any deploy.

---

## Gates — the ONLY constraints on design. The finalist must pass ALL.

Evaluated on the **walk-forward OOS aggregate and per fold**, on the assembled deploy-shape book (the
exact object that would be cloned to live), measured directly (never on certified fold-winner numbers
for a different object).

1. **Breadth & anti-concentration** (per fold dev backtest AND OOS segments, via
   `audit_backtest_breadth`):
   - **Not-yet-listed names.** A name whose first-trade date is after a fold's dev-window start is
     not eligible in that fold: neither a fill nor a miss. Exclude it from that fold's
     `namesWithZeroResolutionAttempts` / `namesWithRejectionsAndZeroFills` and from breadth-shortfall
     reasoning. Thresholds stay absolute counts: ≥ 9 real fills per OOS segment, ≥ 13 cumulative
     across the study, both reachable from the 19 names live across the whole span. (S0.7 already
     confirmed the engine emits no fabricated value for a dead name; Gate 1 just filters its
     listing-date absence. Do not halt at Gate 1 on a not-yet-listed name.)
   - `gates.namesWithRejectionsAndZeroFills` empty for eligible names (affordability must never pick
     the stocks).
   - Cumulative participation ≥ 13/20 across the study; ≥ 9/20 in each OOS segment.
   - Concentration (per fold dev): no single name > 25% of entry notional; top-5 ≤ 60%.
   - `gates.namesWithZeroResolutionAttempts` empty for any **eligible** name whose signal should have
     fired (the data-defect kill → inspect `perUnderlying`).
2. **OOS beats buy & hold:**
   - **Return:** aggregate OOS return beats Baseline A AND SPY, and beats both in a majority of
     folds (≥ +10pp vs A and vs SPY on the aggregate). Worst single fold may trail; aggregate and
     median fold must win with margin.
   - **Sortino (absolute floor):** aggregate OOS Sortino ≥ 1.9, AND no fold below 0.9. Fixed floor.
     Never tune a mechanism whose only justification is nudging Sortino across the floor. (If
     Baseline B's own OOS Sortino lands near or below 1.9, revisit the floor BEFORE the S0 freeze,
     not mid-campaign.)
3. **OOS robustness (the overfitting gate):**
   - OOS return positive in ≥ `ceil(0.75 × fold_count)` folds.
   - Worst single-fold OOS return ≥ −15%.
   - `winnerStableAcrossFolds` true, OR the dominant candidate key wins ≥ half the folds. **A result
     carried by one fold fails this gate.** (This is also the selection signal — see "Selection
     method." If the surface is noise, you have no robust candidate, not a deployable winner.)
4. **Beats Baseline B:** aggregate OOS return > B; OOS Sortino vs B where B qualifies per the
   baseline validity rule (outright with ≥ 5% margin on folds ≥ 12 months; ≥ 90% of B on shorter
   folds; the 90%-floor comparison is exempt from the 5% rule).
5. **Drawdown:** OOS maxDD ≤ 55% in every fold. No exceptions.
6. **Capital posture:** all four posture conditions, on every fold's development window AND OOS
   segment, via `audit_backtest_posture` (thresholds 55/70/100; regime `comparisonValue` 252d,
   0.92/0.82 — match your declared regime).
7. **Reproducibility (field-level).** Re-fire the finalist's assembled-book backtest on one OOS
   window; `compare_backtests {tolerance_bps: 0}` → `identical: true`. AND `get_portfolio` the
   assembled book and confirm its `conditionFieldAudit` raw fields match the intended design (not the
   display names). Mismatch on either = engine defect = stop, document, no deploy.
8. **Live parity (field-level).** After cloning to the live book and BEFORE approving any orders,
   `get_portfolio` the live target and confirm `conditionFieldAudit` matches the source book
   field-for-field; then pull the live evaluator's condition audit
   (`query_portfolio_events` with `include_condition_audit: true`) and compare every indicator value
   in the entry/regime conditions to a same-day fresh backtest of the live target. Any field
   mismatch, or a material indicator mismatch (e.g. a long-window SMA or trailing max off by more
   than the day's move), or mutually-exclusive sleeves both evaluating true = engine defect = stop,
   decline all pending orders, report.

If any gate fails: iterate the **design** (see Process). Gates and lockbox pass conditions are frozen
at S0 and never moved.

---

## Process (stages are scaffolding, not prescriptions)

- **S0 Engine sanity** → **S1 Baselines**, both recorded before any design work.
- **Search (the cheap layer).** Invent candidate designs and tune with the fast tools:
  `create_portfolio` for a family anchor, `create_portfolio_variant` for single-change variants,
  `backtest_portfolio` + `compare_backtests` to score, `systematic_sweep` / `optimize_portfolio` to
  tune **over the walk-forward span only, never the lockbox**. Most iterations live here. Keep a
  kill-log (mechanism → stats → verdict → why). Remember principle 2: the design carries the value;
  the optimizer is a knob-setter. Invest in the family.
- **Assemble the finalist.** Build the deploy-shape book with structured `create_portfolio` (exact
  validated strategy objects; no NL re-authoring). Posture encoded in the book (regime conditions,
  budgets), not in a comment.
- **Certify with walk-forward (the go/no-go).** `run_walk_forward_study` on the assembled finalist:
  `engine_kind: sweep`, anchored, `fold_count: 4`, `mode: validation`, `validation_percent: 50`,
  `certification: true`, genes via `gene_intents` (after `get_sweep_surface` and a `preview_only`
  pass). Read per-fold + aggregate via `get_walk_forward_study_results`. Apply the **Selection
  method** to choose a robust parameterization. Gate 1 per fold via `audit_backtest_breadth`; posture
  per fold via `audit_backtest_posture`; Gates 2–6 from the OOS aggregate + per-fold table, measured
  on the assembled object. Log everything as each completes.
- **Iterate the design, not the gates.** If a gate fails, change a mechanism and re-search;
  re-certify only with a new design worth defending. **Three certification attempts on one idea is
  the ceiling**; after that widen the search instead of tuning toward the bar. A `NoEligibleCandidate`
  fold under the quality floors is honest information — widen validation or rethink the design, do not
  drop the floors.
- **Lockbox confirmation (Stage S2).** After certification passes and the design is frozen, run the
  single assembled finalist over the lockbox exactly once. Pass → sign-off. Fail → calendar-fit
  signal, no deploy without a logged override. Looking and then iterating burns it.
- **Sign-off + live deploy.** Present the deliverable. On explicit human "deploy" (or logged
  override):
  1. `get_portfolio 69a7dc7acdb6bf6a4681d36c` — audit open positions and cash.
  2. **Verify the live book's order pipeline is healthy** before cloning: check recent
     `query_portfolio_events` for `OPTION_CHAIN_EMPTY_FOR_REQUESTED` audits or eligible signals
     producing zero orders. If the chain cache is cold, deploy will signal but not fill — surface it
     to the owner before proceeding.
  3. `clone_strategies_to_portfolio` (source = assembled finalist chat portfolio). The clone REPLACES
     the live book's entire strategy set and auto-cancels its pending orders and archives any monitor.
  4. **Field-verify the clone:** `get_portfolio` the target, confirm `conditionFieldAudit` matches the
     source field-for-field (Gate 7 on the target object, not its names).
  5. Re-backtest the live target with events and `compare_backtests {tolerance_bps: 0}` vs the
     finalist's run (Gate 7 reproducibility).
  6. Re-attach the weekly monitor via `edit_portfolio addStrategies`; verify it appears in
     `get_portfolio`. (The clone archived any prior monitor; re-attaching every time is mandatory.
     Keep the monitor OUT of the finalist chat portfolio so studies/backtests stay clean.)
  7. **Gate-8 live parity** on the first evaluator tick, field-level, BEFORE approving any orders.
  8. Log everything in CAMPAIGN_LOG.md.

---

## Deploy timing + live monitoring (no paper stage)

**When a finalist passes all gates and the lockbox, it deploys LIVE** after sign-off. Risk is managed
in production:

- Gates and lockbox pass conditions are fixed at S0. Rewriting/relaxing/re-deriving any of them
  mid-campaign to convert a failure into a pass invalidates the whole campaign.
- **Human override is allowed but never silent.** A human may "deploy" a book that fails a specific
  gate (or the lockbox) ONLY by naming the failed gate with a written justification recorded verbatim
  in CAMPAIGN_LOG.md and stated in the deliverable ("failed Gate X, deployed by owner override
  because …"). The override is logged; the gate is not moved.
- No strategy edits after deploy without a new campaign.
- **Live kill thresholds** (breach action per item):
  1. **Posture (pause + alert).** Median deployment ≤ 55%; no day > 70% outside the declared regime.
  2. **Drawdown brake, two-stage.** drawdown = 1 − PortfolioValue / running-peak since deploy. Pause
     entries at ≥ 30%; full owner review and possible unwind at ≥ 55% (the Gate-5 ceiling).
  3. **SPY-excess review (review only, NOT a pause).** After 12 weeks live, if excess return vs SPY <
     −15pp, flag for owner review. Prefer a live Baseline-B proxy over SPY where available.
  4. **Order health (pause + alert).** Every rebalance pass with eligible signals produces fills;
     zero cannot-afford rejections; no `OPTION_CHAIN_EMPTY_FOR_REQUESTED`; no unexplained
     rejected/stuck orders.
  5. **Condition integrity (pause + alert).** The weekly audit verifies the live book's raw condition
     FIELDS (`conditionFieldAudit`), never display names, against the intended design. Any drift =
     pause + alert.
- **Weekly agent monitor (mandatory part of deploy):** a `LaunchAgent` strategy on the live book,
  condition `Day = Monday OR CrossBelow(SPY, SMA200(SPY)) = 1`, `cooldownMinutes: 1440`,
  `continueExisting: true`, `google/gemini-3-flash-preview` for planning and execution,
  `maxIterations: 15`, whose brief audits the five thresholds plus per-spread P&L/DTE and proposes
  actions for owner approval. Findings logged in CAMPAIGN_LOG.md weekly.

---

## Tooling

- **`get_sweep_surface`** — call FIRST on the seed before authoring any sweep. Lists valid
  `scope`/`field` pairs, default gene templates, and authoring controls. Zero cost.
- **`run_walk_forward_study`** — the certification engine. `chat_portfolio_id`,
  `global_start_date`/`global_end_date`, `fold_count` (2–8), `walk_forward_mode` (anchored), `mode`
  (validation), `engine_kind` (sweep), `gene_intents` (preferred) or `sweep_config`,
  `validation_percent` (50), `certification` (true), `oos_width_days`. Use `preview_only: true` to
  compile + cost-check without billing. Charges research tokens once on the real launch.
- **`get_walk_forward_study_results`** — per-fold train/validation/OOS stats, the aggregate,
  `selectedChatPortfolioId` per fold, `dominantCandidateKey`, `winnerStableAcrossFolds`. Zero cost.
  Source for the Selection method and Gates 2–6.
- **`get_portfolio` / `conditionFieldAudit`** — the only trustworthy view of what a book IS. Read raw
  `comparison`/`value`/`window` fields; never trust `strategy.name` / `condition.name`.
- **`audit_backtest_breadth`** — Gate-1 breadth/concentration in one call on a `backtest_id`. `rollups`
  + `gates` lists; written at finalize. `status:"unavailable"` → re-fire; never infer zeros.
- **`audit_backtest_posture`** — posture/drawdown in one call (thresholds 55/70/100; regime 252d
  0.92/0.82). Median/p90/max, day counts, per-day violations, maxDD with peak/trough/recovery.
- **`create_portfolio_variant`** — single-change candidates by JSON-Pointer `patches`; immutable
  result; check the `before` echo.
- **`compare_backtests`** — N-way vs a baseline with first-divergence date. Reproducibility
  (`tolerance_bps:0`), variant scoring, forensics.
- **`backtest_portfolio` / `optimize_portfolio` / `systematic_sweep`** — the search layer over the WF
  span (never the lockbox). Gate only on walk-forward OOS and full-window backtests of the assembled
  object, never on optimizer rolling-window stats.

---

## Search constraints (follow these; override only with an A/B pair that disproves them)

- **No stop-losses on hold-to-expiry LEAP/spread books.** Exits = DTE-based closes plus regime-gated
  profit-taking, unless a matched with/without pair proves a stop-loss helps over the full span.
- **No narrow ranked rotation (top-K ≤ 5 with a shared cadence).** Rank shuffle rotates membership
  every pass and turnover destroys the book. Breadth comes from a wide limit + an affordability
  ladder, not concurrent slots.
- **Keep `totalBudget` ≥ K × `perNameAllocation`** within each tier, or a different subset fills every
  pass and turnover explodes.
- **Ship a template ladder so every name has an affordable unit**, including the expensive tail at
  current prices. Cheap structures as the _primary_ template are an automatic kill path; tight rungs
  are for the expensive tail only.
- **Budgets cap cost basis, not market value.** Market deployment runs above the budget once positions
  appreciate. Verify posture on the tape, not the budget number.
- **One mechanism change per candidate.** Decompose multi-change assemblies; `compare_backtests`
  first-divergence attributes the effect.
- **Take-profit is `TakeProfitPct` (Action scope).** `CloseOption` pnl semantics: `minPnlPercent: 100`
  = take-profit at +100%; `maxPnlPercent: -50` = stop-loss at −50%.
- **`DaysSinceLastRebalanceOptionOrder` / `DaysSinceOrder` read `null` on fresh books, and `null >= N`
  is TRUE** — cadence-gated strategies fire at the first evaluation after deploy. The cadence clock is
  SHARED across all RebalanceOption strategies in the book.
- **Dollar-amount budgets do not de-risk as the book bleeds** the way %-of-NAV sizing does. If you use
  fixed dollars, something else must shed risk.
- **Re-sweeping an already-swept book can stack genes** (conditions/triggers accumulate). Sweep from a
  clean seed; field-audit the materialized result for duplicated/stacked conditions before trusting it.

---

## Indicator vocabulary (materials, not prescriptions; full list in the `create_portfolio` schema, ~90 types)

Inside RebalanceOption pipelines, rank `weightIndicator`s, and template `eligibility` conditions, an
indicator with an **empty `targetAsset` (`{"symbol": ""}`) evaluates per candidate name** — that is
how one rank/filter applies across the universe. Named `targetAsset`s (e.g. SPY) make it a
market-level reading.

- **Price & trend:** `Price`, `SimpleMovingAverage`, `ExponentialMovingAverage`,
  `MaximumPrice`/`MinimumPrice`, `MaxDrawdown`/`MaxDrawup`, `PriceRateOfChange`,
  `PriceStandardDeviation`, `AverageTrueRange`, `RelativeStrengthIndex`, `BollingerBand`, `VWAP`,
  `Volume`.
- **Composition:** `Plus`/`Minus`/`Multiply`/`Divide`/`Max`/`Min`/`AbsoluteValue`/`Log`/
  `Exponentiation`.
- **Meta-indicators (windows over indicators):** `IndicatorWindowAgo`,
  `IndicatorSimpleMovingAverage`/`IndicatorExponentialMovingAverage`, `IndicatorStandardDeviation`/
  `IndicatorMeanAbsoluteDeviation`, `IndicatorRateOfChange`, `TrailingSum`.
- **Events & persistence:** `CrossAbove`/`CrossBelow`, `ConsecutiveTrue`/`CountTrue`.
- **Market & macro:** `Index` (`VIX`/`SPX`), `Economic` (`UNRATE`); the regime ratio is `Price(SPY)`
  vs `Multiply(k, MaximumPrice(SPY, 252d))`.
- **Fundamentals:** `Fundamental` (`peRatioTTM`, `marketCap`, `dividendYield`, `freeCashFlow`),
  `CompoundAnnualGrowthRate(metric, years)`.
- **Book & position state:** `OptionGrossExposurePercent` (sum of abs leg marks over NAV, often
  several hundred % on spreads; not a deployment proxy; read actual values before thresholding),
  `OptionPositionCount`, `OptionUnrealizedPnL`, `OptionDaysToExpiration`, `PositionPercentChange`,
  `PositionMaxDrawdown`, `UnderlyingMaxDrawdown`, `PortfolioValue`, `BuyingPower`, the `DaysSince*`
  family.
- **Calendar:** `Day`/`Month`/`Date`.

Calibrate every threshold against observed values (condition audits, equity tapes), never intuition.

### Composed-indicator recipes (copy, modify, or ignore — per-name unless noted)

- **Momentum acceleration:** `ROC(21) − IndicatorWindowAgo(ROC(21), 21d)`.
- **Momentum smoothness (Sharpe-like rank):** `ROC(63) / PriceStandardDeviation(63)`.
- **Vol compression (squeeze):** `ATR(14) / IndicatorSMA(ATR(14), 100d)`, below ~0.8 coiled.
- **Pullback depth in ATR units:** `(MaximumPrice(252) − Price) / ATR(14)`.
- **Parabolic-extension guard:** `(Price − SMA(20)) / ATR(14)`.
- **Trend persistence:** `CountTrue(Price > SMA(50), 63d)`.
- **Relative strength vs market:** `ROC(63, name) − ROC(63, SPY)`.
- **Upside/downside asymmetry:** `MaxDrawup(63) / MaxDrawdown(63)`.
- **Volume thrust:** `Volume / IndicatorSMA(Volume, 50d)`.
- **Adaptive vol regime (market):** `Index(VIX) / IndicatorSMA(Index(VIX), 20d)`.

### Searches worth running (suggestions)

- **Per-template `eligibility` gates**, structure-by-name-state.
- **Structure-by-regime**, different template sets per regime tier (separate RebalanceOption per tier).
- **Underlying-state exits**, one CloseOption per name on its own state; trend exits without a mark
  stop. Search this before any mark-based stop.
- **Exposure-keyed de-risk**, CloseOption on `OptionGrossExposurePercent`; read actual values from an
  events run first.
- **Entry-condition gates**, regime ratios, drawdown, vol filters; sweep with explicit `gene_intents`.

---

## Deliverable (present at sign-off)

Per-fold table + aggregate row + lockbox row:

| Fold          | Dev window | OOS window                   | OOS return      | OOS maxDD | OOS Sortino     | Names filled /20 | Median deploy | %days >70% (in regime?) | vs A | vs B | vs SPY |
| ------------- | ---------- | ---------------------------- | --------------- | --------- | --------------- | ---------------- | ------------- | ----------------------- | ---- | ---- | ------ |
| 1 … N         |            |                              |                 |           |                 |                  |               |                         |      |      |        |
| **Aggregate** |            |                              | mean/median/min | worst     | mean / min-fold |                  |               |                         |      |      |        |
| **Lockbox**   | (held out) | (run date − 126d) → run date |                 |           |                 | (eligible)       |               |                         |      |      |        |

Plus: the walk-forward study id; the **robust parameterization chosen and why** (dominant key / fold
coverage, not a single fold's argmax); full strategy rules in plain English; the declared opportunity
regime; the kill-log; finalist chatPortfolioId; OOS-robustness summary (folds positive, worst fold,
winner stability); per-fold breadth audit; the **lockbox confirmation** PASS/FAIL; **field-level
reproducibility** PASS/FAIL; the **field-level Gate-8 live parity** result; any logged owner override;
and (post-deploy) weekly monitor reports appended to CAMPAIGN_LOG.md.

**The headline characterization is the OOS aggregate of the assembled, directly-measured book. Never
lead with a single-window, in-sample, or certified-fold-winner number.**

## Working rules

- Keep CAMPAIGN_LOG.md current at every stage; it is the article's spine. S0/S1 outcomes recorded
  before any design work.
- Search with standard optimize/variants/backtests; certify with walk-forward. Don't conflate them.
- Select on cross-fold robustness, not single-fold validation max. A different winner every fold means
  no deployable winner yet.
- Verify everything that will trade real money at the FIELD level (`conditionFieldAudit`), never by
  display name.
- Measure deploy decisions on the directly-backtested assembled object, never on certified
  fold-winner numbers for a different object.
- The lockbox is held out from ALL search and ALL folds; touched exactly once at S2. Any earlier touch
  burns it.
- Compare every certified candidate against both baselines on the same fold calendar.
- An honest "no deploy, OOS failed" — or "no robust winner exists" — is a successful campaign outcome.
  Do not torture the search; **three certification attempts on one idea is the ceiling**, then widen.
- Gates and lockbox pass conditions are fixed at S0. Override only with a logged, named-gate owner
  justification.
- Deploy only after explicit human "deploy" (or a logged owner override on a named gate/lockbox).
