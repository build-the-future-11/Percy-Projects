# Durable research lifecycle and evidence CLI

This working, standard-library-only Python tool implements the state and evidence
mechanics of [the project pipeline](../PERCY_PROJECTS_README.md). It stores one
canonical `STATE.md` per study, retains artifact snapshots and failed receipts,
checks scientific state transitions, binds confirmation to frozen provenance, and
can finish an adverse study without relabeling it a success.

It **records and verifies evidence identities and reviewer attestations**. It
does not run training, compute statistics, establish novelty, authenticate a
reviewer, prove a claim, protect a dataset from access, or turn a software gate
into scientific validation. The scientific question remains the researcher's
responsibility. Read [DESIGN.md](DESIGN.md) for the implementation contract.

## Supported study shape

The current freeze schema admits comparative empirical studies with a fixed
`datasets × (proposed + baselines) × seeds` matrix, one successful or failed
execution receipt per declared cell, and one primary endpoint. A seed is an
identifier for a declared repetition; its presence does not establish independent
experimental units. Those units and the aggregation must be justified in the
protocol and independent review.

Proof-only, observational, adaptive, sequential, and unequal-cell studies are
outside this initial schema. Existing theory projects and their artifacts remain
untouched. Do not invent datasets, successful runs, or reviewer receipts to make
a real project fit these gates. An incomplete fixed matrix remains incomplete.

## Run immediately

Requirements: Python 3.11 or later on a local POSIX filesystem supporting `flock`,
atomic rename, directory `fsync`, and `O_NOFOLLOW` (tested locally on Linux with
Python 3.12). There are no third-party runtime or test dependencies.

From the repository root:

```sh
python -m research_pipeline --help
python -m unittest discover -s tests -v
python -m research_pipeline.demo --output /tmp/artificial-research-ledger-demo
python -m research_pipeline verify /tmp/artificial-research-ledger-demo/study
python -m research_pipeline state /tmp/artificial-research-ledger-demo/study
```

The demo requires a new output directory and refuses to overwrite an existing
one. It generates complete JSON inputs, snapshot objects, and a `STATE.md` that
passes all ten software gates with an artificial negative classification.
**Its scores, commit identifiers, reviews, and receipts are fictional software
fixtures. No research is executed, verified, published, or completed by the demo.**

The real CLI never executes any string stored as a reproduction command, model
configuration, analysis procedure, or artifact. There is no subprocess runner.

## Session workflow

At the start of a research session, run `state` and read the canonical state,
previous failures, protocol boundary, budgets, and next action. Before finishing,
record new artifacts, receipts, decisions, and any justified prefreeze revision.
Run `verify` and retain its head digest with the code revision or another trusted
external record. This is what makes a later valid-history rollback detectable.

Project commands accept a project directory; `verify-bundle` accepts a bundle
file. JSON commands read a UTF-8 file using strict parsing: duplicate keys, NaN,
infinity, and schema mismatches are errors.
Commands emit JSON to stdout; errors go to stderr with exit status 2. Success is
exit status 0. Most updates accept `--expected-head HASH` to reject a stale writer.

| Command | Purpose / required additional arguments |
| --- | --- |
| `init` | Create a new project: `--contract contract.json` |
| `state` | Verify and return the current state and budget accounting |
| `verify` | Verify history, exact projection, and every registered artifact |
| `history` | Return the complete hash-linked event history from one snapshot |
| `export` | Write a deterministic self-contained snapshot: `--output NEW_BUNDLE.zip` |
| `verify-bundle` | Verify one bundle file offline; no project directory or artifact execution |
| `artifact` | Snapshot a file: `--id ID --kind KIND --file PATH [--parents ID ...]` |
| `checkpoint` | Qualify gate 1–6: `--number N --evidence ID --reviewer NAME --note TEXT` |
| `freeze` | Gate 7: `--artifact PROTOCOL_ID` |
| `run` | Admit an existing runner receipt: `--json run.json` |
| `claim` | Add a traceable scientific statement: `--json claim.json` |
| `note` | Retain an observation and discriminating development experiment: `--json note.json` |
| `revise` | Before freeze, record a new full contract and reason: `--json revision.json` |
| `lock-evidence` | Gate 8, reviewed classification: `--json conclusion.json` |
| `reseal-evidence` | Explicitly bind an active v1 seal to artifact bytes and require renewed review: `--json reason.json` |
| `verify-review` | Gate 9: `--artifact VERIFICATION_RECEIPT_ID` |
| `complete` | Gate 10: `--artifact RELEASE_MANIFEST_ID` |
| `close-invalid` | Explicit invalid closure: `--json invalid-closure.json` |
| `successor` | New hypothesis after a terminal predecessor: `--target DIR --contract FILE --relationship FILE --protocol FILE` |
| `correct-invalid` | Same hypothesis after an invalid predecessor, with the same four arguments |

