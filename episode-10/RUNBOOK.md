# Runbook: Walk-Forward Options Campaign → Deploy Live

> **Paste this whole file into a fresh LLM session** with the NexusTrade MCP server connected.
> Account-independent and copy/paste-ready: it builds its own baselines, names its own per-run log,
> and discovers the deploy target at sign-off — it never assumes any specific account.
> Follow top to bottom. Do not ask clarifying questions during the campaign; execute. (The ONE
> interactive point is deploy sign-off, which is required to ask — see Deploy.)
> **Ships with `snapshots/`** — `baseline_a.json`, `baseline_b.json`, `incumbent.example.json` —
> which the agent loads via `create_portfolio`. Keep that folder alongside this file. Apart from
> reading those snapshots, every runtime step uses MCP tools only; no other repo checkout.

---

## Owner's thesis (READ FIRST — the WHY behind the design; fixed priors, not things to re-litigate)

1. **The 20-name universe is a personal, conviction watchlist.** These are names I like and hold a
   fundamental view on — I want exposure to *these companies*, not a screened or optimized universe.
   So the universe is FIXED (see watchlist). Do not add, drop, or substitute names, and do not spend
   effort questioning the picks; treat them as given.
2. **Momentum on individual tickers is the chosen edge.** I've found single-name momentum to
   generalize well, so the design family is momentum-first (rank/ride strength on these names). You
   may design *how* momentum is expressed — signal, structure, deltas, DTE, regime, exits — but the
   momentum-on-single-names premise is the starting prior, not a hypothesis to discard. Other
   mechanism families (regime-switch, credit, calendars) are allowed in the certification body to
   stress-test the design, but the deploy intent is an aggressive momentum book on this watchlist.

This is why the book is what it is: conviction names + single-name momentum + aggressive convex
expression, risk-shaped (not neutered) by the gates and the capital-posture policy. Everything below
serves this thesis.

---

## Design philosophy

**This runbook prescribes WHAT must be true, never HOW to achieve it.**

- **Fixed:** the universe, the capital, the calendar, the gates, the selection method, the
  live-monitoring rules, the capital-posture policy, the lockbox, and the deploy procedure.
- **Yours to design:** everything else — signals, structures, deltas, DTEs, cadence, breadth,
  filters, exits, sizing, regime switches. If a design clears the gates, it is valid.

### The hard-won lesson that shapes everything (read twice)

These are methodology lessons from prior campaign runs, not open engine defects. The certification
engine (sweep walk-forward, fold-winner persistence, validation-window scoring, cross-fold robust
selection, field-level audits) is the current production contract.

1. **Validation score is a noisy proxy for out-of-sample. Maximizing it per fold does not find the
   OOS-best book.** Picking the single highest-validation candidate on each fold is high-variance.
   **You do not deploy the per-fold argmax.** You deploy the parameterization that is **robust across
   folds** — use `aggregate.crossFoldRobustSelection` (minimax validation Sortino) plus the Selection
   method below. This is mandatory, not advisory.
2. **The value lives in the DESIGN, not the optimizer.** Treat the optimizer as a modest, robust
   knob-setter that confirms a design's neighborhood, never as a discoverer of magic. Spend effort
   on the family; ask the optimizer for little.
3. **Only the deployable object is real. Verify it at the FIELD level, never by name.** Strategy
   and condition _display names_ can be stale; the `comparison`/`value`/`window` fields are what
   trade. Every certification, reproducibility, and parity check reads `conditionFieldAudit` (raw
   fields), never `strategy.name` or `condition.name`.
4. **Reproducibility is a property of the PROCESS, not a backtest number.** Make the process
   deterministic, field-verified, and auditable; live performance is the only true out-of-sample.

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
   different optimized winner — that is the noise signal. The deploy book is a **separately
   assembled, fixed deploy-shape portfolio** chosen by the cross-fold selection method below; its
   right to deploy is earned by the WF OOS aggregate on that assembled object, the lockbox
   confirmation, and field-level reproducibility/parity.
3. **OOS is the only headline.** Training and validation are in-sample. Never present a train or
   validation number as evidence the book generalizes. The per-fold OOS table and its aggregate
   are the result.

