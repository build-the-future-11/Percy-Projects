# Percy Projects Repository

This repository is the **canonical home of research projects** Percy works on.

It contains two kinds of research units:

1. **Standalone research projects** — one scientific project, with its own complete state, evidence, code, experiments, paper, verification, and release.
2. **Research waves** — groups of multiple individual research projects executed under one shared wave objective. Every individual project inside a wave still follows the complete individual-project research pipeline independently.

The repository exists so that research never becomes scattered across chats, temporary files, or disconnected experiments.

> **If a piece of work is part of a real research project, its durable scientific state belongs here.**

---

# 1. Separation From Percy-Work

There are two Percy repositories.

## Percy-Projects

This repository contains the **canonical scientific projects**.

It owns:

- project state
- hypotheses
- scientific specifications
- code
- experiment protocols
- raw results
- processed results
- figures
- tables
- papers
- claims
- decisions
- failures
- verification
- releases
- wave organization
- final scientific conclusions

## Percy-Work

`Percy-Work` is the execution/operations repository.

It owns:

- incoming tasks
- overnight queues
- cross-project work queues
- blockers
- run logs
- temporary coordination
- work assignments
- handoffs
- links to active projects
- non-canonical drafts or scratch artifacts

**Percy-Work may coordinate research, but Percy-Projects owns the science.**

If research work begins in Percy-Work and becomes a real scientific project, create or locate its canonical project here and link the work item to it.

Do not maintain two conflicting scientific histories.

---

# 2. Ultimate Rule

Every individual research project follows the full research lifecycle:

```text
INITIALIZE
→ ABSTRACT
→ CONCRETE
→ PAPER / SCIENTIFIC SPECIFICATION
→ EXPERIMENTS
→ METHODOLOGY
→ CODING
→ DRY RUN
→ DEVELOPMENT
→ SCIENTIFIC FREEZE
→ CONFIRMATORY RUNS
→ EVIDENCE AUDIT
→ FINISH PAPER
→ INDEPENDENT VERIFICATION
→ RELEASE
→ COMPLETE
```

A project is not complete because a model produced a good metric.

A project is complete when the scientific question has reached a **defensible terminal conclusion** and the relevant evidence, implementation, paper/output, and reproducibility package are complete.

Possible terminal scientific outcomes:

```text
SUPPORTED
MIXED
NEGATIVE
INCONCLUSIVE
```

`INVALID` is a validity state requiring correction or explicit invalid closure.

Percy must never continue changing a frozen experiment merely to force a positive result.

---

# 3. Repository Layout

Recommended structure:

```text
Percy-Projects/
│
├── README.md
├── PROJECT_REGISTRY.md
├── WAVE_REGISTRY.md
│
├── templates/
│   ├── PROJECT_STATE_TEMPLATE.md
│   ├── PROJECT_TASKS_TEMPLATE.md
│   ├── PROJECT_CLAIMS_TEMPLATE.md
│   ├── PROJECT_EXPERIMENTS_TEMPLATE.md
│   ├── PROJECT_DECISIONS_TEMPLATE.md
│   ├── WAVE_STATE_TEMPLATE.md
│   └── WAVE_QUEUE_TEMPLATE.md
│
├── projects/
│   └── <project-slug>/
│       ├── README.md
│       ├── STATE.md
│       ├── TASKS.md
│       ├── DECISIONS.md
│       ├── CLAIMS.md
│       ├── EXPERIMENTS.md
│       ├── research/
│       ├── theory/
│       ├── src/
│       ├── tests/
│       ├── configs/
│       ├── scripts/
│       ├── experiments/
│       ├── results/
│       ├── paper/
│       ├── verification/
│       └── release/
│
└── waves/
    └── <wave-slug>/
        ├── README.md
        ├── WAVE_STATE.md
        ├── WAVE_QUEUE.md
        ├── WAVE_DECISIONS.md
        ├── SHARED_RESOURCES.md
        └── projects/
            ├── <project-a>/
            ├── <project-b>/
            ├── <project-c>/
            └── ...
```

Do not create empty directories merely for appearance. Create structure as it becomes useful.

---

# 4. Project Registry

`PROJECT_REGISTRY.md` is the portfolio-level index of every standalone project and every individual project inside waves.

Each entry should contain:

```text
PROJECT:
SLUG:
TYPE: STANDALONE / WAVE_PROJECT
WAVE:
STATUS:
PHASE:
SCIENTIFIC RESULT:
PRIMARY OBJECTIVE:
CENTRAL HYPOTHESIS:
CURRENT BEST EVIDENCE:
NEXT EXECUTABLE ACTION:
BLOCKERS:
CANONICAL FOLDER:
EXTERNAL REPOSITORY:
LATEST VERIFIED COMMIT:
LAST UPDATED:
```

Allowed project statuses:

```text
QUEUED
ACTIVE
BLOCKED
WAITING_EXTERNAL
NEEDS_REVIEW
VERIFYING
COMPLETE
ARCHIVED
```

Allowed scientific result states:

```text
NOT_YET_TESTED
SUPPORTED
MIXED
NEGATIVE
INCONCLUSIVE
INVALID
```

---

# 5. Wave Registry

`WAVE_REGISTRY.md` is the index of all research waves.

Each wave entry should contain:

```text
WAVE:
SLUG:
OBJECTIVE:
SCOPE:
STATUS:
NUMBER_OF_PROJECTS:
PROJECTS_ACTIVE:
PROJECTS_COMPLETE:
PROJECTS_BLOCKED:
SHARED_RESOURCES:
START_DATE:
TARGET_CLOSE_DATE:
NEXT WAVE ACTION:
LAST UPDATED:
```

Allowed wave statuses:

```text
PLANNED
ACTIVE
BLOCKED
VERIFYING
COMPLETE
ARCHIVED
```

A wave is only `COMPLETE` when every included individual project has a declared disposition:

```text
COMPLETE
ARCHIVED
CANCELLED_WITH_REASON
MOVED_TO_SUCCESSOR
```

No project may silently disappear from a wave.

---

# 6. Individual Project Contract

Every individual project — standalone or inside a wave — must have one canonical `STATE.md`.

Before any new work, Percy reads it.

Before ending any work session, Percy updates it.

Minimum contents:

```text
# Project State

## Identity
Project:
Project slug:
Standalone or wave:
Wave:
Canonical folder:
External repo:

## Research Question

## Scientific Objective

## Current Hypothesis

## Intended Contribution

## Project Scope

## Current Phase

## Project Status

## Current Scientific Result

## Development Budget

## Compute Budget

## Protected Evaluation Boundary

## Datasets

## Repositories

## Important Artifacts

## Current Best Evidence

## Claims Currently Supported

## Claims Not Yet Supported

## Completed Work

## Missing Work

## Known Failures

## Important Decisions

## Blockers

## Next Executable Action

## Definition of Done

## Last Updated
```

Never allow previous negative results, failed experiments, frozen protocols, or important decisions to disappear between iterations.

---

# 7. Project Task State

Every project maintains `TASKS.md`.

Use:

```text
[ ] QUEUED
[>] IN_PROGRESS
[!] BLOCKED
[?] NEEDS_REVIEW
[V] VERIFYING
[x] DONE
[-] CANCELLED
```

Every substantial task should include:

```text
TASK:
PRIORITY:
STATE:
OBJECTIVE:
DEFINITION OF DONE:
DEPENDENCIES:
EXPECTED ARTIFACTS:
VERIFICATION METHOD:
EVIDENCE:
```

A task is never `[x] DONE` simply because Percy attempted it.

---

# 8. Project Lifecycle — Initialize

Before research begins, create the canonical project state.

Define:

- exact research question
- scientific objective
- hypothesis
- intended contribution
- scope
- current phase
- development budget
- compute budget
- protected evaluation boundary
- repositories
- datasets
- artifacts
- claims
- decisions
- failures
- complete known project history

The goal is continuity.

A future Percy run must be able to reconstruct the project without relying on chat memory.

---

# 9. Project Lifecycle — Abstract

Understand the field before building.

Determine:

- fundamental problem
- why the problem matters
- existing approaches
- known limitations
- what existing approaches fundamentally struggle with
- why those failures occur
- possible mechanisms
- strongest underlying principle
- likely assumptions
- likely failure regimes
- falsifying observation
- novelty boundary

Reduce the direction to:

```text
Existing approaches struggle with X under Y.
We propose Z because mechanism M predicts Q.
```

Do not begin major implementation until there is a defensible research contribution.

---

# 10. Project Lifecycle — Concrete

Attack the idea before spending major compute.

Audit:

- novelty
- scientific significance
- mathematical validity
- assumptions
- identifiability
- causality
- computational feasibility
- scaling
- data requirements
- leakage
- confounders
- baseline fairness
- optimization difficulty
- numerical stability
- generalization
- robustness
- complexity
- simpler alternatives
- compute advantage
- parameter advantage
- information advantage
- tuning advantage
- data advantage
- reviewer objections
- failure modes