Initialize an actual study only after its contract is concrete:

```sh
python -m research_pipeline init projects/my-study --contract contract.json
python -m research_pipeline artifact projects/my-study --id model-spec-v1 --kind specification --file model-specification.md
python -m research_pipeline checkpoint projects/my-study --number 1 --evidence model-spec-v1 --reviewer 'Researcher name' --note 'Question, novelty boundary, mechanism, falsifier, and bounded test reviewed.'
```

The files in the demo's `inputs/` directory are complete examples of every major
JSON receipt. They are useful for learning the schema; they are not evidence to
reuse in a real project.

## Portable evidence bundles

Export packages the canonical state and every registered object into one
deterministic archive. It supports incomplete ACTIVE histories, completed
histories of any recorded disposition, and explicit invalid closures. It records
the existing checkpoint and scientific result; exporting does not append an
event, qualify a checkpoint, or mark the project complete.

```sh
python -m research_pipeline export projects/my-study --output evidence-snapshot.zip
python -m research_pipeline verify-bundle evidence-snapshot.zip
```

The output path must be new. The destination's parent directory must already
exist. An existing file or symlink is never overwritten, including one created
by another writer immediately before installation. Both commands accept
`--expected-head HASH`, using a full lowercase SHA-256 previously retained in a
trusted external record. An unanchored verification reports
`trusted_head_checked: false`; a valid older bundle may pass in that mode.

The exporter holds the project lock, verifies the existing history, and renders
`STATE.md` from that verified snapshot. It retains the complete artifact records
and deduplicates objects by SHA-256. Each object is streamed through a regular
no-follow descriptor, checking the exact bytes copied into the archive. Repeated
exports of the same snapshot are byte-identical: no export time, source pathname,
filesystem timestamp, or process umask enters the ZIP.

The verifier copies the input once into private temporary storage while hashing
and enforcing the source byte cap. Replacing the original input path afterward
cannot change this verification. It admits only the fixed version-1 ZIP layout,
checks exact member names, regular-file metadata, local/central headers, CRCs,
sizes and digests, then reconstructs the project under computed private paths.
It replays the unchanged ledger and requires the archived state bytes and the
entire manifest to match their canonical reconstruction. It never extracts
arbitrary paths, installs a persistent project, or executes an artifact or
reproduction command.

Success receipts include `bundle_sha256`, `bundle_bytes`, `project_id`, `head`,
event/artifact/object counts, `recorded_state` (status, checkpoint, scientific
result and evidence seal version), and `trusted_head_checked`. Export additionally
reports its destination and installation. `valid: true` means internal bundle
and ledger integrity passed. It does not authenticate reviewer names, establish
scientific validity, or establish that an unanchored history is the newest one.

| Limit | Default / rule |
| --- | --- |
| Source/output ZIP and aggregate member bytes | 512 MiB; `--max-bytes` |
| Individual object bytes | 512 MiB; `--max-object-bytes` |
| Number of ZIP members, including state and manifest | 10,000; `--max-members` |
| Canonical `STATE.md` | Fixed 16 MiB |
| Canonical `manifest.json` | Fixed 8 MiB |
| Format | Fixed UNIX regular mode 0600, 1980 timestamp, ZIP_STORED; ZIP32 only, below the standard library's 2 GiB ZIP64 threshold |