**Strategy intent:** a deliberately high-risk momentum book on my favorite names. Aggressive is
fine — leverage, convexity, concentration-in-time are on the table. The gates shape the risk; they
are not there to make the book timid. (See **Owner's thesis** at the top for the WHY.)

## Campaign log (per-agent, isolated — read and write ONLY your own)

Each run writes to its OWN uniquely-named log file. Do not use a single shared log shared across runs.

- **Filename:** `<AGENT>_CAMPAIGN_LOG_<UTC-TIMESTAMP>.md` in `episode-10/`, where `<AGENT>` is your
  client (`CLAUDE_CODE`, `CURSOR`, etc.) and `<UTC-TIMESTAMP>` is the run-start instant as
  `YYYYMMDDTHHMMSSZ` — e.g. `CLAUDE_CODE_CAMPAIGN_LOG_20260613T101500Z.md`. Create it as your very
  first action and append as you go.
- **Isolation is mandatory.** Multiple agents may run this runbook concurrently. Do NOT read, diff,
  import, or reference any other `*_CAMPAIGN_LOG_*.md`, nor any chat portfolio / study / backtest ID
  you did not create in THIS run. Each run reproduces the whole pipeline from S0 independently and
  builds its own baselines. Never reuse another run's artifacts.
- Throughout this document, **`<RUN_LOG>`** means this file. Every "log / record / report"
  instruction refers to it.

## Execution mandate (NON-SKIPPABLE — the campaign is INVALID without this)

**This is a certification campaign.** The deploy / no-deploy verdict rests on a body of
**walk-forward sweep certifications**, never on `backtest_portfolio` numbers. Read this before
designing anything.

1. **Certification is the workhorse — run it liberally; there is NO token budget here.** Do not
   minimize calls or "do just enough." Point `run_walk_forward_study` (`engine_kind: sweep`,
   `certification: true`, `validation_percent: 50`) at real candidate seeds, repeatedly, across the
   grid and across families. The S0 smoke run and the S1 baseline scoring runs **DO NOT COUNT**
   toward this — they are contract checks and benchmarks, not candidate certifications.
2. **A verdict is FORBIDDEN from the search layer.** `backtest_portfolio` / `create_portfolio_variant`
   results may only KILL or PROMOTE an idea into certification — they may never end the campaign.
   Issuing any verdict — and especially "no deployable winner" / "structural infeasibility" —
   without optimizing certifications having run on candidate seeds makes the campaign **INVALID**
   (not "an honest no-deploy"). **This is the single most important rule in this document.** (It is
   exactly the line a prior run crossed: it declared infeasibility having run ZERO optimizing
   certifications.)
3. **Minimum certification body before any "no robust winner" / infeasibility verdict:**
   - **≥ 3 distinct MECHANISM FAMILIES certified** — genuinely different mechanisms, not three tweaks
     of one family. Family menu (pick ≥ 3; invent more freely): (a) momentum-long calls/verticals;
     (b) regime-switch long/flat (deploy gated on an opportunity-regime signal, flat otherwise);
     (c) defined-credit / short-premium that earns in flat/down tape; (d) calendar / diagonal
     time-spreads; (e) protective-collar or put-spread-financed longs.
   - **Each family: up to 3 certification attempts** (re-sweep from a CLEAN seed with refined
     `gene_intents`, deeper grid, or wider validation) before the family is "exhausted." Realistic
     floor: ~3–9 sweep certifications, **plus the incumbent (Baseline C) certified as a seed.**
   - **Each sweep must be non-trivial: ≥ 3 `gene_intents` axes × ≥ 3 values each** (e.g.
     `BuyingPowerPct`, `TakeProfitPct`, `RollTriggerDte`, rank depth, delta band, DTE). A 1-axis or
     2-value sweep does NOT satisfy this — the optimizer needs a real surface to certify.
   - **`systematic_sweep` over the deployment × structure × DTE × delta grid is mandatory** in the
     search layer before any design neighborhood is declared dead. Never conclude from a handful of
     hand-built books.
4. **Per-family certification ledger in `<RUN_LOG>`** — a family with no ledger row was NOT explored:
   | Family | Seed id | `get_sweep_surface` ✓ | gene_intents axes | Study id | `crossFoldRobustSelection` key | Assembled book id | Per-fold OOS gate result | PROMOTE / KILL (reason) |
5. **No infeasibility claim from N hand-built points.** Any "the gates can't be met" statement must
   cite the `systematic_sweep` + the ≥ 3-family certification body, and must name the SINGLE binding
   gate per family with its study-id evidence. **One counterexample in your own data** (e.g. a
   candidate that clears the return hurdle) forbids a blanket infeasibility claim — localize the
   binding constraint, do not generalize.

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
| `validation_percent`                     | **50** (long validation windows — mandatory, see "Why 50")             |
| `certification`                          | **true** (activity + quality floors on fold-winner selection)          |
| `baseline_symbol`                        | SPY                                                                    |
| Live deploy target                       | DISCOVERED at sign-off via `fetch_portfolios` — not hardcoded (see Deploy) |
| Baseline A (equity B&H, 20 names)        | load `snapshots/baseline_a.json` → `create_portfolio` at S1            |
| Baseline B (naive LEAP ladder, 20 names) | load `snapshots/baseline_b.json` → `create_portfolio` at S1           |
| Baseline C (incumbent — the bar to beat) | FROZEN published OOS stats (see "Performance targets"); seed = `snapshots/incumbent.json` if present else `snapshots/incumbent.example.json` |

**Why `validation_percent: 50` is mandatory.** Short validation splits make fold-winner selection
noisy on convexity books and can yield `NoEligibleCandidate` under the quality floors — honest
information, not a bug. Long validation windows (8–20 months) are the biggest lever for stable
selection. The server defaults to 50 when `certification: true`; do not override without a logged
reason.

**Why `certification: true`.** Activity and quality floors (participation ≥ 0.35, distinct names ≥
9, validation return ≥ 0, validation Sortino ≥ 0.5) evict degenerate thin-book validation winners.
A fold returning `NoEligibleCandidate` means the design cannot be cleanly certified on that window
— widen validation or rethink the design; do not drop the floors.

Build Baselines A and B at S1 by loading their committed snapshots
(`snapshots/baseline_a.json`, `snapshots/baseline_b.json`) via `create_portfolio` (structured
payload — account-independent, deterministic), then scoring them on the current engine. Record
their IDs + per-fold OOS in `<RUN_LOG>` before designing anything. Do not reuse stale baseline runs.
Baseline C is the FROZEN incumbent bar (see "Performance targets"), not rebuilt.

Seed affordability note: any single-template ~$1k-per-name book structurally fails Gate 1. Minimum
defined-risk structures on the expensive tail (META/LLY/GS/TSM/ADI/AVGO) cost $1.3–2.4k per
contract. Every template set must end in a rung the most expensive name can fill at the configured
per-name allocation. Do not remove the cheapest rung when sweeping structures.

Baseline B definition (canonical; the committed `snapshots/baseline_b.json` is exactly this): all 20
names, no rank, no filter, 14-day cadence, 8%-of-portfolio per name under a 95% budget, structure =
first affordable rung of [Δ0.50 call → Δ0.55/0.25 vertical → Δ0.55/0.40 vertical → Δ0.50/0.42
vertical], all 180–365 DTE, single exit at DTE ≤ 45. Naive in mechanism, honest in participation.
Baselines are benchmarks, not candidates.

**Baseline validity rule (applied per fold):**

- **Baseline A is a return bar only**, never a Sortino bar. Its Sortino reflects equity-rally
  smoothness a leveraged long-premium book cannot match; comparing to it is incoherent.
- **Baseline B is a return bar, and a Sortino bar in folds where it has ≥ 9/20 breadth**
  (`rollups.distinctNamesFilled` from `audit_backtest_breadth` on that OOS segment). Where B fails
  breadth in a fold, the absolute Sortino floor (Gate 2) is the only Sortino constraint there. If
  S1.5 fires, use the POSTURE-MATCHED B for Gate 4 (the original fully-deployed B is reference only).
- **Baseline C (the incumbent) is BOTH a return bar AND a Sortino bar, every fold** — it is the live
  book the campaign exists to beat. The finalist must beat C on return AND Sortino, per fold and
  aggregate. C's frozen numbers are in "Performance targets" below.

---

## Engine choice: sweep, not GA (fixed)

Certification uses `engine_kind: sweep` — a bounded, typed grid over a small number of knobs.
Open-ended GA is **not** used for deploy-grade certification (`certification: true` + GA is
rejected unless `allow_ga_certification: true`). Reason: GA mutates genome structure (comparators,
constants, window lengths), producing degenerate thin-book winners and scrambled conditions. A
bounded sweep only moves the knobs you name.

**Authoring a sweep (the only supported path):**

1. `get_sweep_surface` on the seed portfolio first — valid `scope`/`field` pairs, default gene
   templates, authoring controls. Do not hand-guess field names.
2. Build genes with **`gene_intents`** (plain English, one per axis). The server compiles and
   validates them. Prefer this over hand-authored `sweep_config` JSON.
   - Take-profit is `TakeProfitPct` on **Action** scope. Never sweep take-profit as an
     `ExitCondition` / `OptionPositionPercentChange`.
   - Roll DTE is `RollTriggerDte` on **Action** scope (roll CloseOption only).
3. `run_walk_forward_study` with `preview_only: true` first — compiles genes and estimates cost
   without billing. Confirm compiled `scope`/`field` and value labels, then launch for real.

---

## Selection method (fixed — this is the core of the methodology)

When the study completes, you do **not** deploy the per-fold validation argmax. You select the
parameterization that is **robust across the whole calendar**:

1. From `get_walk_forward_study_results`, read the per-fold OOS table, `aggregate`, and every
   fold's `selectedChatPortfolioId`. Confirm winners persisted and materialized (real IDs, no
   `materializationError`).
