# Evidence bundle engineering record — 2026-10-10

## Delivery and scientific boundary

This pass adds real deterministic archive export and bounded offline verification
to the existing lifecycle CLI. The tested source base is PR #6 commit
`eb3d36109e93a32ec2bd1454899cd106d029da4b`, tree
`e34cc899f85db95e21720051a99c5b688fa4ab57`. Its verified JSON-snapshot fix,
byte-bound v2 evidence seals, v1 replay compatibility, original source and prior
engineering records are retained. `ledger.py` is unchanged.

The falsifiable specification in `ARCHIVE_DESIGN_20261010.md` was written before
the new source. `archive.py` now implements the stream, hash, manifest, ZIP layout,
atomic installation, once-read input snapshot and actual offline Project replay.
The CLI exposes `export` and `verify-bundle`; these are executable paths, with no
network service, optional dependency or scientific runner.

Every generated study is explicitly an artificial engineering fixture. The full
negative demo reaches its existing fictional gate-10 state and round-trips
without changing its negative disposition. Actual retained v1 fixture states
also replay byte-for-byte without resealing or migration. No real scientific
checkpoint, protected boundary, protocol, split or scientific result changes.
No paid compute, accelerator, protected evaluation or external submission ran.

## Retained development failures

The initial contract tests ran before `archive.py` and the CLI commands existed.
Two methods failed because the module was absent; the real CLI method failed
because `export` was unsupported. These three test observations establish one
missing release capability, not three separate implementation defects.
Their complete output is retained in
`verification/evidence_bundle_20261010/initial_missing_feature.txt`.

The first implementation passed those three methods, including the full negative
fixture. Expanded adversarial testing then reported three errors: two test
fixtures supplied a one-field development note, inconsistent with the existing
six-field ledger schema; those fixtures were corrected without changing ledger
admission. The third found an actual descriptor-ownership defect. Wrapping an
open directory with `os.fdopen` raised `IsADirectoryError` before the regular-file
check and left that descriptor open on the tested Python runtime. The reader now
checks `fstat` before wrapping, uses `closefd=False`, and closes its owned raw
descriptor unconditionally. The rejected-directory regression verifies closure.
The original errors remain in `adversarial_first.txt`.

A final upper-limit probe found that the standard writer's conservative
`file_size * 1.05` ZIP64 guard can raise `zipfile.LargeZipFile` before the nominal
ZIP32 size threshold, outside the prior CLI error handler. The retained witness
uses a 960,000-byte object and a deliberately scaled 1,000,000-byte standard
library threshold; it exercises that actual guard without multi-gigabyte I/O.
Export now catches that specific format exception as an `IntegrityError`, giving
the CLI exit status 2 and preserving stage cleanup/no-publication behavior. No
format is silently upgraded. The original failing probe is retained in
`zip32_guard_before_fix.txt`, and its passing counterpart is retained separately.

## Executed verification

All commands ran locally with Python 3.12 on Linux, using installed standard
library dependencies. Results are engineering evidence, not empirical support
for a portfolio hypothesis.

| Stage | Actual outcome | Retained raw output |
| --- | --- | --- |
| Exact inherited suite before new tests | 65 passed; 19.874 s | `baseline_65.txt` |
| Pre-implementation capability witness | 3 methods: 1 failure, 2 errors; 0.497 s | `initial_missing_feature.txt` |
| Initial implementation on the three contract methods | 3 passed; 1.220 s | `first_implementation.txt` |
| Expanded adversarial suite before fixes | 33 methods: 30 passed, 3 errors; 1.954 s | `adversarial_first.txt` |
| Repaired archive suite | 34 passed; 1.910 s | `adversarial_repaired.txt` |
| Combined suite before the upper-limit probe | 99 passed; 23.124 s | `integrated_99.txt` |
| ZIP64 library-guard witness before normalization | 1 error; 0.051 s | `zip32_guard_before_fix.txt` |
| Repaired ZIP64 library-guard regression | 1 passed; 0.056 s | `zip32_guard_repaired.txt` |
| Intermediate combined guard implementation | 100 passed; 22.798 s | `integrated_100.txt` |
| Final exact source with the exception handler narrowed to `LargeZipFile` | 100 passed; 25.067 s | `final_integrated_100.txt` |

Raw paths are under `research_pipeline/verification/evidence_bundle_20261010/`.
Focused Ruff checks (`E4,E7,E9,F,I`) passed on the changed source and tests after
routine import formatting and removal of one unused test variable. Reproduce:

```sh
python -m unittest discover -s tests -p test_archive.py -v
python -m unittest discover -s tests -v
python -m ruff check --select E4,E7,E9,F,I research_pipeline/archive.py research_pipeline/__main__.py tests/test_archive.py
```

The new tests exercise deterministic bytes across destinations, object timestamps
and umasks; deduplication; omitted unregistered store objects; complete negative,
ACTIVE, INVALID_CLOSED and legacy v1 histories; trusted-head rollback checks;
one locked state load; state/object/input replacement; nonregular inputs; output
collision and installation failures; exact positive integer limits; source,
object, state, manifest and entry-count caps; malformed names and duplicates;
regular modes; encryption/data-descriptor flags; compression; altered CRCs,
payloads, sizes and local/central names; overlapping offsets; ZIP64; comments;
preambles; trailing or hidden bytes; canonical JSON types and state newline
identity; private temporary cleanup; and real CLI success/failure status.

## Exact source identities and independent review

The machine-readable receipt records source SHA-256 identities, unchanged ledger
identity, every validation stage and the independent review scope. Its source
base and digests identify the tested implementation without a self-referential
commit hash. The containing Git commit/tree identifies the full publication.

Independent review passed on final `archive.py` SHA-256
`976d74cdf886f8ae3840da24e2240003066ebc9d16e3c96eec022e77f772b137`.
The reviewer first inspected the complete prior implementation and independently
checked 3,145,738 binary object bytes across one- and two-MiB chunk boundaries,
ZIP CRCs and payloads, deterministic export across destination/mtime/umask
changes, offline replay after removing the live project and original inputs,
and 23 corrupted archives. All checks passed. The final review confirmed that
the exact source delta was only the four-line `LargeZipFile` normalization,
reviewed its scaled-threshold regression, and reran the independent probe on the
final source. It again passed (1.597 s). These checks are not an exhaustive parser
proof or scientific validation.

Both source-bound reviews and their reproducers are retained separately under
`research_pipeline/verification/archive_20261010/`:
`root_independent_review.py/.json` binds the earlier source;
`root_independent_review_final.py/.json` binds the final source. The earlier
receipt was not relabeled as a review of a different implementation.

## Limits and next action

The format verifies exact local bytes and ledger consistency. It does not sign
review attestations, authenticate a researcher, establish scientific validity,
or detect an otherwise valid rollback without an external trusted head. The
byte/member caps do not bound general ledger-replay CPU complexity. The local
project lock coordinates compliant writers, with no claim against privileged
directory mutation or every storage/hardware fault.

The source and evidence are prepared for the separate draft branch
`codex/percy-evidence-bundles-20261010`, stacked on the exact current PR #6 branch
`codex/ledger-json-snapshot-20261010`. The base tree is retained outside the named
changes. The existing Python 3.11/3.12 unittest workflow applies without a workflow
change or manual dispatch. Local and independent results above do not claim a
hosted job has passed before its result is observed. Review and merge remain
separate actions. No scientific gate is advanced by this delivery.
