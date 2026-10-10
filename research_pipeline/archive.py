"""Deterministic evidence snapshots and bounded, offline ledger replay.

This format records the existing scientific state. It neither advances a gate
nor authenticates a reviewer or scientific result. See ARCHIVE_DESIGN_20261010.md.
"""

from __future__ import annotations

import hashlib
import os
import re
import stat
import struct
import tempfile
import zipfile
from contextlib import contextmanager
from pathlib import Path

from .ledger import (
    GateError,
    IntegrityError,
    Project,
    _object_path,
    _render,
    _sync_directory,
    canonical,
)

DEFAULT_MAX_BYTES = 512 * 1024 * 1024
DEFAULT_MAX_OBJECT_BYTES = DEFAULT_MAX_BYTES
DEFAULT_MAX_MEMBERS = 10_000
MAX_STATE_BYTES = 16 * 1024 * 1024
MAX_MANIFEST_BYTES = 8 * 1024 * 1024
FORMAT_MAX_BYTES = (1 << 31) - 1  # Below the standard library's ZIP64 threshold.
CHUNK_BYTES = 1024 * 1024
_STAMP = (1980, 1, 1, 0, 0, 0)
_MODE = (stat.S_IFREG | 0o600) << 16
_END = struct.Struct("<4s4H2IH")
_LOCAL = struct.Struct("<4s5H3I2H")
_OBJECT_NAME = re.compile(r"objects/([0-9a-f]{64})\Z")


def _check(condition, message):
    if not condition:
        raise IntegrityError(message)


def _options(expected_head, max_bytes, max_object_bytes, max_members):
    for name, value in (("max_bytes", max_bytes), ("max_object_bytes", max_object_bytes),
                        ("max_members", max_members)):
        if type(value) is not int or value <= 0:
            raise GateError(f"{name} must be an exact positive integer")
    if expected_head is not None and (not isinstance(expected_head, str)
                                     or re.fullmatch(r"[0-9a-f]{64}", expected_head) is None):
        raise GateError("expected_head must be a full lowercase SHA-256 identity")


def _head(events, expected_head):
    head = events[-1]["sha256"]
    _check(expected_head is None or head == expected_head,
           "bundle state head differs from the trusted expected head")
    return head


def _recorded_state(state):
    seal = state["evidence_lock"]
    return {"status": state["status"], "checkpoint": state["checkpoint"],
            "scientific_result": state["scientific_result"],
            "evidence_seal_version": seal.get("schema_version", 1) if seal else None}


def _manifest(events, state, state_bytes):
    objects = {}
    for item in state["artifacts"].values():
        sha, size = item["sha256"], item["bytes"]
        _check(re.fullmatch(r"[0-9a-f]{64}", sha) is not None
               and type(size) is int and size > 0, "invalid registered object identity")
        _check(sha not in objects or objects[sha] == size,
               "registered records disagree about the size of one object")
        objects[sha] = size
    return {"format": "percy-evidence-bundle", "schema_version": 1,
            "project_id": state["contract"]["project_id"], "head": events[-1]["sha256"],
            "event_count": len(events), **_recorded_state(state),
            "state": {"path": "STATE.md", "sha256": hashlib.sha256(state_bytes).hexdigest(),
                      "bytes": len(state_bytes)},
            "artifacts": state["artifacts"],
            "objects": [{"path": "objects/" + sha, "sha256": sha, "bytes": objects[sha]}
                        for sha in sorted(objects)]}


def _receipt(manifest, sha, size, expected_head):
    return {"valid": True, "bundle_sha256": sha, "bundle_bytes": size,
            "project_id": manifest["project_id"], "head": manifest["head"],
            "event_count": manifest["event_count"], "artifact_count": len(manifest["artifacts"]),
            "object_count": len(manifest["objects"]),
            "recorded_state": {key: manifest[key] for key in
                               ("status", "checkpoint", "scientific_result", "evidence_seal_version")},
            "trusted_head_checked": expected_head is not None}


def _info(name, size):
    result = zipfile.ZipInfo(name, date_time=_STAMP)
    result.create_system = 3
    result.create_version = result.extract_version = 20
    result.external_attr = _MODE
    result.internal_attr = 0
    result.compress_type = zipfile.ZIP_STORED
    result.file_size = size
    return result