2. **Read `aggregate.crossFoldRobustSelection`.** This is the engine's cross-fold robust pick:
   the grid cell with the highest **minimum validation Sortino** across all completed folds
   (`metric: "minSortino"`, `candidateKey`, `score`, `perFoldSortino`). **Start here.** Compare
   its `candidateKey` to each fold's `selectedCandidateKey` and to
   `aggregate.dominantCandidateKey` / `winnerStableAcrossFolds`.
3. **Prefer cross-fold robustness over single-fold spikes.** If `crossFoldRobustSelection` disagrees
   with one fold's argmax, treat that as the expected noise signal — do not deploy fold-3's winner
   because it spiked. If `winnerStableAcrossFolds` is false and `crossFoldRobustSelection` is
   absent or weak (no cell covers all folds), the surface is noise: deepen search or widen
   validation; you have no deployable winner yet.
4. **Assemble the deploy book from the robust parameterization** (`crossFoldRobustSelection.candidateKey`
   or a centroid of the top cluster — parameter values most common among top-ranked cells), not by
   cloning a single fold's materialized winner. Build deploy-shape with structured
   `create_portfolio` (validated strategy objects); posture encoded in conditions/budgets.
5. **Measure the assembled book directly.** Backtest it on each fold's OOS window and the aggregate.
   The deploy decision rests on _the assembled object's measured OOS_, never on certified fold-winner
   numbers for a different object.

---

## Stage S0 — Engine sanity (MANDATORY; blocks everything)

Quick contract checks before trusting certification. Record every S0 outcome in `<RUN_LOG>`.