Limits must be exact positive integers in the Python API; booleans, floats and
coercible strings are refused. They can be adjusted within the format's
structural limits. Byte and member bounds constrain storage and parsing; they
do not provide a CPU-time limit for general ledger replay. This version rejects
compressed, encrypted, ZIP64, commented or repacked noncanonical archives, even
if a general ZIP utility would accept them. The standard writer can require
ZIP64 slightly before its nominal threshold for a large individual member;
export reports that as a format-limit refusal and publishes no partial file.

Installation uses a flushed/fsynced sibling staging file, a no-overwrite atomic
hard link and parent-directory fsync. If directory fsync fails after linking,
the command reports that the bundle **was installed**. Verify that installed file
before retrying; a subsequent export to the same name will refuse the collision.
Earlier write or link failures publish no partial bundle and clean the owned
staging file. These are local POSIX integrity and durability measures, subject to
the filesystem and the existing cooperating-writer boundary.

The Python entry points are `research_pipeline.archive.export_bundle(project,
destination, ...)` and `verify_bundle(source, ...)`. Their keyword limits use the
CLI names with underscores. See [ARCHIVE_DESIGN_20261010.md](ARCHIVE_DESIGN_20261010.md)
for the pre-code contract and [ARCHIVE_DEVELOPMENT_20261010.md](ARCHIVE_DEVELOPMENT_20261010.md)
for executed tests, retained failures and independent review.

## Exact input contracts

Unknown and missing top-level fields are rejected. Artifact references are
previously registered immutable IDs, rather than live paths.

### Initialization and revision

A contract contains exactly:

`project_id`, `title`, `owner`, `question`, `objective`, `hypothesis`,
`contribution`, `scope`, `development_budget`, `compute_budget`,
`protected_boundary`, `repositories`, `datasets`, `known_history`,
`definition_of_done`, `next_action`.

Text fields must be nonempty; `project_id` is a lowercase alphanumeric, hyphen,
or underscore slug. `repositories` is a nonempty list of unique strings.
`datasets` and `known_history` are unique string lists and may be empty before
methodology is selected. Budgets are `{ "max_runs": integer }` and
`{ "seconds": number, "description": "measurement meaning" }`, respectively.
Their numeric limits are finite and nonnegative. Seconds mean the sum of admitted
run runtimes, including parallel workers' individual recorded durations; choose
and document the same measurement convention throughout the study.

A revision is `{ "contract": <complete contract>, "reason": "..." }`.
It increments the development version and resets current qualifications to zero.
Earlier contracts, qualifications, artifacts, claims, spending, and outcomes
remain in history. Artifact, run, and claim IDs cannot be reused. Current claim
headings show only the current version, label the scientific phase, and retain a
separate history of all claims.

A note has exactly `observation`, `cause`, `change`, `prediction`, `experiment`,
and `result`, each nonempty text. A note documents a proposed or completed change;
it does not itself modify the contract or grant authority to change a freeze.

### Artifacts

Kinds: `specification`, `protocol`, `code`, `config`, `dataset`, `split`,
`environment`, `raw`, `log`, `analysis`, `figure`, `table`, `paper`,
`verification`, `release`, `other`.

The CLI copies nonempty regular-file bytes into the content-addressed store and
records their SHA-256, size, source basename, ID, kind, and parent IDs. Parents
must already exist, so the provenance graph cannot contain a cycle. A dataset
artifact can be an actual data archive or an explicitly identified immutable
dataset manifest. Hashing a manifest verifies that manifest's bytes; it does not
verify an external dataset's contents. Keep the actual data verification evidence
and licenses in the methodology.

After freeze, new scientific input objects (`code`, `config`, `dataset`, `split`,
`environment`, `specification`, `protocol`) are rejected. Raw outputs, logs,
analysis, displays, papers, review, and release objects may still be registered.
No object from earlier development is deleted or overwritten by this tool.

### Freeze and qualification