For each major flaw:

```text
Flaw
→ Cause
→ Severity
→ Possible Solution
→ Required Evidence
```

Checkpoint:

```text
IDEA READY
```

Do not continue unless:

- question is precise
- prior-art boundary is understood
- mechanism is explicit
- contribution is falsifiable
- project has a reason to exist
- major conceptual flaws are addressed
- bounded experimentation can answer the question

---

# 11. Project Lifecycle — Scientific Specification

Write the scientific specification before final results.

Complete:

- introduction
- related work
- problem formulation
- model specification

Define:

- inputs
- outputs
- variables
- units where applicable
- state spaces
- assumptions
- constraints
- objective
- optimization problem
- probabilistic formulation where applicable
- identifiability
- training setting
- inference setting
- evaluation setting

For every model component define:

- purpose
- inputs
- outputs
- dimensions
- parameters
- equations
- transformations
- initialization
- optimization
- interactions
- complexity
- expected behavior
- failure behavior

Also specify:

- forward process
- training process
- inference process
- losses
- regularization
- algorithms
- numerical procedures
- tolerances
- hyperparameters or development-only calibration parameters

Checkpoint:

```text
MODEL SPECIFICATION READY
```

No scientifically important architectural decision should remain implicit.

---

# 12. Project Lifecycle — Experiments

Determine exactly what evidence could support or reject the hypothesis.

Define:

- datasets
- provenance
- licenses
- synthetic generation if applicable
- independent experimental units
- training data
- development data
- validation data
- protected test data
- OOD data
- intervention data where applicable
- distribution shifts
- primary endpoint
- secondary endpoints
- practical effect threshold
- baselines
- mechanism-off controls
- compute-matched controls
- parameter-matched controls where appropriate
- statistics
- uncertainty estimation
- number of independent repetitions
- seed policy
- randomness sources
- failure handling
- stopping conditions
- compute measurement
- memory measurement
- runtime measurement

Explicitly design the strongest reasonable experiment that could falsify the central hypothesis.

---

# 13. Project Lifecycle — Methodology

Build the complete scientific evaluation matrix.

Include where appropriate:

- primary experiment
- strong baselines
- simple baseline
- classical baseline
- state-of-the-art baseline
- mechanism-off control
- compute-matched control
- parameter-matched control
- ablations
- sensitivity analysis
- robustness tests
- OOD/generalization
- scaling tests
- efficiency tests
- failure analysis
- predefined statistical procedure

Separate experimentation into:

```text
DEVELOPMENT
CONFIRMATORY
```

Development results may be used to improve the method.

Protected confirmatory outcomes may not be used to redesign the same frozen hypothesis.

Checkpoint:

```text
METHODOLOGY READY
```

---

# 14. Project Lifecycle — Coding

Implement the paper-specified model.

No:

- pseudocode in place of required executable code
- placeholder scientific mechanisms
- fake implementations
- mock experimental results
- silent failure skipping

Implement as required:

- model
- mathematical operators
- training
- inference
- config
- checkpointing
- numerical safeguards
- deterministic controls
- unit tests
- mathematical tests
- shape tests
- gradient tests
- edge cases
- hand-verifiable sanity cases

Checkpoint:

```text
MODEL IMPLEMENTED
```

Then implement the methodology:

- datasets
- preprocessing
- frozen splits
- baselines
- controls
- evaluation
- metrics
- ablations
- robustness
- OOD tests
- statistics
- compute profiling
- manifests
- logging
- artifact preservation
- failure preservation
- reproduction commands
- figure generation
- table generation

Checkpoint:

```text
EXPERIMENT SYSTEM IMPLEMENTED
```

Every result must be traceable to:

```text
configuration
→ code revision
→ data/split identity
→ environment
→ raw output
→ analysis
```

---

# 15. Project Lifecycle — Engineering Optimization

Improve:

- runtime
- memory
- numerical stability
- parallelism
- batching
- data loading
- checkpointing
- failure recovery
- logging
- reproducibility
- resource efficiency

Engineering-equivalent optimizations are allowed after equivalence testing.

Any change affecting the hypothesis, mechanism, behavior, evaluation, or scientific claim is a scientific change and must be recorded as such.

Never silently change the science while optimizing engineering.

---

# 16. Project Lifecycle — Dry Run

Before expensive execution, verify:

- data integrity
- split integrity
- no leakage
- baselines run
- proposed method runs
- metrics are correct
- artifacts save
- failures remain preserved
- recovery works
- statistics execute
- figures regenerate
- runtime measurement works
- memory measurement works
- full-run cost is estimated
- reproduction commands work

Checkpoint:

```text
RUN READY
```

---

# 17. Project Lifecycle — Development Runs

Execute the authorized development matrix.

Retain every meaningful outcome.

For weaknesses use:

```text
Observation
→ Hypothesized Cause
→ Proposed Change
→ Predicted Consequence
→ Discriminating Experiment
→ Result
```

Audit:

- unexpected failures
- unexpected successes
- baseline behavior
- mechanism behavior
- ablations
- variance
- scaling
- efficiency
- generalization
- confounding explanations

Do not blindly optimize a metric.

Do not search indefinitely for a positive result.

Stay within the declared development budget.

---

# 18. Result Audit and Development Revision

If development reveals weakness, ask:

- what failed?
- what succeeded?
- was the hypothesis wrong?
- was the implementation wrong?
- was the methodology weak?
- did the mechanism behave as predicted?
- does another variable explain the result?
- was the baseline stronger than expected?
- is a scientifically justified modification needed?
- does the evidence imply a genuinely new hypothesis?

If justified, revise the development version and record the change.

If the required change materially alters the hypothesis, mechanism, model, or claim, create a new version or successor project rather than rewriting history.

---

# 19. Scientific Freeze

Before protected confirmatory evaluation, freeze:

- research question
- hypothesis
- code commit
- architecture
- dataset versions
- dataset hashes
- splits
- baselines
- hyperparameters
- metrics
- primary endpoint
- practical effect threshold
- statistical analysis
- seed/repetition policy
- exclusion rules
- stopping rules
- environment
- compute protocol

Checkpoint:

```text
CONFIRMATORY PROTOCOL FROZEN
```

Protected outcomes remain protected until this point.

---

# 20. Confirmatory Runs

Run the frozen methodology without adapting it to protected outcomes.

Retain:

- every successful run
- every failed run
- every seed
- every configuration
- raw outputs
- logs
- checkpoints
- runtime
- memory
- compute
- deviations
- unexpected observations

Classify the scientific result:

```text
SUPPORTED
MIXED
NEGATIVE
INCONCLUSIVE
INVALID
```

---

# 21. Supported Results

If supported:

- verify
- attempt to break the result
- run predefined robustness work
- reproduce major findings where practical
- check compute advantage
- check parameter advantage
- check information advantage
- check leakage
- check baseline weakness
- check tuning asymmetry
- check statistical artifacts
- check aggregation
- check lucky initialization

Then proceed to final paper completion.

---

# 22. Mixed Results

Determine:

- where the method works
- where it fails
- why
- whether claims need narrowing
- whether a new mechanism is suggested

Preserve the original result.

A post-hoc subgroup finding does not become the original confirmatory hypothesis.

A genuinely new hypothesis becomes a separately versioned successor project.

---

# 23. Negative Results

First verify experimental validity.

If valid:

- accept the negative result
- explain why the mechanism failed
- identify which assumptions failed
- document tested regimes
- state what evidence rules out
- state what remains unresolved
- determine whether the negative finding is scientifically informative

Do not rerun the frozen experiment merely to obtain a positive result.

---

# 24. Inconclusive Results

Determine why:

- high variance
- insufficient independent units
- weak measurement
- insufficient precision
- inadequate compute
- unstable optimization
- poor identifiability
- experimental limitations

Only authorize more evidence if it can realistically resolve the uncertainty.

Otherwise close as inconclusive.

---

# 25. Invalid Results

Identify the exact validity failure.

Examples:

- bug
- leakage
- incorrect metric
- broken baseline
- incorrect split
- corrupted dataset
- mathematical implementation error
- invalid statistical procedure

Then:

1. preserve the invalid evidence
2. document the defect
3. fix it
4. freeze the corrected protocol
5. rerun only scientifically affected work

Never erase invalid-run history.

---

# 26. Evidence Audit

Before final paper completion, construct:

```text
Claim
→ Experiment
→ Raw Artifact
→ Analysis
→ Figure/Table
```

For every claim ask:

- directly supported?
- evidence valid?
- uncertainty represented?
- scope correct?
- simpler explanation?
- wording stronger than evidence?

Audit:

- equations
- citations
- tables
- figures
- statistics
- numerical values
- conclusions

Remove or weaken unsupported claims.