1. **Walk-forward sweep smoke.** `create_portfolio` a trivial chat book (e.g. SPY > SMA50).
   `run_walk_forward_study`: `mode: validation`, `fold_count: 2`, `engine_kind: sweep`, one
   `gene_intent` × 3 values, `certification: false`. Must start and complete with per-fold OOS +
   aggregate via `get_walk_forward_study_results`. Failure → **STOP, report.**
2. **Window fidelity (one fold).** On a completed fold from (1) or a prior cert: note validation and
   OOS windows. `backtest_portfolio` the materialized fold winner on each window; fold
   `validationStatistics` and `oosStatistics` must match standalone backtests within rounding.
   Also confirm disjointness: train ∩ validation, train ∩ OOS, validation ∩ OOS empty; OOS starts
   after validation ends. Mismatch → **STOP, report.**
3. **Persistence.** `get_walk_forward_study_results` returns a real `selectedChatPortfolioId` for
   every completed fold. Missing → **STOP, report.**
4. **Dead-name handling (SNDK).** Tiny `backtest_portfolio` over a 2022 window on the 20-name
   universe. **Pass:** SNDK absent or in not-yet-listed reject lists with **no fabricated price/
   indicator values**. **Fail:** engine errors, or any non-null reading for a name that did not
   trade.

Only after S0 passes do you design anything.

---

## Stage S1 — Baselines as OOS bars (A, B, AND C the incumbent)

Run `run_walk_forward_study` (anchored, `fold_count: 4`, `oos_width_days: 252`,
`validation_percent: 50`, `mode: validation`, `inner_mode: backtest_only`, walk-forward span ending
at lockbox cutoff) on **Baseline A and Baseline B** (loaded from `snapshots/baseline_a.json` and
`snapshots/baseline_b.json`). Record per baseline: each fold's OOS return + Sortino + maxDD, OOS
aggregate, and per-fold breadth (which folds give B ≥ 9/20). Confirm Baseline B's per-fold breadth
audit shows no `namesWithZeroResolutionAttempts` for **eligible** names whose signals should
have fired.