Gate evidence kinds are: 1–2 `specification`; 3 `protocol`; 4 `code`; 5 `code`
or `verification`; 6 `verification`. All six require a named reviewer and a
nonempty qualification note. Gate 7 requires the exact protocol qualified at
gate 3, the exact model specification qualified at gate 2, and the exact code
artifact qualified at gate 4. Replacing a scientific input requires a recorded
prefreeze revision and requalification.

The protocol contains exactly:

`version`, `question`, `hypothesis`, `code`, `architecture_artifact`, `datasets`,
`baselines`, `hyperparameters`, `metrics`, `primary_endpoint`, `direction`,
`practical_effect_threshold`, `statistics`, `seeds`, `independent_unit`,
`exclusion_rules`, `stopping_rules`, `environment_artifact`, `compute_protocol`,
`expected_runs`, `protected_boundary`, `protected_outcomes_unobserved`.

`question`, `hypothesis`, and `protected_boundary` must match the current contract.
`protected_outcomes_unobserved` must be the boolean `true`, an attestation rather
than a secrecy guarantee. Nested fields are:

- `code`: `repository`, full 40-character lowercase hexadecimal `commit`, and
  `artifact` of kind `code`; repository must be in the contract.
- Each `datasets` entry: unique `id`, `version`, `license`, `artifact` of kind
  `dataset`, and `split_artifact` of kind `split`.
- `baselines`: nonempty unique names; `proposed` is reserved for the tested arm.
- `hyperparameters`: an explicit object, including `{}` when justified.
- `metrics`: nonempty unique names; `primary_endpoint` must be one of them.
  `direction` is `lower` or `higher`; effect threshold is finite and nonnegative.
- `statistics`: nonempty `procedure`, `uncertainty`, `aggregation`, `multiplicity`,
  and `decision_rule`. These descriptions are preserved, not executed.
- `seeds`: nonempty unique nonnegative integers.
- `compute_protocol`: nonempty `hardware`, positive `max_seconds`, and nonempty
  `measurement`; the cap must fit the remaining project runtime budget.
- Each `expected_runs` entry: unique `run_id`, `seed`, `variant`, `dataset_id`,
  and `config_artifact` of kind `config`. Every declared matrix cell must occur
  exactly once. Neither duplicate cells nor reused run IDs are admitted.

Other specification fields are nonempty text or references to artifacts of the
matching kind. Every registered object is verified during state loading.

### Existing runner receipts

A run contains exactly:

`run_id`, `phase`, `status`, `source_commit`, `config_artifact`,
`dataset_artifact`, `split_artifact`, `environment_artifact`, `seed`, `variant`,
`runtime_seconds`, `peak_memory_bytes`, `compute`, `metrics`, `raw_artifacts`,
`log_artifacts`, `failure_reason`, `deviations`, `protocol_hash`.

`phase` is `DEVELOPMENT` or `CONFIRMATORY`. `status` is `SUCCESS`, `FAILED`, or
`INVALID`. Source commits are full 40-character lowercase hexadecimal strings;
the caller must verify that the measured runner actually used that revision.
Runtime and peak memory are finite/nonnegative; memory and seed are integers.
`compute` is a nonempty JSON object describing resource measurements. Successful
runs require finite metrics, nonempty raw evidence, nonempty logs, and null
`failure_reason`. Failed/invalid runs require a reason and logs, and may have no
raw outputs. `deviations` is a list of unique nonempty strings, possibly empty.

Development receipts require null `protocol_hash` and cannot be admitted after
freeze. Confirmatory receipts require the frozen protocol SHA-256 and exact
expected run ID, code, config, data, split, environment, seed, and variant.
Successful confirmatory metric names must match the declared metrics exactly.
A missing or extra run blocks the evidence lock. Failed IDs remain used forever;
a different execution needs an explicitly planned ID and protocol.

The receipt does not prove its measurements or recover omitted work. Register
the actual existing runner's raw outputs and failure logs before admitting it.

### Budgets