@contextmanager
def _regular_reader(path, label):
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except OSError as exc:
        raise IntegrityError(f"cannot open {label} as a regular no-follow file: {exc}") from exc
    try:
        _check(stat.S_ISREG(os.fstat(fd).st_mode), f"{label} must be a regular file")
        with os.fdopen(fd, "rb", closefd=False) as handle:
            yield handle
    finally:
        os.close(fd)


def _copy_checked(incoming, outgoing, limit, label, *, expected_size=None, expected_sha=None):
    sha, size = hashlib.sha256(), 0
    for chunk in iter(lambda: incoming.read(CHUNK_BYTES), b""):
        size += len(chunk)
        _check(size <= limit, f"{label} exceeds its byte cap")
        _check(expected_size is None or size <= expected_size, f"{label} size mismatch")
        sha.update(chunk)
        if outgoing is not None:
            outgoing.write(chunk)
    _check(expected_size is None or size == expected_size, f"{label} size mismatch")
    actual_sha = sha.hexdigest()
    _check(expected_sha is None or actual_sha == expected_sha, f"{label} SHA-256 mismatch")
    return actual_sha, size


def export_bundle(project, destination, *, expected_head=None, max_bytes=DEFAULT_MAX_BYTES,
                  max_object_bytes=DEFAULT_MAX_OBJECT_BYTES, max_members=DEFAULT_MAX_MEMBERS):
    """Install a deterministic bundle at a new path, without changing the ledger.

    A directory fsync error after installation raises OSError and explicitly
    reports that the destination is already installed. It must be verified before
    retrying. Existing destinations, including dangling symlinks, are never replaced.
    """
    _options(expected_head, max_bytes, max_object_bytes, max_members)
    project = project if isinstance(project, Project) else Project(project)
    destination = Path(destination).absolute()
    with project._lock():
        events, state = project._load()
        _head(events, expected_head)
        state_bytes = _render(events, state).encode("utf-8")
        _check(len(state_bytes) <= MAX_STATE_BYTES, "STATE.md exceeds its byte cap")
        manifest = _manifest(events, state, state_bytes)
        manifest_bytes = canonical(manifest) + b"\n"
        _check(len(manifest_bytes) <= MAX_MANIFEST_BYTES, "manifest.json exceeds its byte cap")
        members = [("manifest.json", len(manifest_bytes)), ("STATE.md", len(state_bytes))]
        for item in manifest["objects"]:
            _check(item["bytes"] <= max_object_bytes, "object exceeds its byte cap")
            members.append((item["path"], item["bytes"]))
        _check(len(members) <= min(max_members, 65_535), "bundle exceeds its member-count cap")
        # Each fixed member has a 30-byte local and 46-byte central header.
        encoded_size = 22 + sum(size + 76 + 2 * len(name.encode("ascii")) for name, size in members)
        _check(encoded_size <= min(max_bytes, FORMAT_MAX_BYTES), "bundle exceeds its byte cap or ZIP32 limit")
        fd, name = tempfile.mkstemp(prefix=".percy-bundle-", dir=destination.parent)
        staging, installed = Path(name), False
        try:
            with os.fdopen(fd, "w+b") as handle:
                with zipfile.ZipFile(handle, "w", compression=zipfile.ZIP_STORED, allowZip64=False) as packed:
                    packed.writestr(_info("manifest.json", len(manifest_bytes)), manifest_bytes)
                    packed.writestr(_info("STATE.md", len(state_bytes)), state_bytes)
                    for item in manifest["objects"]:
                        path = _object_path(project.root, item["sha256"])
                        with _regular_reader(path, "object " + item["sha256"]) as incoming:
                            _check(os.fstat(incoming.fileno()).st_size == item["bytes"], "object size mismatch")
                            with packed.open(_info(item["path"], item["bytes"]), "w") as outgoing:
                                _copy_checked(incoming, outgoing, max_object_bytes, "object " + item["sha256"],
                                              expected_size=item["bytes"], expected_sha=item["sha256"])
                handle.flush()
                os.fsync(handle.fileno())
                handle.seek(0)
                bundle_sha, bundle_size = _copy_checked(handle, None, max_bytes, "bundle",
                                                        expected_size=encoded_size)
            os.link(staging, destination)
            installed = True
            try:
                _sync_directory(destination.parent)
            except OSError as exc:
                raise OSError(f"bundle was installed at {destination} but directory fsync failed; "
                              "verify the installed bundle before retrying") from exc
            return {**_receipt(manifest, bundle_sha, bundle_size, expected_head),
                    "destination": str(destination), "installed": True}
        except zipfile.LargeZipFile as exc:
            # The stdlib applies an additional conservative ZIP64 guard before
            # writing large members; normalize that refusal for API/CLI callers.
            raise IntegrityError(f"cannot encode bundle in the version-1 ZIP32 format: {exc}") from exc
        finally:
            try:
                staging.unlink(missing_ok=True)
            except OSError as exc:
                condition = "was installed" if installed else "was not installed"
                raise OSError(f"bundle {condition}; cannot remove its staging file {staging}") from exc