Checkpoint:

```text
EVIDENCE LOCKED
```

---

# 27. Claims Ledger

Every project maintains `CLAIMS.md`.

Use:

```text
## Claim

STATUS:
SUPPORTED / PARTIALLY_SUPPORTED / UNSUPPORTED / REJECTED

SCOPE:

EVIDENCE:
- experiment
- raw artifact
- analysis
- figure/table

LIMITATIONS:

PAPER LOCATION:
```

No important scientific claim should exist without traceable evidence.

---

# 28. Experiment Ledger

Every project maintains `EXPERIMENTS.md`.

Recommended entry:

```text
## Experiment <ID>

DATE:
TYPE: DEVELOPMENT / CONFIRMATORY
OBJECTIVE:
HYPOTHESIS:
CODE COMMIT:
CONFIG:
DATASET:
SPLIT:
SEEDS:
COMPUTE:
PRIMARY METRIC:
SECONDARY METRICS:
RESULT:
UNCERTAINTY:
STATUS:
RAW ARTIFACTS:
PROCESSED ARTIFACTS:
FIGURES:
INTERPRETATION:
LIMITATIONS:
FOLLOW-UP:
```

Failed experiments stay in the ledger.

---

# 29. Decisions Ledger

Use `DECISIONS.md`.

Recommended entry:

```text
## Decision — <date>

DECISION:
WHY:
ALTERNATIVES:
EVIDENCE:
CONSEQUENCES:
WHAT WOULD JUSTIFY REVERSAL:
```

Do not silently reverse important scientific decisions.

---

# 30. Finish the Paper

Complete where applicable:

- abstract
- introduction
- related work
- problem formulation
- method
- algorithms
- methodology
- experimental setup
- results
- ablations
- robustness
- OOD/generalization
- efficiency
- statistical analysis
- failure analysis
- discussion
- limitations
- conclusion
- reproducibility statement
- appendices

Generate from verified evidence:

- heatmaps
- architecture diagrams
- flowcharts
- scientific diagrams
- performance graphs
- scaling plots
- ablation plots
- robustness plots
- tables
- statistical summaries

Every important number must trace back to retained evidence.

---

# 31. Independent Verification

Use a clean or independent review pass.

Verify:

- repository builds
- tests pass
- major experiments reproduce where practical
- raw results regenerate analysis
- figures regenerate
- tables regenerate
- paper numbers match artifacts
- mathematical derivations are checked
- citations support statements
- no unsupported claims remain

The verifier should try to find errors, not merely approve completion.

Checkpoint:

```text
VERIFIED
```

---

# 32. Release

Prepare as applicable:

- final source
- final PDF
- figures
- tables
- bibliography
- supplement
- code
- configs
- environment
- dataset instructions
- reproduction instructions
- raw evidence where distributable
- artifact hashes
- authorship
- licensing
- ethics requirements
- venue requirements
- arXiv package
- submission package

Freeze the final release commit/version.

Record:

```text
FINAL DISPOSITION:
EXACT CLAIM SCOPE:
RELEASE COMMIT:
RELEASE ARTIFACTS:
```

Checkpoint:

```text
RESEARCH COMPLETE
```

---

# 33. Research Waves

A wave is **not one giant project**.

A wave is a coordinated container of multiple individual research projects.

Every project in a wave follows the full individual project pipeline above.

Example:

```text
waves/
└── research-wave-4/
    ├── WAVE_STATE.md
    ├── WAVE_QUEUE.md
    ├── WAVE_DECISIONS.md
    ├── SHARED_RESOURCES.md
    └── projects/
        ├── project-001/
        │   ├── STATE.md
        │   ├── TASKS.md
        │   ├── CLAIMS.md
        │   ├── EXPERIMENTS.md
        │   └── ...
        ├── project-002/
        └── project-003/
```

The wave may coordinate:

- shared theme
- shared datasets
- shared infrastructure
- shared compute
- shared literature review
- shared deadlines
- shared implementation components
- common benchmarks
- common release targets

But shared infrastructure must never replace project-specific scientific records.

---

# 34. Wave State

Every wave maintains `WAVE_STATE.md`.

Minimum contents:

```text
# Wave State

## Wave Objective

## Scientific Theme

## Scope

## Inclusion Criteria

## Project List

## Shared Resources

## Shared Datasets

## Shared Infrastructure

## Shared Compute Budget

## Wave-Level Deadlines

## Active Projects

## Complete Projects

## Blocked Projects

## Cancelled Projects and Reasons

## Cross-Project Findings

## Shared Risks

## Next Wave-Level Action

## Wave Definition of Done

## Last Updated
```