Every retained development receipt counts toward `max_runs`, including failures
and previous development versions. All retained run runtimes count toward the
project seconds limit; confirmatory runtimes also count toward the immutable
frozen cap. Comparisons use exact rational representations of the admitted JSON
numbers. Projection seconds are decimal strings with 20 significant digits, so
large totals remain serializable without silently becoming infinity.

Over-budget receipts are **retained**. The state records the overrun and exposes
used, remaining, blocked, and development planning eligibility. An overrun blocks
qualification and freeze until a recorded prefreeze contract revision explicitly
amends the budget; spending and the original overrun remain visible. Reaching a
limit exactly is not an overrun, but has no remaining allowance. After freeze,
the caps cannot change: an overrun restricts closure to `INCONCLUSIVE` or explicit
`INVALID_CLOSED`. This does not stop external commands or authorize more spending.

### Claims and reviewed conclusion

A claim contains exactly:

`claim_id`, `text`, `scope`, `status`, `limitations`, `uncertainty`,
`paper_location`, `phase`, `run_ids`, `raw_artifacts`, `analysis_artifact`,
`display_artifacts`.

Status is `SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNSUPPORTED`, or `REJECTED`.
Every named run must contribute at least one selected raw/log artifact. Supported
claims require successful evidence and an actual raw artifact from **each** run.
Runs must share the claim's phase; invalid runs are inadmissible. The analysis
must list all selected sources as parents, and each figure/table must list that
analysis as a parent. Text, scope, limitations, uncertainty, and paper location
are mandatory. Failed runs can support a traceable failure analysis with an
unsupported/rejected claim, without implying a scientific negative finding.

A conclusion contains `disposition`, `scope`, and `reason`. Valid dispositions
are `SUPPORTED`, `MIXED`, `NEGATIVE`, and `INCONCLUSIVE`. Gate 8 requires the full
fixed matrix, no invalid run, and a confirmatory claim. Conclusive dispositions
also require successful evidence and a supported/partially supported evidentiary
statement. A supported statement can describe a negative finding; it does not
need to endorse the hypothesis. Classification is a **reviewer judgment**, not
an automatic calculation from metric direction or score. New runs or claims after
locking require another study.

New evidence locks use seal version 2. Their immutable `manifest` binds the
contract and study version, frozen protocol, all registered artifact records
(including SHA-256, byte count, kind and provenance parents), all admitted runs
and claims with their development versions, current qualifications, predecessor
identity, and conclusion. Earlier contract revisions, notes and rejection events
remain in the full ledger, whose externally retained head binds that history.
Thus changing retained code, data, logs, raw outcomes, analyses or displays cannot
reuse an existing evidence digest just by retaining the same artifact IDs.
Earlier admitted development and failed-run evidence is included. Later paper,
review, and release registration does not change the sealed manifest.

#### Existing version 1 histories

Version 1 event semantics remain available for exact historical replay; reading
an old study does not rewrite its state or digest. `verify` reports
`evidence_seal_version` (`null` before locking, otherwise 1 or 2). Its `valid`
field concerns ledger/object integrity, not scientific validity or the strength
of an old seal. A v1 seal binds receipt labels, not every referenced object's
bytes, so retain the externally trusted full ledger head when assessing old work.

New review or release actions on an active v1 study require an explicit
`reseal-evidence` receipt with exactly `{ "reason": "..." }`. This appends an
event, includes the previous seal in the new manifest, preserves all earlier
events, artifacts, outcomes, and the frozen protocol, and returns to gate 8.
The prior review remains in history and its artifact remains registered; a new
review must attest the new digest. Resealing does not authorize another run,
change the conclusion, or alter the freeze. A completed or invalid-closed study
remains immutable and cannot be resealed. A version 2 seal cannot be repeatedly
resealed to reset review.

### Independent verification and release