def _snapshot_source(source, destination, max_bytes):
    with _regular_reader(source, "bundle input") as incoming:
        _check(os.fstat(incoming.fileno()).st_size <= min(max_bytes, FORMAT_MAX_BYTES),
               "bundle input exceeds its byte cap or ZIP32 limit")
        with destination.open("xb") as outgoing:
            return _copy_checked(incoming, outgoing, min(max_bytes, FORMAT_MAX_BYTES), "bundle input")


def _directory(handle, source_size, max_members):
    """Bound the central directory before ZipFile constructs its member list."""
    _check(source_size >= _END.size, "bundle is shorter than its ZIP end record")
    handle.seek(source_size - _END.size)
    signature, disk, first_disk, disk_count, count, size, offset, comment = _END.unpack(handle.read(_END.size))
    _check(signature == b"PK\x05\x06" and disk == first_disk == comment == 0 and disk_count == count,
           "bundle requires a single-disk ZIP32 end record with no comment or trailing bytes")
    _check(2 <= count <= min(max_members, 65_535), "bundle exceeds its member-count cap or lacks required members")
    # Longest legal filename is objects/<64 hexadecimal characters> (72 bytes).
    _check(count * 46 <= size <= count * (46 + 72), "invalid or oversized ZIP central directory")
    _check(offset + size + _END.size == source_size, "ZIP central directory does not account for the input bytes")
    return count, size, offset


def _members(packed, handle, directory, max_bytes, max_object_bytes):
    count, directory_size, directory_offset = directory
    entries = packed.infolist()
    _check(len(entries) == count, "ZIP entry count mismatch")
    names = [item.filename for item in entries]
    _check(len(set(names)) == len(names), "duplicate ZIP member name")
    _check(len(names) >= 2 and names[:2] == ["manifest.json", "STATE.md"],
           "bundle must begin with manifest.json and STATE.md")
    _check(names[2:] == sorted(names[2:]), "object members must be sorted by SHA-256")
    offset, aggregate, central_size = 0, 0, 0
    for item in entries:
        name = item.filename
        object_match = _OBJECT_NAME.fullmatch(name)
        _check(name in {"manifest.json", "STATE.md"} or object_match is not None, "unexpected or unsafe ZIP member name")
        _check(item.orig_filename == name, "ZIP member name contains a NUL character")
        _check(item.create_system == 3 and stat.S_ISREG(item.external_attr >> 16),
               "ZIP members must declare regular UNIX files")
        _check(item.compress_type == zipfile.ZIP_STORED and item.flag_bits == 0,
               "compressed, encrypted or flagged ZIP members are unsupported")
        _check(item.external_attr == _MODE and item.internal_attr == 0
               and item.create_version == item.extract_version == 20
               and item.reserved == item.volume == 0 and item.date_time == _STAMP
               and not item.extra and not item.comment, "ZIP member metadata differs from the fixed format")
        limit = max_object_bytes if object_match else (MAX_STATE_BYTES if name == "STATE.md" else MAX_MANIFEST_BYTES)
        _check(0 < item.file_size <= limit and item.compress_size == item.file_size, "ZIP member exceeds its byte cap or has an invalid size")
        aggregate += item.file_size
        _check(aggregate <= max_bytes, "ZIP members exceed their aggregate byte cap")
        name_bytes = name.encode("ascii")
        central_size += 46 + len(name_bytes)
        _check(item.header_offset == offset, "ZIP has a preamble, gap, overlap or unregistered local member")
        handle.seek(offset)
        raw_header = handle.read(_LOCAL.size)
        _check(len(raw_header) == _LOCAL.size, "truncated local ZIP header")
        expected = (b"PK\x03\x04", 20, 0, zipfile.ZIP_STORED, 0, 33,
                    item.CRC, item.file_size, item.file_size, len(name_bytes), 0)
        _check(_LOCAL.unpack(raw_header) == expected and handle.read(len(name_bytes)) == name_bytes,
               "local ZIP header disagrees with canonical central metadata")
        offset += _LOCAL.size + len(name_bytes) + item.file_size
        _check(offset <= directory_offset, "ZIP member overlaps its central directory")
    _check(offset == directory_offset and central_size == directory_size,
           "unaccounted bytes occur outside the allowed ZIP members")
    return entries