**Baseline C (the incumbent bar) is FROZEN, not rebuilt.** Its per-fold + aggregate OOS numbers are
already published in "Performance targets" — copy them into `<RUN_LOG>` as the bar; do not recompute.
(They are account-independent: the incumbent's strategies are private.) Separately, a **seed**
representing the incumbent mechanism is available for the certification loop: load
`snapshots/incumbent.json` if the operator dropped one in, else `snapshots/incumbent.example.json`.
That seed (or a tuned version) may be certified like any candidate; if it clears the gates +
lockbox, it is a valid finalist. Keep the bar (frozen stats) and the seed (a portfolio) distinct in
`<RUN_LOG>` — and never merge "search found no new winner" with "the incumbent bar wasn't beaten."

### Stage S1.5 — Gate-coherence / feasibility check (before any design)

Before designing candidates, confirm the gate set is **jointly satisfiable** against the measured
baselines — specifically the tension between **Gate 4 (beat Baseline B)** and the **≤ 55% posture
cap** (Gate 6). Baseline B is a 95%-deployed, fully-invested book; a posture-capped finalist cannot
out-deploy it, so requiring the finalist to beat B's return *and* per-fold Sortino while held to
≤ 55% median deployment may be impossible by construction.

**If the check shows the gates are jointly unsatisfiable, AUTO-RELAX Baseline B (deterministic, no
owner round-trip):**

1. Rebuild Baseline B with its `totalBudget` derated so its OWN measured median daily deployment is
   ≤ 55% (`audit_backtest_posture` on a full-span backtest; lower the budget until median ≤ 55%).
   This makes B a **posture-matched** bar — apples-to-apples with the finalist constraint.
2. Re-run B's S1 walk-forward scoring on the posture-matched book; these become the Gate-4 numbers.
3. Log the substitution explicitly in `<RUN_LOG>` (original B IDs/returns, derated budget, new
   posture-matched B IDs/returns) and flag it in the deliverable. The ORIGINAL fully-deployed B is
   retained as an unconstrained over-bar for reference only.

This is a fixed, automatic step — not a gate relaxation and not an owner decision. The posture cap
and all gate thresholds stay frozen; only the benchmark is made comparable.

---

## Performance targets — Baseline C (the incumbent bar; FROZEN)

This is the published, account-independent bar the finalist must beat. It is the live
"Public Portfolio Challenge" book **backtested over the campaign OOS folds** (same calendar as
A/B), `initial_value` 25000, baseline SPY. **Numbers only — the incumbent's strategy rules are
private and are NOT part of this runbook.** These figures are frozen at S0; do not recompute or
re-baseline mid-run.

| Fold | OOS window               | Return    | Sortino | maxDD  | Breadth /20 |
| ---- | ------------------------ | --------- | ------- | ------ | ----------- |
| 0    | 2023-05-07 → 2024-01-14  | +24.17%   | 1.47    | 17.06% | 10          |
| 1    | 2024-01-14 → 2024-09-22  | +8.78%    | 0.64    | 18.47% | 9           |
| 2    | 2024-09-22 → 2025-06-01  | +66.87%   | 5.60    | 16.56% | 9           |
| 3    | 2025-06-01 → 2026-02-08  | +137.51%  | 4.37    | 17.35% | 7           |
| **Aggregate** |                 | **mean +59.33%** / min +8.78% | **mean 3.02 / min 0.64** | worst 18.47% | |
| Full span | 2023-05-07 → 2026-02-08 | **+441.9%** | 2.43 | 24.0% | 16 |

**The finalist must beat Baseline C on BOTH return AND Sortino, per fold AND aggregate** (this is
part of Gate 4). C is a genuine, well-risk-managed bar: ~17–18% per-fold maxDD with strong convex
upside. Beating it at ≤ 55% posture is the real objective — design and certify accordingly.

> Operator note (only if you ARE the incumbent's owner and want to refresh the bar on a new run
> date): re-backtest your live book over the then-current OOS folds and replace this table, logging
> old→new in `<RUN_LOG>`. Everyone else treats these numbers as fixed.

### The consolidated bar (compute the two account-relative numbers at S1, then FREEZE all of it)

Before designing, write this target block into `<RUN_LOG>` and freeze it:

- **Return:** aggregate OOS ≥ max(Baseline A, SPY) + 10pp **AND** > Baseline B (posture-matched if
  S1.5 fired) **AND** > Baseline C aggregate (+59.33%). Majority of folds beat A and SPY.
- **Sortino:** aggregate ≥ 1.9; every fold ≥ 0.9; beat Baseline B per-fold where B has ≥ 9 breadth;
  **beat Baseline C per-fold and aggregate** (agg > 3.02; clear every fold incl. F2's 5.60).
- **Drawdown:** OOS maxDD ≤ 55% every fold. **Posture:** median deployment ≤ 55%, > 70% only in
  the declared opportunity regime.
- The deliverable restates each as **target vs achieved** so pass/fail is unambiguous.

---

## Stage S2 — Lockbox confirmation (single touch, after design freeze)

The walk-forward span stops `lockbox_width_days` before the run date. That final window is the
lockbox: no fold, sweep, or search touches it. Only the assembled deploy-shape book that **passed
every gate on the WF aggregate** runs over the lockbox exactly once after design freeze.

**Pass conditions (frozen at S0):**

- Lockbox OOS return ≥ worst single-fold WF OOS return.
- Lockbox maxDD ≤ 55%.
- Posture clean over the lockbox (`audit_backtest_posture`, all four conditions).
- Breadth ≥ 9 **eligible** names over the lockbox (`audit_backtest_breadth`).

A lockbox failure is calendar-fit selection pressure. Do not deploy except by logged owner
override naming the lockbox.

**Single-touch is absolute.** If you look at the lockbox and then iterate the design, the lockbox is
burned — move the WF span back and hold out a fresh tail before any deploy.

---

## Gates — the ONLY constraints on design. The finalist must pass ALL.

Evaluated on the **walk-forward OOS aggregate and per fold**, on the assembled deploy-shape book,
measured directly (never on certified fold-winner numbers for a different object).

1. **Breadth & anti-concentration** (per fold dev backtest AND OOS segments, via
   `audit_backtest_breadth`):
   - **Not-yet-listed names** excluded from breadth shortfall reasoning per fold (Gate 1 rule).
   - `gates.namesWithRejectionsAndZeroFills` empty for eligible names.
   - Cumulative participation ≥ 13/20; ≥ 9/20 in each OOS segment.
   - Concentration (per fold dev): no single name > 25% entry notional; top-5 ≤ 60%.
   - `gates.namesWithZeroResolutionAttempts` empty for eligible names whose signal should have fired.
2. **OOS beats buy & hold:**
   - **Return:** aggregate OOS beats Baseline A AND SPY (≥ +10pp vs each on aggregate); majority of
     folds beat both.
   - **Sortino (absolute floor):** aggregate OOS Sortino ≥ 1.9; no fold below 0.9. Fixed floor.
3. **OOS robustness (the overfitting gate):**
   - OOS return positive in ≥ `ceil(0.75 × fold_count)` folds.
   - Worst single-fold OOS return ≥ −15%.
   - `winnerStableAcrossFolds` true OR `crossFoldRobustSelection.candidateKey` matches
     `dominantCandidateKey` with ≥ half the folds, OR cross-fold robust pick covers all folds with
     acceptable min Sortino. **A result carried by one fold fails.**
4. **Beats Baseline B AND Baseline C:** per baseline validity rule. B per its validity rule
   (posture-matched if S1.5 fired). **C (the incumbent) on BOTH return AND Sortino, per fold AND
   aggregate** — see "Performance targets" for the frozen numbers.
5. **Drawdown:** OOS maxDD ≤ 55% every fold.
6. **Capital posture:** all four conditions on every fold dev window AND OOS segment.
7. **Reproducibility (field-level).** Re-fire assembled-book backtest on one OOS window;
   `compare_backtests {tolerance_bps: 0}` → `identical: true`. `get_portfolio` +
   `conditionFieldAudit` matches intended design (fields, not names).
8. **Live parity (field-level).** After clone, before approving orders: `get_portfolio` target vs
   source field-for-field; `query_portfolio_events` with `include_condition_audit: true` vs same-day
   backtest. Mismatch → stop, decline pending orders, report.

If any gate fails: iterate the **design**. Gates and lockbox conditions are frozen at S0.

**Verdict preconditions (a verdict is invalid otherwise):**

- **A gate failure on a candidate is only meaningful after that candidate was CERTIFIED** (sweep WF
  + `crossFoldRobustSelection` + assembled-book OOS). A hand-built `backtest_portfolio` that fails a
  gate kills that draft, not the family.
- **"No deployable winner" / "no robust winner" requires the full minimum body** (Execution mandate
  §3: ≥ 3 families certified, `systematic_sweep` run, incumbent certified as a seed, ledger complete).
- **Binding-constraint attribution:** every kill names the SINGLE failed gate and cites its certified
  evidence (study id + the numbers). "It generally underperformed" is not a kill reason.
- **Remedy-coherence:** any remedy you propose must be consistent with the killed candidate's
  MEASURED state. Do not propose "raise deployment / posture" for a book that failed while already
  under the cap; do not propose "add convexity" for one that failed on drawdown. Diagnose from the
  posture/breadth/OOS numbers actually observed.

---

## Process (stages are scaffolding, not prescriptions)

- **S0 Engine sanity** → **S1 Baselines**, recorded before design work.
- **Search (cheap layer — picks SEEDS, never issues verdicts).** `create_portfolio`, variants,
  `backtest_portfolio`, `optimize_portfolio`, and a **mandatory** `systematic_sweep` over the
  deployment × structure × DTE × delta grid (WF span only — **never the lockbox**). Kill-log every
  mechanism. Output of this layer is a ranked set of SEEDS to certify, nothing more.
- **Certify (the workhorse — run it for EVERY candidate family; ≥ 3 families total).** For each seed:
  1. `get_sweep_surface` on the seed (never hand-guess field names).
  2. `run_walk_forward_study` with `preview_only: true` to compile genes + cost-check.
  3. `run_walk_forward_study`: `engine_kind: sweep`, `certification: true`, `validation_percent: 50`,
     `fold_count: 4`, **≥ 3 `gene_intents` axes × ≥ 3 values each**.
  4. `get_walk_forward_study_results` → apply the **Selection method** via `crossFoldRobustSelection`.
  5. **Assemble** the deploy-shape book from the robust parameterization (structured
     `create_portfolio`), then **gate on the assembled object's directly-measured per-fold OOS**.
  6. Write the **certification ledger row** in `<RUN_LOG>` (Execution mandate §4).
  Up to **3 attempts per family** (re-sweep from a clean seed), then that family is exhausted and
  you widen to the next family. Do not stop at one family; do not stop at one attempt.
- **Lockbox (S2).** Single touch after freeze.
- **Sign-off + deploy** (explicit human "deploy" or logged override) — **deploy target is DISCOVERED,
  never hardcoded:**
  0. **Discover the target.** `fetch_portfolios` (`include_live: true`). Identify suitable
     live-trading portfolios (a broker-linked `type: "live"` book). **Then ASK the owner:**
     - exactly one suitable live book → propose deploying to THAT one and ask for explicit confirmation;
     - more than one → list them and ask WHICH to deploy to;
     - none → report that no live target exists; stop (the finalist is certified + lockbox-passed and
       deploy-ready, but there is nothing to deploy into). Never invent or assume an ID.
  1. `get_portfolio <confirmed target>` — audit positions/cash.
  2. Verify live order pipeline (`query_portfolio_events` — no cold chain / empty-chain audits).
  3. `clone_strategies_to_portfolio` to the confirmed target (replaces strategy set; archives monitor).
  4. Field-verify clone (`conditionFieldAudit` source vs target).
  5. Re-backtest live target; `compare_backtests {tolerance_bps: 0}` vs finalist (Gate 7).
  6. Re-attach weekly monitor via `edit_portfolio addStrategies`; verify in `get_portfolio`.
  7. **Gate-8 live parity** on first evaluator tick before approving orders.
  8. Log everything in `<RUN_LOG>`.

---

## Deploy timing + live monitoring (no paper stage)

**When a finalist passes all gates and the lockbox, it deploys LIVE** after sign-off.

- Gates and lockbox frozen at S0. Mid-campaign relaxation invalidates the campaign.
- **Human override:** name the failed gate/lockbox, verbatim justification in `<RUN_LOG>` and
  deliverable.
- No strategy edits after deploy without a new campaign.
- **Live kill thresholds:**
  1. Posture: median ≤ 55%; no day > 70% outside declared regime.
  2. Drawdown brake: pause entries at ≥ 30% from deploy peak; full review at ≥ 55%.
  3. SPY-excess review (not pause): after 12 weeks, excess < −15pp → owner review.
  4. Order health: fills on eligible signals; no cannot-afford rejections; no
     `OPTION_CHAIN_EMPTY_FOR_REQUESTED`.
  5. Condition integrity: weekly field audit vs intended design.
- **Weekly agent monitor (mandatory):** `LaunchAgent`, `Day = Monday OR CrossBelow(SPY, SMA200(SPY)) = 1`,
  `cooldownMinutes: 1440`, `continueExisting: true`, `google/gemini-3-flash-preview`,
  `maxIterations: 15` — audits thresholds + per-spread P&L/DTE. Keep monitor OFF finalist chat
  portfolio.

---

## Tooling

- **`get_sweep_surface`** — call FIRST. Valid scope/field pairs, gene templates. Zero cost.
- **`run_walk_forward_study`** — certification. `engine_kind: sweep`, `gene_intents`,
  `validation_percent: 50`, `certification: true`, `preview_only: true` to compile/cost-check.
- **`get_walk_forward_study_results`** — per-fold stats, aggregate (`crossFoldRobustSelection`,
  `dominantCandidateKey`, `winnerStableAcrossFolds`), `selectedChatPortfolioId` per fold.
- **`get_portfolio` / `conditionFieldAudit`** — what a book IS (fields, not names).
- **`audit_backtest_breadth`** / **`audit_backtest_posture`** — Gates 1 and 6.
- **`create_portfolio_variant`**, **`compare_backtests`**, **`backtest_portfolio`**,
  **`systematic_sweep`** — search layer (WF span only, not lockbox).

---

## Search constraints (follow these; override only with an A/B pair that disproves them)

- **No stop-losses on hold-to-expiry LEAP/spread books** unless A/B proves otherwise.
- **No narrow ranked rotation (top-K ≤ 5 with shared cadence).**
- **`totalBudget` ≥ K × `perNameAllocation`** per tier.
- **Template ladder** so every name has an affordable unit; cheap structures as primary = kill path.
- **Budgets cap cost basis, not market value** — verify posture on tape.
- **One mechanism change per candidate.**
- **Take-profit is `TakeProfitPct` (Action scope).** `CloseOption` pnl: `minPnlPercent: 100` = +100%
  TP; `maxPnlPercent: -50` = −50% stop.
- **`DaysSinceLastRebalanceOptionOrder` / `DaysSinceOrder`:** `null >= N` is TRUE on fresh books;
  shared cadence clock across RebalanceOption strategies.
- **Dollar budgets do not de-risk like %-of-NAV sizing.**
- **Re-sweep from a clean seed** — re-sweeping an already-swept book can stack genes; field-audit
  for duplicated conditions before trusting.

---

## Indicator vocabulary (materials, not prescriptions; full list in `create_portfolio` schema, ~90 types)

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
- **Market & macro:** `Index` (`VIX`/`SPX`), `Economic` (`UNRATE`); regime ratio = `Price(SPY)` vs
  `Multiply(k, MaximumPrice(SPY, 252d))`.
- **Fundamentals:** `Fundamental`, `CompoundAnnualGrowthRate(metric, years)`.
- **Book & position state:** `OptionGrossExposurePercent`, `OptionPositionCount`,
  `OptionUnrealizedPnL`, `OptionDaysToExpiration`, `PositionPercentChange`, `PortfolioValue`,
  `BuyingPower`, `DaysSince*` family.
- **Calendar:** `Day`/`Month`/`Date`.

Calibrate thresholds against observed values, never intuition.

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

- Per-template `eligibility` gates; structure-by-regime; underlying-state exits;
  exposure-keyed de-risk; entry-condition gates via `gene_intents`.

---

## Condition & composition patterns (copy-paste skeletons)

> **The authoritative, exhaustive lists live in the `create_portfolio` schema you receive every
> run** (~90 indicator `type`s; all action types; the full condition grammar). READ THAT SCHEMA for
> completeness — do not treat the lists in this runbook as exhaustive; they curate the common,
> high-value shapes. Validate any draft with `build_portfolio` before `create_portfolio`.

**Condition grammar.** A condition is one of: `Base` (`{type:"Base", comparison, lhs, rhs}` — compare
two indicators), `And` / `Or` (`{type, conditions:[...]}`), or `Multi` (`{type:"Multi", value:N,
conditions:[...]}` — true when ≥ N of the nested fire). `comparison` ∈ {lessThan, greaterThan,
lessThanOrEqual, greaterThanOrEqual, equal, notEqual}. Indicators with an empty `targetAsset`
(`{"type":"Stock","symbol":""}`) evaluate **per candidate name** inside pipelines/eligibility; a named
`targetAsset` (e.g. SPY) is a market-level reading.

**Opportunity-regime gate (SPY ≥ 8% off highs)** — the posture-policy regime, as a condition:
```json
{"type":"Base","comparison":"lessThan",
 "lhs":{"type":"Price","targetAsset":{"type":"Stock","symbol":"SPY"}},
 "rhs":{"type":"Multiply","indicators":[
    {"type":"Value","value":0.92},
    {"type":"MaximumPrice","targetAsset":{"type":"Stock","symbol":"SPY"},"window":{"length":252,"interval":"Day"}}]}}
```
Use `0.82` for the extreme/crash leg. Calm regime = the `greaterThanOrEqual` mirror.

**Shared rebalance cadence** (fires on a fresh book; one clock across RebalanceOption strategies):
```json
{"type":"Base","comparison":"greaterThanOrEqual",
 "lhs":{"type":"DaysSinceLastRebalanceOptionOrder"},"rhs":{"type":"Value","value":21}}
```

**Per-name momentum eligibility filter** (Filter stage, evaluated per candidate via empty symbol):
```json
{"type":"Filter","condition":{"type":"Base","comparison":"greaterThan",
 "lhs":{"type":"Price","targetAsset":{"type":"Stock","symbol":""}},
 "rhs":{"type":"SimpleMovingAverage","targetAsset":{"type":"Stock","symbol":""},"window":{"length":150,"interval":"Day"}}}}
```

**Rank → top-K** (concentrate in momentum; keep K > 5 per search constraints):
```json
{"type":"SelectTop","direction":"Highest","limit":12,
 "metric":{"type":"PriceRateOfChange","targetAsset":{"type":"Stock","symbol":""},"window":{"length":126,"interval":"Day"}}}
```

**Exposure-keyed de-risk valve** (trim winners when the book is too hot, only in calm regime):
```json
{"type":"And","conditions":[
  {"type":"Base","comparison":"greaterThan","lhs":{"type":"OptionGrossExposurePercent"},"rhs":{"type":"Value","value":75}},
  <calm-regime Base condition> ]}
```
…paired with a `CloseOption` `{triggers:[{type:"pnl","minPnlPercent":30}]}` action.

**Exit / roll stack** (separate CloseOption strategies, OR-gated triggers within one):
- Take-profit: `{type:"pnl","minPnlPercent":100}` (= +100%). Stop: `{type:"pnl","maxPnlPercent":-50}`.
- DTE roll: `{type:"dte","maxDte":45}`. Days-held: `{type:"daysHeld","maxDaysHeld":N}`.
- Greeks: `{type:"greeks","maxSpreadDelta":...}`.

**Structure ladder (affordability)** — order templates expensive→cheap; the engine fills the FIRST
affordable rung per name, so the costly tail (META/LLY/GS/TSM/ADI/AVGO) lands on the cheapest rung.
Never remove the cheapest rung (see Seed affordability note). Pin leg deltas with `greekFilter`
(`{minDelta, maxDelta}`) and DTE with `expirationSelector`.

**Regime-switched structure** — gate two RebalanceOption sleeves/strategies on calm vs opportunity
regime (different budgets, deltas, DTE) so deployment scales with opportunity while obeying posture.

These are starting shapes, not prescriptions. Compose freely; the gates — not this list — decide
validity. For anything you can't express from these, read the full `create_portfolio` schema.

---

## Deliverable (present at sign-off)

Per-fold table + aggregate row + lockbox row:

| Fold          | Dev window | OOS window                   | OOS return      | OOS maxDD | OOS Sortino     | Names filled /20 | Median deploy | %days >70% (in regime?) | vs A | vs B | vs C | vs SPY |
| ------------- | ---------- | ---------------------------- | --------------- | --------- | --------------- | ---------------- | ------------- | ----------------------- | ---- | ---- | ---- | ------ |
| 1 … N         |            |                              |                 |           |                 |                  |               |                         |      |      |      |        |
| **Aggregate** |            |                              | mean/median/min | worst     | mean / min-fold |                  |               |                         |      |      |      |        |
| **Lockbox**   | (held out) | (run date − 126d) → run date |                 |           |                 | (eligible)       |               |                         |      |      |      |        |

(vs C = vs the frozen Baseline-C incumbent bar, on return AND Sortino — Gate 4.)

Plus: the **per-family certification ledger** (Execution mandate §4) with EVERY study id; the
**Baseline C (incumbent) row** reported separately from the search result; the **posture-matched
Baseline B substitution note** if S1.5 fired (original vs derated B); **`crossFoldRobustSelection`
candidateKey and why chosen** per certified family (vs per-fold winners); full strategy rules;
declared opportunity regime; kill-log with binding-gate attribution; finalist chatPortfolioId;
OOS-robustness summary; per-fold breadth audit; lockbox PASS/FAIL; field-level reproducibility
PASS/FAIL; Gate-8 live parity; any owner override; weekly monitor reports in `<RUN_LOG>`.

**Verdict integrity (state explicitly in the deliverable):** confirm the Execution mandate was
satisfied — number of families certified, number of sweep certifications run, `systematic_sweep`
done, incumbent certified as a seed. A "no deployable winner" deliverable that cannot show ≥ 3
certified families and the full ledger is an INVALID campaign, not a result.

**Headline = OOS aggregate of the assembled, directly-measured book. Never a single-window or
in-sample number.**

## Working rules

- `<RUN_LOG>` at every stage; S0/S1 before design.
- Search with optimize/variants/backtests; certify with walk-forward.
- **Select on cross-fold robustness** (`crossFoldRobustSelection`), not per-fold validation argmax.
- Verify everything that trades real money at FIELD level (`conditionFieldAudit`).
- Measure deploy decisions on the directly-backtested assembled object.
- Lockbox held out from ALL search; touched exactly once at S2.
- Compare certified candidates against Baselines A, B (posture-matched if S1.5 fired), C, and SPY on
  the same calendar.
- **This is a certification campaign: no verdict from the search layer. ZERO optimizing
  certifications = INVALID campaign, not a no-deploy.** (Execution mandate is the controlling rule.)
- **Certify liberally — no token economy.** ≥ 3 mechanism families, up to 3 attempts each, ≥ 3
  gene_intents axes × ≥ 3 values per sweep, plus the incumbent certified as a seed, plus
  `systematic_sweep`. Maintain the certification ledger.
- Honest "no deploy" / "no robust winner" = successful outcome **only after** the full minimum
  certification body is on record (≥ 3 certified families, ledger complete, binding gate isolated
  with study-id evidence). Otherwise it is an incomplete campaign, not an honest no-deploy.
- Measure the incumbent (Baseline C) and report its gate status SEPARATELY from the search result.
- A proposed remedy must not contradict the killed candidate's measured posture/breadth/OOS state.
- One log per run: `<AGENT>_CAMPAIGN_LOG_<UTC-TIMESTAMP>.md`. Never read another run's log or IDs.
- Deploy only after explicit human "deploy" or logged override.
