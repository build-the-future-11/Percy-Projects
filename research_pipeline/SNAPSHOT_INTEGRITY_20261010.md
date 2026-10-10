# Verified JSON snapshots and mutation receipts

## Development contract

This bounded engineering follow-up starts from PR #4 commit
`a664fea4a5db0789bde91898328514ceb8d45a31`. It does not execute a scientific
experiment or qualify a real project for a research checkpoint. The previous
implementation and its 52-test verification record remain in Git history and
`DEVELOPMENT_20261010.md`.

Two observable integrity requirements are tested:

1. A JSON protocol, verification receipt, or release manifest must be parsed
   from the same byte snapshot whose SHA-256 and size were checked. Replacing
   the path after verification must not introduce unverified JSON into a gate.
2. A successful mutation must return the ledger head and state produced by that
   mutation. Another cooperating writer may commit immediately after lock
   release, but its state must not be returned as the first writer's receipt.

## Implementation specification

The regular-file, no-follow object verifier continues to stream ordinary large
artifacts. An explicit `capture` option additionally retains its streamed chunks
for JSON consumers. Bytes are returned only after the existing digest and size
checks succeed; JSON decoding and strict parsing consume those bytes directly.
Non-JSON verification does not accumulate the object in memory. JSON already
requires memory proportional to its document size; no universal maximum size is
introduced here.

Initialization, mutation, and artifact registration return their validated
state while still holding the existing exclusive project lock. The existing
atomic replacement, fsync behavior, stale-head checks, and rejection history
are preserved. Standalone reads remain unlocked snapshots of the installed
state file.

## Falsifying engineering tests

Use artificial temporary files and deterministic interleavings. Replace a
verified JSON file with different JSON just before decoding; the returned
document must still equal the verified original, while a later fresh read must
reject the corrupt object. Schedule a second writer immediately after each
mutation releases its lock; the first receipt must identify the first mutation,
and the final ledger must include both events. Also retain the existing full
suite for hash/size mismatch, nonregular files, frozen protocols, stale writers,
durability failure, budget accounting, and terminal-state preservation.

This protects the parse boundary and cooperating-writer receipt boundary. It
does not make the local store tamper-proof, authenticate scientific evidence,
or prevent a privileged process from replacing the project directory. A trusted
external head remains necessary to detect a whole-history rollback.

## Verification result

The executed results and source hashes are recorded in the companion JSON
receipt after the implementation and regressions run. No gate is advanced by
the presence of this specification.

## Concurrent integration and final executed verification

The initial candidate passed 56 tests and a separate source review. Before
publication, concurrent PR #5 at `b2bd69186327d0e188df2f4567a116d8afebd255`
added complementary byte-bound evidence seals and legacy-history compatibility.
Those changes are preserved as this PR's base. The full combined suite
(`python -m unittest discover -s tests -v`) passes **65 tests**, including its
nine new evidence-binding tests. The prior four baseline failures and initial
56-test result are preserved alongside the final raw output and source hashes.
