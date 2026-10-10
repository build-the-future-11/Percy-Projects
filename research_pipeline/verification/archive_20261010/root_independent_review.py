"""Independent binary round-trip and archive-boundary corruption witnesses."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import struct
import sys
import tempfile
import time
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(root), str(root / "tests")]
from research_pipeline import IntegrityError, Project  # noqa: E402
from research_pipeline.archive import export_bundle, verify_bundle  # noqa: E402
from test_research_pipeline import toy_contract  # noqa: E402

source = root / "research_pipeline/archive.py"
source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
assert source_sha == "ec3b95811ccb89eaa4595e2877cf3965832042cd9ec78c50110227dca2eedb72"
started = time.perf_counter()
checks = []
with tempfile.TemporaryDirectory(prefix="percy-independent-archive-") as name:
    temporary = Path(name)
    project = Project(temporary / "study")
    contract = toy_contract("independent-binary-fixture")
    contract["title"] = "ARTIFICIAL Μνήμη – 证据 binary archive fixture"
    project.initialize(contract)
    values = [bytes(range(256)) * 8192 + b"\x00\xffTAIL", b"\xff\x00\x80A" * 262145]
    originals = {}
    for index, value in enumerate(values):
        path = temporary / f"generated-{index}.bin"
        path.write_bytes(value)
        project.add_artifact(f"raw-{index}", "raw", path)
        originals[hashlib.sha256(value).hexdigest()] = value
    project.add_artifact("same-byte-alias", "other", temporary / "generated-0.bin")
    head = project.read()["head"]
    ledger_bytes = project.path.read_bytes()
    first, second = temporary / "first.zip", temporary / "second.zip"
    exported = export_bundle(project, first, expected_head=head)
    for path in (project.root / ".research/objects").iterdir():
        os.utime(path, (1234567890, 1234567890))
    previous_umask = os.umask(0o027)
    try:
        export_bundle(project, second, expected_head=head)
    finally:
        os.umask(previous_umask)
    raw = first.read_bytes()
    assert raw == second.read_bytes()
    assert project.path.read_bytes() == ledger_bytes
    with zipfile.ZipFile(first) as packed:
        assert packed.testzip() is None
        assert packed.read("STATE.md") == ledger_bytes
        inventory = packed.infolist()
        assert packed.namelist() == ["manifest.json", "STATE.md"] + [
            "objects/" + digest for digest in sorted(originals)
        ]
        for digest, expected in originals.items():
            assert packed.read("objects/" + digest) == expected
    checks.append({"check": "binary_stream_round_trip", "status": "PASS",
                   "bytes_of_unique_objects": sum(map(len, values)), "unique_objects": 2,
                   "artifact_labels": 3, "independent_zip_crc_and_bytes": True,
                   "destination_mtime_umask_independent": True})
    shutil.rmtree(project.root)
    for path in temporary.glob("generated-*.bin"):
        path.unlink()
    verified = verify_bundle(first, expected_head=head)
    assert verified["valid"] and verified["trusted_head_checked"]
    assert verified["bundle_sha256"] == hashlib.sha256(raw).hexdigest()
    assert verified["bundle_bytes"] == len(raw) == exported["bundle_bytes"]
    assert verified["recorded_state"]["status"] == "ACTIVE"
    checks.append({"check": "offline_after_original_project_and_inputs_removed",
                   "status": "PASS", "head": head})

    positions = {0, 14}
    for info in inventory:
        name_length, extra_length = struct.unpack_from("<HH", raw, info.header_offset + 26)
        payload = info.header_offset + 30 + name_length + extra_length
        positions.update((payload, payload + info.file_size - 1))
        if info.filename.startswith("objects/"):
            for relative in (1048575, 1048576, 2097152):
                if relative < info.file_size:
                    positions.add(payload + relative)
    central = struct.unpack_from("<I", raw, len(raw) - 6)[0]
    positions.update(central + relative for relative in (0, 8, 14, 34, 38, 42))
    positions.update((len(raw) - 12, len(raw) - 6))
    rejections = []
    for index, position in enumerate(sorted(positions)):
        changed = bytearray(raw)
        changed[position] ^= 1
        path = temporary / f"mutation-{index}.zip"
        path.write_bytes(changed)
        try:
            verify_bundle(path, expected_head=head)
        except IntegrityError as error:
            rejections.append({"byte_offset": position, "error": str(error)})
        else:
            raise AssertionError(f"single-byte corruption was admitted at {position}")
        path.unlink()
    checks.append({"check": "local_data_chunk_boundary_central_and_end_corruption",
                   "status": "PASS", "rejected_mutations": len(rejections),
                   "rejections": rejections})

assert hashlib.sha256(source.read_bytes()).hexdigest() == source_sha
receipt = {
    "reviewer": "root independent adversarial review",
    "status": "PASS",
    "source_sha256": source_sha,
    "source_unchanged_during_execution": True,
    "seconds": time.perf_counter() - started,
    "checks": checks,
    "scope": "Generated binary objects crossing one- and two-MiB boundaries, independent ZIP CRC/payload inspection, offline replay after removal of live source, deterministic metadata, and byte corruptions. No scientific study, reviewer authentication, universal filesystem guarantee or exhaustive parser proof.",
}
Path(__file__).with_suffix(".json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt, indent=2))
