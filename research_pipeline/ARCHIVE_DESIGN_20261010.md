# Deterministic evidence bundles — engineering contract

This contract is recorded before implementation, on Percy-Projects PR #6 head
`eb3d36109e93a32ec2bd1454899cd106d029da4b`. It adds an engineering release tool.
It does not change ledger transitions, qualify a scientific checkpoint, execute
research, or authenticate a reviewer. Existing frozen and adverse histories stay
unchanged. ACTIVE, COMPLETE and INVALID_CLOSED histories are all exportable;
the bundle records their existing disposition exactly.

## Falsifiable behavior

1. Two exports of the same verified snapshot produce identical bytes regardless
   of destination, wall clock, object filesystem timestamps or process umask.
2. Export takes the project lock once and derives both state bytes and manifest
   from that single verified `_load` result. It never rereads the state pathname.
   Every registered artifact record is retained; byte-identical objects occur
   once, sorted by digest. Unregistered objects are omitted.
3. The exact bytes copied into the archive must match each registered SHA-256
   and byte count. A path replacement after ledger loading cannot silently
   substitute different archived evidence. Regular no-follow descriptors also
   refuse symlinks, directories and FIFOs without blocking.
4. Export installs no partial output. It uses its own sibling staging file,
   flushes/fsyncs it, atomically hard-links it to an absent destination and fsyncs
   the parent directory. A collision preserves the existing destination. A
   directory-sync failure after the link reports that output is already installed;
   it must not promise rollback. Each failure cleans only its own staging file.
5. Offline verification reads the user-supplied path once into private temporary
   storage while hashing and enforcing its byte cap. Later replacement of that
   path cannot affect this verification or its reported source digest.
6. Verification admits only the exact version-1 archive layout and expected
   member set. It never extracts arbitrary paths. It checks local/central ZIP
   metadata, member CRCs, sizes, object digests, canonical state and manifest,
   then replays the unchanged Project ledger from computed private paths.
   Additional members, unaccounted bytes, duplicate names, nonregular members,
   encryption, compression, traversal and inconsistent headers are failures.
7. A trusted expected head rejects a valid older history. Without that external
   anchor an otherwise valid rollback remains valid internally. A success receipt
   reports whether that anchor was checked; integrity is not scientific validity
   or evidence of reviewer authenticity.

Each statement above must have an executed temporary-fixture test. The full
negative demo must round-trip offline, preserving every original ledger byte and
the recorded negative result. Tests are engineering evidence only. Initial
missing-feature failures and any implementation failures remain in the dated
verification record; an absent API is one missing capability, not several
independently discovered defects.

## Version-1 format and bounds

ZIP_STORED members appear in this order: `manifest.json`, `STATE.md`, then
`objects/<64-character lowercase SHA-256>` sorted by digest. There are no
directory entries, comments, extra fields, data descriptors, ZIP64 records,
preambles or trailing payload. Metadata is fixed: UNIX regular file mode 0600,
DOS timestamp 1980-01-01 00:00:00, ZIP version 2.0 and zero flags/attributes apart
from the fixed regular-file mode. Version 1 deliberately supports the seekable
ZIP32 subset produced by the standard library, below its 2 GiB ZIP64 threshold.

The canonical manifest is UTF-8 compact sorted-key JSON followed by one newline.
It binds format/schema version, project ID, ledger head/event count, recorded
status/checkpoint/scientific result/evidence seal version, exact canonical state
SHA-256 and bytes, every artifact record, and the sorted deduplicated object
inventory. It contains no export time or local pathname. The manifest is rebuilt
from replayed state and compared byte-for-byte, preventing permissive JSON type
equality from accepting a different declaration.

Default source/output and aggregate uncompressed caps are each 512 MiB;
the default per-object cap is 512 MiB and entry-count cap is 10,000. These three
limits may be lowered or raised explicitly within the format's structural limits.
State and manifest have fixed 16 MiB and 8 MiB caps. All configurable limits must
be exact positive integers; booleans and coercible strings are rejected by the
Python API. ZIP entry-count and central-directory bounds are checked before the
standard ZIP reader allocates its member list. Declared and actual stream sizes
are both checked. Caps bound storage and parsed input, not general CPU time or
the ledger replay algorithm's complexity.

The CLI adds `export PROJECT --output NEW_ZIP` and `verify-bundle ZIP`, with
optional `--expected-head`, `--max-bytes`, `--max-object-bytes` and `--max-members`.
Successful receipts identify source bytes/digest, project/head, event/artifact/
object counts, recorded state and trusted-head checking. The verifier creates
no persistent project and executes no artifact or reproduction command.

## Boundaries and release criteria

The project lock coordinates compliant local writers; this work does not claim
to defeat privileged mutation of directories or hardware/filesystem failures.
Object bytes are checked as streamed, and accepted state is rendered from the
verified event snapshot. A bundle is neither a signed release nor a declaration
that its recorded scientific result is correct. Archiving does not advance a
gate or append an event. The unchanged ledger source and original histories are
identified in the final verification receipt.

Before publication: retain initial failures, pass the existing 65-test suite
plus meaningful archive regressions, obtain a separate adversarial source review,
resolve its blockers, update the canonical index without erasing prior records,
and check the exact current base for concurrent changes.