def verify_bundle(source, *, expected_head=None, max_bytes=DEFAULT_MAX_BYTES,
                  max_object_bytes=DEFAULT_MAX_OBJECT_BYTES, max_members=DEFAULT_MAX_MEMBERS):
    """Verify one bounded input snapshot using only local temporary storage.

    Without an externally trusted expected_head a valid older bundle can pass.
    No artifact, command or scientific analysis is executed by this verifier.
    """
    _options(expected_head, max_bytes, max_object_bytes, max_members)
    try:
        with tempfile.TemporaryDirectory(prefix="percy-bundle-verify-") as name:
            private = Path(name)
            snapshot = private / "source.zip"
            source_sha, source_size = _snapshot_source(source, snapshot, max_bytes)
            root = private / "project"
            objects = root / ".research" / "objects"
            objects.mkdir(parents=True)
            measured_state, manifest_bytes = None, None
            with snapshot.open("rb") as handle:
                directory = _directory(handle, source_size, max_members)
                with zipfile.ZipFile(handle, "r", allowZip64=False) as packed:
                    entries = _members(packed, handle, directory, max_bytes, max_object_bytes)
                    for item in entries:
                        if item.filename == "manifest.json":
                            with packed.open(item, "r") as incoming:
                                manifest_bytes = incoming.read(MAX_MANIFEST_BYTES + 1)
                            _check(len(manifest_bytes) == item.file_size, "manifest size mismatch")
                            continue
                        if item.filename == "STATE.md":
                            target, limit, expected_sha = root / "STATE.md", MAX_STATE_BYTES, None
                        else:
                            expected_sha = _OBJECT_NAME.fullmatch(item.filename).group(1)
                            target, limit = objects / expected_sha, max_object_bytes
                        with packed.open(item, "r") as incoming, target.open("xb") as outgoing:
                            measured = _copy_checked(incoming, outgoing, limit, item.filename,
                                                     expected_size=item.file_size, expected_sha=expected_sha)
                        if item.filename == "STATE.md":
                            measured_state = measured
            events, state = Project(root)._load()
            _head(events, expected_head)
            state_bytes = _render(events, state).encode("utf-8")
            manifest = _manifest(events, state, state_bytes)
            _check(measured_state == (manifest["state"]["sha256"], manifest["state"]["bytes"]),
                   "archived STATE.md bytes differ from their canonical replay")
            _check(manifest_bytes == canonical(manifest) + b"\n", "manifest disagrees with the verified canonical project")
            expected_names = ["manifest.json", "STATE.md"] + [item["path"] for item in manifest["objects"]]
            _check([item.filename for item in entries] == expected_names,
                   "bundle contains missing or unregistered objects")
            return _receipt(manifest, source_sha, source_size, expected_head)
    except (zipfile.BadZipFile, zipfile.LargeZipFile, EOFError, NotImplementedError,
            UnicodeError, struct.error, RecursionError, OverflowError) as exc:
        raise IntegrityError(f"bundle verification failed: {exc}") from exc