---

# 35. Wave Queue

`WAVE_QUEUE.md` tracks execution across the projects.

Recommended columns:

```text
PRIORITY
PROJECT
PHASE
STATUS
NEXT ACTION
BLOCKER
OWNER
LAST UPDATED
```

Percy should use this queue to decide which individual project to advance next.

Do not confuse wave priority with scientific validity.

---

# 36. Wave Execution Strategy

When Ryan says:

```text
Work on Wave <X>.
```

Percy should:

1. read `WAVE_STATE.md`
2. read `WAVE_QUEUE.md`
3. inspect every project state
4. identify invalid/broken work first
5. identify projects near completion
6. identify experiments ready to execute
7. identify shared blockers
8. execute project work
9. preserve project-specific evidence
10. update each touched project
11. update wave state
12. continue to the next executable project

Maximum default:

```text
3 substantial projects actively in progress at once
```

unless genuine parallel execution makes more sense.

---

# 37. Shared Wave Findings

Cross-project analysis is allowed, but it must not erase project boundaries.

If a pattern emerges across several projects, record:

```text
OBSERVATION:
PROJECTS INVOLVED:
EVIDENCE:
COMMON MECHANISM HYPOTHESIS:
ALTERNATIVE EXPLANATIONS:
FOLLOW-UP:
```

If the cross-project pattern becomes a new scientific hypothesis, create a successor project rather than retroactively modifying previous confirmatory claims.

---

# 38. Wave Completion

A wave is finished when:

- every included project has a disposition
- no project has unexplained missing state
- important failures are preserved
- cross-project findings are documented
- shared artifacts are organized
- project registries are updated
- successor research is separated from completed work

Wave completion does not require every project to be positive.

A wave containing negative or inconclusive projects may still be a successfully completed research wave.

---

# 39. Successor Projects

New observations do not reopen completed research automatically.

A successor project requires:

```text
Previous Finding
→ Remaining Problem
→ New Hypothesis
→ Material Scientific Difference
→ New Falsifier
→ New Protocol
→ New Project Version
```

Preserve the completed predecessor exactly as it was.

---

# 40. External Canonical Repositories

Some projects may already have their own GitHub repositories.

If so:

1. record the external repo in `STATE.md`
2. treat the proper code repository as canonical for implementation if appropriate
3. record commit SHAs here
4. store scientific state, evidence mapping, coordination, and release metadata here
5. do not create contradictory copies
6. if Ryan explicitly wants a mirror, document the relationship clearly

A project must always be understandable from its Percy-Projects state even when code lives elsewhere.

---

# 41. Artifact Rules

Preserve:

- raw results
- processed results
- logs
- manifests
- configs
- figures
- tables
- papers
- verification reports

Do not carelessly commit:

- enormous datasets
- unnecessary caches
- temporary binaries
- huge checkpoints

Use:

- reproducible generation/download scripts
- hashes
- manifests
- Git LFS where intentionally configured
- canonical external storage references

Never lose provenance.

---

# 42. Percy Behavior in This Repository

When Ryan says:

```text
Start a research project.
```

Percy should create the canonical project state here and begin the research pipeline.

When Ryan says:

```text
Finish <project>.
```

Percy should inspect the existing project and attempt to move it toward a verified terminal conclusion rather than merely describing next steps.

When Ryan says:

```text
Run <wave>.
```

Percy should advance the individual projects in the wave, each under its own project contract.

When Ryan says:

```text
Finish all research.
```

Percy should use the registries and queues, prioritize existing active projects, clear invalid/broken work, push near-complete projects toward closure, and continue across the portfolio without inventing positive findings.

---

# 43. Things Percy Must Never Do

Never:

- fabricate experiments
- fabricate results
- fabricate citations
- fabricate successful runs
- fabricate project completion
- hide negative evidence
- delete failed runs because they are inconvenient
- silently alter frozen confirmatory protocols
- tune indefinitely until a result becomes positive
- merge separate projects merely because they share a theme
- treat a wave-level result as proof for every project
- leave important research state only in chat
- mark work complete without evidence
- rewrite completed history to fit a successor hypothesis

---

# Final Rule

**Standalone projects follow the full individual research pipeline.**

**Wave projects follow the exact same pipeline individually, grouped inside a shared wave container.**

The wave coordinates the work.

The project owns the science.

The evidence decides the result.