A new verification artifact is JSON with exactly `reviewer`, `evidence_sha256`,
`paper_artifact`, `paper_sha256`, `environment_artifact`, `environment_sha256`,
`checks`, `reproduction_command`, and `limits`. The reviewer must supply the full
lowercase SHA-256 identities of the actual paper and environment artifacts they
reviewed. These must match retained bytes; the CLI does not invent these
attestations. The reviewed environment must be the frozen environment that will
be released. Its reviewer name must differ from the contract owner, and its
evidence digest must match the version 2 seal at gate 8. Checks are exactly `build`, `tests`, `reproduction`,
`figures`, `tables`, `paper_numbers`, `mathematics`, `citations`, and `claim_scope`,
all boolean true. If a check cannot be substantiated, do not invent a passing
receipt. Explain practical reproduction limits in `limits`.

The release artifact is JSON with exactly `release_commit`, `disposition`,
`scope`, `evidence_sha256`, `roles`, and `reviews`. Its disposition/scope/digest
must preserve the locked conclusion. `roles` contains the independently verified
`paper`, frozen `code`, every frozen `configuration` in a list, frozen
`environment`, and `reproduction` / `data_instructions` artifacts of kind `other`.

`reviews` contains exactly `bibliography`, `supplement`, `authorship`, `licensing`,
`ethics`, `venue`, `arxiv`, and `submission`. Each is either
`{ "artifact_id": "registered evidence" }` or
`{ "not_applicable": "specific reason" }`. Treat applicability as a reviewed
scientific/release decision. The ledger does not upload or submit anything.

### Invalid closure and successor studies

`close-invalid` takes `{ "reason": "documented defect", "report_artifact": "ID" }`;
the report must be an analysis or verification artifact. It is available for any
active study, including after evidence lock or independent review. It preserves
the earlier lock and all results, records `INVALID_CLOSED`, and never awards gate
10. Completed releases are immutable.

An ordinary successor uses a new project ID and different hypothesis. Its
relationship has exactly `previous_finding`, `remaining_problem`,
`new_hypothesis`, `material_difference`, and `new_falsifier`, all nonempty.

`correct-invalid` is a separate path only for an `INVALID_CLOSED` predecessor. It
preserves the scientific question/hypothesis, creates a new project ID, and takes
`previous_finding`, `validity_defect`, `repair`, `affected_work`, and `justification`.
Its corrected protocol must have a different hash from the invalid frozen
protocol. The retained predecessor is never rewritten. The corrected study still
starts at initialization, qualifies all gates, and freezes its corrected exact
protocol. New protected data may be required scientifically; this tool cannot
restore secrecy once outcomes were seen. The reviewer must resolve that boundary.

Both successor paths snapshot the declared new protocol and bind its identity to
the predecessor's verified head. That same protocol must eventually be frozen.

## Durability, errors, and recovery

`STATE.md` combines a generated readable projection and a hash-linked event
ledger. Every load replays the history, checks sequence/hash links, verifies all
registered object bytes, and requires the exact regenerated projection. Manual
edits, changed or missing objects, and symlink substitutions are rejected.
Keep the complete project directory, including its object store, in durable
versioned storage appropriate to the artifact licenses and sensitivity.

Cooperating writers use one persistent `flock` inode. Busy writers fail promptly;
stale expected-head attempts are retained as rejections without applying their
scientific update. Mutations append events, fsync a sibling staging file, replace
state atomically, and fsync its directory. Object installation synchronizes its
store and ancestor directories. These are ordinary POSIX durability measures,
not a guarantee against storage hardware failures or hostile writers.

Validation failures on valid active state are retained as rejected attempts.
Corrupt state, lock contention, terminal immutability, and storage errors cannot
always receive such a record. Before-replacement write failures keep the previous
state; a directory-fsync error **after** replacement reports that the new state
was already installed. Verify the current head before retrying. An artifact copy
installed before a failed ledger write can be an unreferenced object; it never
replaces earlier evidence. The tool intentionally provides no automatic deletion.

A complete self-consistent history rewrite or rollback requires an externally
trusted head or version-control history to detect. Stored code IDs and reviewer
names are provenance declarations, not authentication. Full object verification
on every load favors auditability over throughput; benchmark large archives
before adopting this mechanism for a large evidence store.
