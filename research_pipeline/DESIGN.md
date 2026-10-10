# Research ledger implementation contract

This is execution and evidence infrastructure for the existing ten checkpoints
in `PERCY_PROJECTS_README.md`. It does not implement or simulate a research model.
This contract was written before the implementation.

The initial admitted study type is a comparative empirical study with a fixed
dataset × proposed/baseline × seed matrix. This is not a universal protocol
engine for proof-only, observational, adaptive, or sequential studies. Existing
theory projects need no fictional datasets or forced migration into this schema.

## Canonical state and history

Each project has one canonical `STATE.md`: a readable current-state projection
and a machine-readable, SHA-256-linked event ledger in the same file. Every
accepted change appends an event. Replaying the events reconstructs the state;
the rendered projection must agree exactly. Contract revisions are permitted
only before freeze and reset the current checkpoint qualifications, preserving
the earlier qualifications and runs in history.

Writes acquire an exclusive operating-system advisory lock, load and verify the
current state, apply an action, then replace the complete file atomically using
a flushed/fsynced sibling staging file, then fsync the containing directory.
Object installation also synchronizes its store and ancestor directories.
Competing writers fail promptly with a
busy error. An optional expected-head value rejects stale updates. Validation
rejections are retained as events when the existing ledger is valid. Corrupted
state, lock contention and storage failures cannot safely guarantee a rejection
record; the command reports the error and does not pretend the update succeeded.

Hash links detect ordinary mutation. A trusted externally retained head digest
is needed to detect a complete valid-history rewrite or rollback. Local advisory
locks do not protect against malicious writers or guarantee network-filesystem
semantics. The usual POSIX durability steps still depend on the filesystem,
mount, device, and hardware. If directory fsync fails after replacement, the new
state is already installed: report that condition and verify before retrying,
rather than claim rollback. Earlier write/replace failures preserve the prior
state. An object installed before a failed admission may remain unreferenced.

## Artifact identity

Artifacts are copied into a content-addressed object store while hashing the
exact copied byte stream. Artifact IDs are immutable. Existing object bytes must
match their name and recorded size before admission. Parents form a chronological
provenance graph. Verification checks every registered object, including failed
and superseded development evidence. Original input files may later change; the
registered snapshot is the retained evidence. This tool never runs a supplied
training, evaluation, analysis or shell command.

## Gates

1. IDEA READY: a recorded reviewer qualification bound to a specification.
2. MODEL SPECIFICATION READY: qualification bound to a specification.
3. METHODOLOGY READY: qualification bound to a protocol artifact.
4. MODEL IMPLEMENTED: qualification bound to a code artifact.
5. EXPERIMENT SYSTEM IMPLEMENTED: qualification bound to code or verification.
6. RUN READY: qualification bound to verification evidence.
7. CONFIRMATORY PROTOCOL FROZEN: immutable protocol, validated exact provenance,
   declared independent units, hypotheses, metric direction/threshold, analysis,
   seeds, complete expected matrix, exclusions, stopping and compute rules, and
   an explicit attestation that protected outcomes remain unobserved.
   Architecture, methodology, and code must be the exact artifacts qualified at
   checkpoints 2, 3, and 4; replacing them requires recorded requalification.
8. EVIDENCE LOCKED: every expected cell retained, valid conclusion classification,
   traceable claims, and a fixed digest of protocol/runs/claims/conclusion.
9. VERIFIED: a named independent review receipt bound to the evidence digest,
   paper, environment and required verification checks.
10. RESEARCH COMPLETE: a release manifest matching the locked disposition/scope,
    independently verified paper and frozen code/config/environment, with the
    remaining release requirements either evidenced or explicitly inapplicable.

Checkpoints 1–6 and 9 record reviewer attestations. A matching file and recorded
attestation do not independently prove novelty, mathematical validity, absence of
leakage or scientific correctness. They make those claims concrete and auditable.

## Run and claim rules

Development and confirmatory runs are distinct. Every run has source commit,
config/data/split/environment identities, independent-unit seed, variant,
runtime, memory, logs, raw artifacts, metrics and failure/deviation fields.
Confirmatory receipts must match the frozen expected cell exactly. Run IDs
cannot be reused, including after failure. Confirmatory metrics are finite and
complete for successful runs. New runs after evidence lock are rejected.

Claim evidence is a checked chain: declared run -> its raw/log artifacts -> an
analysis artifact whose parents include them -> figure/table artifacts with the
analysis as parent. Every named run must contribute at least one source. Supported
claims require successful runs and an actual raw artifact from every run; log-only
failure analysis cannot become a supported scientific claim. Claims are immutable
entries; revisions get new IDs. Invalid
runs never support claims or completion. Failed runs remain available for an
inconclusive/failure analysis; they cannot alone justify a supported/mixed/negative
scientific conclusion.

Conclusion classification is a recorded reviewer judgment; this tool does not
execute the declared statistical decision rule or infer the result from metrics.
A conclusive classification requires at least one supported evidentiary statement,
which can be a supported negative finding. It does not require the proposed
hypothesis to have succeeded.

## Versioned evidence identity correction

New evidence seals include the exact artifact records and admitted run/claim
history, along with contract, study version, freeze, current qualifications and reviewed
conclusion. This closes a v1 gap: reusable artifact labels alone did not bind
their referenced bytes to the review digest. New review receipts separately bind
the paper and frozen release environment SHA-256 identities. Earlier contracts,
notes and rejection events remain bound by the full externally retained ledger
head; the evidence manifest does not claim to replace that complete history.

The original v1 transition semantics remain intact for byte-exact history replay.
Public lock/review/complete actions emit explicitly versioned v2 events. Active
v1 studies can append an explicit `reseal_evidence` event, retaining the previous
seal in the manifest and invalidating only the current qualification of its old
review. They return to gate 8 for a fresh review. No freeze, scientific outcome,
prior receipt or event is replaced. Terminal studies remain immutable. This
correction does not establish reviewer authenticity or scientific correctness.

## Resource accounting

All admitted run receipts, including failures and earlier development versions,
count toward the declared budgets. Compare aggregate runtime using exact rational
values of the recorded JSON numbers; display seconds as decimal strings rounded
to 20 significant digits. Over-budget receipts are retained and overruns are
recorded. An overrun blocks checkpoint qualification and freeze until an explicit
prefreeze contract revision amends the budget. Revisions do not reset spending.
The frozen compute cap must fit the remaining project budget. Frozen caps cannot
be amended after outcomes: an overrun permits only inconclusive or explicit
invalid closure. The CLI records measurements and planning eligibility; it cannot
prevent an external command from running, authenticate a budget authorization,
or recover an unreported run.

## Terminal and successor identity

All four valid terminal outcomes are permitted. An invalid study can be closed
explicitly as INVALID_CLOSED, which is not checkpoint 10. This is also available
after evidence lock or review when a validity defect is discovered; the prior
lock and result remain in history. A completed release remains immutable.
A successor requires
the predecessor's verified current head, finding, remaining problem, materially
different hypothesis, new falsifier and new protocol identity. Creating it never
writes the predecessor.

The separate `correct-invalid` path permits the same question and hypothesis
only for an INVALID_CLOSED predecessor. It records the validity defect, repair,
affected work, rationale and corrected protocol identity in a new project.
Changing scientific scope instead uses the ordinary new-hypothesis successor.
