"""Artificial bundle fixtures exercise integrity, never scientific correctness."""

from __future__ import annotations

import copy
import hashlib
import importlib
import io
import json
import os
import stat
import struct
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

import test_research_pipeline as fixtures

from research_pipeline import BusyError, GateError, IntegrityError, Project
from research_pipeline.demo import build_fixture

REPO = Path(__file__).resolve().parents[1]


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.project = Project(self.base / "study")
        self.project.initialize(fixtures.toy_contract("archive-fixture"))
        source = self.base / "source.txt"
        source.write_bytes(b"ARTIFICIAL shared evidence bytes.\n")
        self.project.add_artifact("original", "other", source)
        self.project.add_artifact("alias", "log", source, parents=["original"])

    def api(self):
        return importlib.import_module("research_pipeline.archive")

    def exported(self, name="valid.zip"):
        path = self.base / name
        self.api().export_bundle(self.project, path)
        return path

    def rewrite(self, source, transform, name="changed.zip"):
        with zipfile.ZipFile(source) as packed:
            entries = [(copy.copy(item), packed.read(item)) for item in packed.infolist()]
        entries = transform(entries)
        target = self.base / name
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)  # Intentional duplicate-name fixture.
            with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_STORED) as packed:
                for item, data in entries:
                    packed.writestr(item, data)
        return target

    def header_offsets(self, source):
        data = source.read_bytes()
        with zipfile.ZipFile(source) as packed:
            local = {item.filename: item.header_offset for item in packed.infolist()}
        central = {}
        position = struct.unpack_from("<I", data, len(data) - 6)[0]
        while data[position:position + 4] == b"PK\x01\x02":
            name_size, extra_size, comment_size = struct.unpack_from("<3H", data, position + 28)
            name = data[position + 46:position + 46 + name_size].decode("ascii")
            central[name] = position
            position += 46 + name_size + extra_size + comment_size
        return local, central

    def assert_clean(self):
        self.assertEqual(list(self.base.glob(".percy-bundle-*")), [])

    def note(self, text):
        return self.project.apply("note", {key: text for key in
                                          ("observation", "cause", "change", "prediction", "experiment", "result")})

    def test_deterministic_bytes_deduplicate_and_preserve_ledger(self):
        archive = self.api()
        original = self.project.path.read_bytes()
        before = self.project.read()
        first, second = self.base / "first.zip", self.base / "second.zip"
        one = archive.export_bundle(self.project, first, expected_head=before["head"])
        for path in (self.project.root / ".research" / "objects").iterdir():
            os.utime(path, (946684800, 946684800))
        old_umask = os.umask(0o027)
        try:
            two = archive.export_bundle(self.project, second)
        finally:
            os.umask(old_umask)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        self.assertEqual(one["bundle_sha256"], hashlib.sha256(first.read_bytes()).hexdigest())
        self.assertEqual(one["bundle_sha256"], two["bundle_sha256"])
        self.assertEqual(one["artifact_count"], 2)
        self.assertEqual(one["object_count"], 1)
        with zipfile.ZipFile(first) as packed:
            self.assertEqual(packed.read("STATE.md"), original)
            self.assertEqual(len(packed.namelist()), 3)
        self.assertEqual(self.project.path.read_bytes(), original)
        self.assertEqual(self.project.read(), before)

    def test_full_negative_fixture_replays_offline(self):
        archive = self.api()
        fixture = build_fixture(self.base / "negative-fixture")
        project = Project(fixture["project"])
        original = project.path.read_bytes()
        destination = self.base / "negative.zip"
        exported = archive.export_bundle(project, destination, expected_head=fixture["head"])
        verified = archive.verify_bundle(destination, expected_head=fixture["head"])
        self.assertEqual(exported["bundle_sha256"], verified["bundle_sha256"])
        self.assertEqual(verified["head"], fixture["head"])
        self.assertEqual(verified["recorded_state"]["status"], "COMPLETE")
        self.assertEqual(verified["recorded_state"]["checkpoint"], 10)
        self.assertEqual(verified["recorded_state"]["scientific_result"], "NEGATIVE")
        self.assertEqual(verified["recorded_state"]["evidence_seal_version"], 2)
        self.assertTrue(verified["trusted_head_checked"])
        self.assertEqual(project.path.read_bytes(), original)

    def test_cli_exports_and_verifies(self):
        destination = self.base / "cli.zip"
        head = self.project.read()["head"]
        export = subprocess.run([sys.executable, "-m", "research_pipeline", "export",
                                 str(self.project.root), "--output", str(destination),
                                 "--expected-head", head], cwd=REPO, text=True, capture_output=True)
        self.assertEqual(export.returncode, 0, export.stderr)
        verify = subprocess.run([sys.executable, "-m", "research_pipeline", "verify-bundle",
                                 str(destination), "--expected-head", head],
                                cwd=REPO, text=True, capture_output=True)
        self.assertEqual(verify.returncode, 0, verify.stderr)
        self.assertEqual(json.loads(export.stdout)["head"], head)
        result = json.loads(verify.stdout)
        self.assertEqual(result["head"], head)
        self.assertTrue(result["valid"])
        self.assertTrue(result["trusted_head_checked"])

    def test_active_and_invalid_closed_labels_are_preserved(self):
        archive = self.api()
        active = archive.verify_bundle(self.exported())
        self.assertEqual(active["recorded_state"], {"status": "ACTIVE", "checkpoint": 0,
                                                   "scientific_result": "NOT_YET_TESTED",
                                                   "evidence_seal_version": None})
        self.assertFalse(active["trusted_head_checked"])
        source = self.base / "invalid.txt"
        source.write_text("ARTIFICIAL validity defect retained without scientific execution.")
        self.project.add_artifact("invalid-report", "verification", source)
        self.project.apply("close_invalid", {"reason": "Artificial defect", "report_artifact": "invalid-report"})
        original = self.project.path.read_bytes()
        closed = archive.verify_bundle(self.exported("invalid.zip"))
        self.assertEqual(closed["recorded_state"]["status"], "INVALID_CLOSED")
        self.assertEqual(closed["recorded_state"]["scientific_result"], "INVALID")
        self.assertEqual(self.project.path.read_bytes(), original)

    def test_legacy_v1_seals_round_trip_without_migration(self):
        archive = self.api()
        fixture = json.loads((REPO / "tests/fixtures/legacy_ledger_v1.json").read_text())
        for stage in ("locked", "verified", "complete"):
            with self.subTest(stage=stage):
                project = Project(self.base / stage)
                objects = project.root / ".research" / "objects"
                objects.mkdir(parents=True)
                for sha, content in fixture["objects"].items():
                    (objects / sha).write_text(content)
                project.path.write_text(fixture["states"][stage])
                original = project.path.read_bytes()
                before = project.read()
                target = self.base / (stage + ".zip")
                archive.export_bundle(project, target)
                result = archive.verify_bundle(target, expected_head=before["head"])
                self.assertEqual(result["recorded_state"]["evidence_seal_version"], 1)
                self.assertEqual(result["recorded_state"]["checkpoint"], before["state"]["checkpoint"])
                self.assertEqual(project.path.read_bytes(), original)

    def test_empty_inventory_and_unregistered_store_objects(self):
        archive = self.api()
        empty = Project(self.base / "empty")
        empty.initialize(fixtures.toy_contract("empty-fixture"))
        target = self.base / "empty.zip"
        archive.export_bundle(empty, target)
        self.assertEqual(archive.verify_bundle(target)["object_count"], 0)
        orphan = b"ARTIFICIAL orphan must not become registered evidence."
        store = self.project.root / ".research" / "objects"
        (store / hashlib.sha256(orphan).hexdigest()).write_bytes(orphan)
        self.assertEqual(archive.verify_bundle(self.exported())["object_count"], 1)

    def test_valid_older_bundle_needs_external_head_to_detect_rollback(self):
        archive = self.api()
        old = self.project.read()["head"]
        previous = self.exported("previous.zip")
        self.note("ARTIFICIAL later decision; old history remains valid.")
        current = self.project.read()["head"]
        self.assertNotEqual(old, current)
        unanchored = archive.verify_bundle(previous)
        self.assertEqual(unanchored["head"], old)
        self.assertFalse(unanchored["trusted_head_checked"])
        self.assertTrue(archive.verify_bundle(previous, expected_head=old)["trusted_head_checked"])
        with self.assertRaisesRegex(IntegrityError, "trusted expected head"):
            archive.verify_bundle(previous, expected_head=current)

    def test_export_stale_head_does_not_append_rejection_or_publish(self):
        archive = self.api()
        original = self.project.path.read_bytes()
        target = self.base / "stale.zip"
        with self.assertRaisesRegex(IntegrityError, "trusted expected head"):
            archive.export_bundle(self.project, target, expected_head="0" * 64)
        self.assertFalse(target.exists())
        self.assertEqual(self.project.path.read_bytes(), original)
        self.assert_clean()

    def test_export_uses_one_locked_load_and_renders_its_verified_snapshot(self):
        archive = self.api()
        original = self.project.path.read_bytes()
        old_load, old_lock = self.project._load, self.project._lock
        counts = {"load": 0, "lock": 0}

        @contextmanager
        def locked():
            counts["lock"] += 1
            with old_lock():
                yield

        def load_then_replace():
            counts["load"] += 1
            verified = old_load()
            self.project.path.write_text("Unverified replacement after the only load.\n")
            with self.assertRaises(BusyError):
                Project(self.project.root).apply("note", {"text": "Competing fixture writer"})
            return verified

        try:
            with mock.patch.object(self.project, "_load", side_effect=load_then_replace), \
                    mock.patch.object(self.project, "_lock", side_effect=locked):
                target = self.exported()
            with zipfile.ZipFile(target) as packed:
                self.assertEqual(packed.read("STATE.md"), original)
            archive.verify_bundle(target)
            self.assertEqual(counts, {"load": 1, "lock": 1})
        finally:
            self.project.path.write_bytes(original)

    def test_export_object_replacement_after_load_is_not_published(self):
        item = self.project.read()["state"]["artifacts"]["original"]
        path = self.project.root / ".research" / "objects" / item["sha256"]
        original_object, original_state = path.read_bytes(), self.project.path.read_bytes()
        old_load = self.project._load

        def load_then_replace():
            verified = old_load()
            other = self.base / "replacement"
            other.write_bytes(b"!" * len(original_object))
            os.replace(other, path)
            return verified

        with mock.patch.object(self.project, "_load", side_effect=load_then_replace):
            with self.assertRaisesRegex(IntegrityError, "SHA-256 mismatch"):
                self.exported()
        self.assertFalse((self.base / "valid.zip").exists())
        self.assertEqual(self.project.path.read_bytes(), original_state)
        self.assert_clean()

    def test_export_missing_symlink_and_fifo_objects_after_load_are_refused(self):
        archive = self.api()
        item = self.project.read()["state"]["artifacts"]["original"]
        path = self.project.root / ".research" / "objects" / item["sha256"]
        original = path.read_bytes()
        old_load = self.project._load
        for kind in ("missing", "symlink", "fifo"):
            with self.subTest(kind=kind):
                def load_then_replace():
                    verified = old_load()
                    path.unlink()
                    if kind == "symlink":
                        path.symlink_to(self.base / "source.txt")
                    elif kind == "fifo":
                        os.mkfifo(path)
                    return verified

                with mock.patch.object(self.project, "_load", side_effect=load_then_replace):
                    with self.assertRaises(IntegrityError):
                        archive.export_bundle(self.project, self.base / (kind + ".zip"))
                path.unlink(missing_ok=True)
                path.write_bytes(original)
                self.assert_clean()

    def test_input_path_replacement_after_first_read_keeps_original_snapshot(self):
        archive = self.api()
        source = self.exported()
        old_bytes, old_head = source.read_bytes(), self.project.read()["head"]
        self.note("ARTIFICIAL newer history in replacement bundle.")
        replacement = self.exported("newer.zip")
        reader, opens, replaced = archive._regular_reader, [], []

        class SwapAfterRead:
            def __init__(self, incoming):
                self.incoming = incoming

            def fileno(self):
                return self.incoming.fileno()

            def read(self, count):
                data = self.incoming.read(count)
                if not replaced:
                    os.replace(replacement, source)
                    replaced.append(True)
                return data

        @contextmanager
        def watched(path, label):
            with reader(path, label) as incoming:
                if Path(path) == source:
                    opens.append(path)
                    yield SwapAfterRead(incoming)
                else:
                    yield incoming

        with mock.patch.object(archive, "_regular_reader", side_effect=watched):
            verified = archive.verify_bundle(source, expected_head=old_head)
        self.assertEqual(len(opens), 1)
        self.assertNotEqual(source.read_bytes(), old_bytes)
        self.assertEqual(verified["bundle_sha256"], hashlib.sha256(old_bytes).hexdigest())
        self.assertEqual(verified["bundle_bytes"], len(old_bytes))
        self.assertEqual(verified["head"], old_head)

    def test_input_symlink_directory_and_fifo_are_refused(self):
        archive = self.api()
        source = self.exported()
        link, fifo = self.base / "link.zip", self.base / "fifo.zip"
        link.symlink_to(source)
        os.mkfifo(fifo)
        for path in (link, fifo, self.base):
            with self.subTest(path=path.name), self.assertRaises(IntegrityError):
                archive.verify_bundle(path)

    def test_nonregular_descriptor_is_closed_even_before_wrapping(self):
        archive = self.api()
        original_close = archive.os.close
        with mock.patch.object(archive.os, "close", wraps=original_close) as closed:
            with self.assertRaisesRegex(IntegrityError, "regular file"):
                with archive._regular_reader(self.base, "directory fixture"):
                    self.fail("directory was admitted")
        self.assertEqual(closed.call_count, 1)
        descriptor = closed.call_args.args[0]
        with self.assertRaises(OSError):
            os.fstat(descriptor)

    def test_existing_output_and_dangling_symlink_are_not_overwritten(self):
        archive = self.api()
        target, link = self.base / "existing.zip", self.base / "dangling.zip"
        target.write_bytes(b"EXISTING unrelated evidence")
        link.symlink_to(self.base / "absent")
        original = self.project.path.read_bytes()
        for path in (target, link):
            with self.subTest(path=path.name), self.assertRaises(FileExistsError):
                archive.export_bundle(self.project, path)
        self.assertEqual(target.read_bytes(), b"EXISTING unrelated evidence")
        self.assertTrue(link.is_symlink())
        self.assertEqual(self.project.path.read_bytes(), original)
        self.assert_clean()

    def test_output_collision_at_atomic_install_preserves_competing_file(self):
        archive = self.api()
        target = self.base / "collision.zip"
        old_link = archive.os.link

        def collision(staging, destination):
            Path(destination).write_bytes(b"Competing writer owns this output.")
            return old_link(staging, destination)

        with mock.patch.object(archive.os, "link", side_effect=collision):
            with self.assertRaises(FileExistsError):
                archive.export_bundle(self.project, target)
        self.assertEqual(target.read_bytes(), b"Competing writer owns this output.")
        self.assert_clean()

    def test_write_file_sync_and_link_failures_clean_only_owned_stage(self):
        archive = self.api()
        sentinel = self.base / ".percy-bundle-unrelated"
        sentinel.write_bytes(b"Another process owns this staging name.")
        original = self.project.path.read_bytes()
        patches = [mock.patch.object(zipfile.ZipFile, "writestr", side_effect=OSError("write fixture failure")),
                   mock.patch.object(archive.os, "fsync", side_effect=OSError("file sync fixture failure")),
                   mock.patch.object(archive.os, "link", side_effect=OSError("link fixture failure"))]
        for index, patch in enumerate(patches):
            target = self.base / f"failure-{index}.zip"
            with self.subTest(stage=index), patch, self.assertRaises(OSError):
                archive.export_bundle(self.project, target)
            self.assertFalse(target.exists())
            self.assertEqual(list(self.base.glob(".percy-bundle-*")), [sentinel])
            self.assertEqual(self.project.path.read_bytes(), original)

    def test_directory_sync_failure_truthfully_reports_installed_bundle(self):
        archive = self.api()
        target = self.base / "installed.zip"
        original = self.project.path.read_bytes()
        with mock.patch.object(archive, "_sync_directory", side_effect=OSError("directory sync fixture")):
            with self.assertRaisesRegex(OSError, "was installed.*directory fsync failed"):
                archive.export_bundle(self.project, target)
        self.assertTrue(archive.verify_bundle(target)["valid"])
        self.assertEqual(self.project.path.read_bytes(), original)
        self.assert_clean()

    def test_zip32_library_guard_is_reported_as_a_bounded_format_refusal(self):
        archive = self.api()
        from research_pipeline.__main__ import main

        large = self.base / "larger-object.txt"
        large.write_bytes(b"X" * 960_000)
        self.project.add_artifact("larger", "other", large)
        # The real stdlib guard uses file_size * 1.05. Scale its threshold down
        # so this boundary runs on a 1 MiB fixture instead of a multi-GiB object.
        with mock.patch.object(zipfile, "ZIP64_LIMIT", 1_000_000):
            with self.assertRaisesRegex(IntegrityError, "ZIP32"):
                archive.export_bundle(self.project, self.base / "large.zip", max_bytes=999_999)
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                status = main(["export", str(self.project.root), "--output", str(self.base / "cli-large.zip"),
                               "--max-bytes", "999999"])
        self.assertEqual(status, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("ZIP32", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())
        self.assertFalse((self.base / "large.zip").exists())
        self.assertFalse((self.base / "cli-large.zip").exists())
        self.assert_clean()

    def test_exact_positive_integer_options_reject_coercion_and_booleans(self):
        archive = self.api()
        source = self.exported()
        for field in ("max_bytes", "max_object_bytes", "max_members"):
            for value in (False, True, 0, -1, 1.5, "1", None):
                with self.subTest(field=field, value=value):
                    with self.assertRaisesRegex(GateError, "exact positive integer"):
                        archive.verify_bundle(source, **{field: value})
                    with self.assertRaisesRegex(GateError, "exact positive integer"):
                        archive.export_bundle(self.project, self.base / "invalid-limit.zip", **{field: value})
        for head in (False, 1, "A" * 64, "0" * 63, "0" * 65):
            with self.subTest(head=head), self.assertRaisesRegex(GateError, "SHA-256 identity"):
                archive.verify_bundle(source, expected_head=head)

    def test_actual_byte_object_and_member_caps_have_exact_boundaries(self):
        archive = self.api()
        source = self.exported()
        total = source.stat().st_size
        object_size = self.project.read()["state"]["artifacts"]["original"]["bytes"]
        limits = {"max_bytes": total, "max_object_bytes": object_size, "max_members": 3}
        archive.verify_bundle(source, **limits)
        archive.export_bundle(self.project, self.base / "exact.zip", **limits)
        for field, value in limits.items():
            with self.subTest(field=field):
                bounded = {**limits, field: value - 1}
                with self.assertRaisesRegex(IntegrityError, "cap"):
                    archive.verify_bundle(source, **bounded)
                with self.assertRaisesRegex(IntegrityError, "cap"):
                    archive.export_bundle(self.project, self.base / (field + ".zip"), **bounded)
                self.assertFalse((self.base / (field + ".zip")).exists())
        oversized = self.base / "sparse-too-large.zip"
        with oversized.open("wb") as handle:
            handle.truncate(archive.DEFAULT_MAX_BYTES + 1)
        with self.assertRaisesRegex(IntegrityError, "byte cap"):
            archive.verify_bundle(oversized)

    def test_fixed_state_and_manifest_caps_precede_ledger_replay(self):
        archive = self.api()
        source = self.exported()
        for member, cap in (("STATE.md", archive.MAX_STATE_BYTES), ("manifest.json", archive.MAX_MANIFEST_BYTES)):
            with self.subTest(member=member):
                target = self.rewrite(source, lambda entries: [(info, b" " * (cap + 1) if info.filename == member else data)
                                                               for info, data in entries], member + ".zip")
                with mock.patch.object(Project, "_load", side_effect=AssertionError("must refuse before replay")):
                    with self.assertRaisesRegex(IntegrityError, "byte cap"):
                        archive.verify_bundle(target)

    def test_missing_state_manifest_or_object_is_rejected(self):
        archive = self.api()
        source = self.exported()
        with zipfile.ZipFile(source) as packed:
            names = packed.namelist()
        for missing in names:
            with self.subTest(missing=missing):
                target = self.rewrite(source, lambda entries: [(info, data) for info, data in entries if info.filename != missing])
                with self.assertRaises(IntegrityError):
                    archive.verify_bundle(target)

    def test_tampered_object_state_and_manifest_are_rejected(self):
        archive = self.api()
        source = self.exported()
        with zipfile.ZipFile(source) as packed:
            names = packed.namelist()
        for changed in names:
            with self.subTest(changed=changed):
                target = self.rewrite(source, lambda entries: [(info, b"!" * len(data) if info.filename == changed else data)
                                                               for info, data in entries])
                with self.assertRaises(IntegrityError):
                    archive.verify_bundle(target)

    def test_state_newline_normalization_cannot_hide_changed_archived_bytes(self):
        archive = self.api()
        source = self.exported()
        target = self.rewrite(source, lambda entries: [(info, data.replace(b"\n", b"\r\n") if info.filename == "STATE.md" else data)
                                                       for info, data in entries])
        with self.assertRaisesRegex(IntegrityError, "STATE.md bytes differ"):
            archive.verify_bundle(target)

    def test_manifest_requires_exact_canonical_values_types_and_encoding(self):
        archive = self.api()
        source = self.exported()
        variants = [lambda value: {**value, "schema_version": True},
                    lambda value: {**value, "status": "COMPLETE"},
                    lambda value: {**value, "head": "0" * 64},
                    lambda value: {**value, "objects": []},
                    lambda value: {**value, "extra": "Unbound claim"}]
        for index, change in enumerate(variants):
            def altered(entries):
                info, data = entries[0]
                entries[0] = (info, json.dumps(change(json.loads(data)), sort_keys=True, separators=(",", ":")).encode() + b"\n")
                return entries
            with self.subTest(variant=index):
                target = self.rewrite(source, altered)
                with self.assertRaisesRegex(IntegrityError, "manifest disagrees"):
                    archive.verify_bundle(target)
        target = self.rewrite(source, lambda entries: [(info, data + b" " if info.filename == "manifest.json" else data)
                                                       for info, data in entries])
        with self.assertRaisesRegex(IntegrityError, "manifest disagrees"):
            archive.verify_bundle(target)

    def test_duplicate_and_unsafe_member_names_are_rejected(self):
        archive = self.api()
        source = self.exported()
        target = self.rewrite(source, lambda entries: entries + [entries[-1]])
        with self.assertRaisesRegex(IntegrityError, "duplicate"):
            archive.verify_bundle(target)
        for name in ("../escape", "/absolute", "objects/../../escape", "objects\\escape",
                     "objects/" + "A" * 64, "objects/" + "0" * 64 + "/../escape", "extra.txt"):
            def rename(entries):
                entries[-1][0].filename = name
                return entries
            with self.subTest(name=name):
                target = self.rewrite(source, rename)
                with self.assertRaises(IntegrityError):
                    archive.verify_bundle(target)
        self.assertFalse((self.base / "escape").exists())

    def test_valid_but_unregistered_object_is_rejected(self):
        archive = self.api()
        source = self.exported()
        orphan = b"ARTIFICIAL extra object with a correct digest."

        def extra(entries):
            info = copy.copy(entries[-1][0])
            info.filename = "objects/" + hashlib.sha256(orphan).hexdigest()
            entries.append((info, orphan))
            return entries[:2] + sorted(entries[2:], key=lambda item: item[0].filename)

        target = self.rewrite(source, extra)
        with self.assertRaisesRegex(IntegrityError, "unregistered objects"):
            archive.verify_bundle(target)

    def test_nonregular_compressed_and_noncanonical_metadata_are_rejected(self):
        archive = self.api()
        source = self.exported()
        variants = [("external_attr", (stat.S_IFLNK | 0o777) << 16),
                    ("external_attr", (stat.S_IFDIR | 0o700) << 16),
                    ("external_attr", (stat.S_IFIFO | 0o600) << 16),
                    ("compress_type", zipfile.ZIP_DEFLATED), ("create_system", 0),
                    ("date_time", (2020, 1, 1, 0, 0, 0)), ("comment", b"Unbound comment"),
                    ("extra", b"\xfe\xca\x00\x00")]
        for attribute, value in variants:
            def altered(entries):
                setattr(entries[-1][0], attribute, value)
                return entries
            with self.subTest(attribute=attribute, value=value):
                target = self.rewrite(source, altered)
                with self.assertRaises(IntegrityError):
                    archive.verify_bundle(target)

    def test_encryption_and_data_descriptor_flags_are_refused(self):
        archive = self.api()
        source = self.exported()
        local, central = self.header_offsets(source)
        member = next(name for name in local if name.startswith("objects/"))
        for flag in (1, 8):
            data = bytearray(source.read_bytes())
            struct.pack_into("<H", data, local[member] + 6, flag)
            struct.pack_into("<H", data, central[member] + 8, flag)
            target = self.base / f"flag-{flag}.zip"
            target.write_bytes(data)
            with self.subTest(flag=flag), self.assertRaisesRegex(IntegrityError, "flagged ZIP"):
                archive.verify_bundle(target)

    def test_crc_payload_size_and_local_header_corruption_are_rejected(self):
        archive = self.api()
        source = self.exported()
        local, central = self.header_offsets(source)
        member = next(name for name in local if name.startswith("objects/"))
        original = source.read_bytes()
        cases = []
        payload = bytearray(original)
        payload[local[member] + 30 + len(member)] ^= 1
        cases.append(("payload", payload))
        crc = bytearray(original)
        wrong_crc = struct.unpack_from("<I", crc, local[member] + 14)[0] ^ 1
        struct.pack_into("<I", crc, local[member] + 14, wrong_crc)
        struct.pack_into("<I", crc, central[member] + 16, wrong_crc)
        cases.append(("crc", crc))
        size = bytearray(original)
        smaller = struct.unpack_from("<I", size, local[member] + 22)[0] - 1
        for position in (local[member] + 18, local[member] + 22, central[member] + 20, central[member] + 24):
            struct.pack_into("<I", size, position, smaller)
        cases.append(("size", size))
        header = bytearray(original)
        header[local[member] + 30] ^= 1
        cases.append(("local-name", header))
        nul = bytearray(original)
        nul[local[member] + 30 + 10] = 0
        nul[central[member] + 46 + 10] = 0
        cases.append(("nul-name", nul))
        overlap = bytearray(original)
        struct.pack_into("<I", overlap, central[member] + 42, 0)
        cases.append(("overlap", overlap))
        for label, data in cases:
            target = self.base / (label + ".zip")
            target.write_bytes(data)
            with self.subTest(label=label), self.assertRaises(IntegrityError):
                archive.verify_bundle(target)

    def test_preamble_trailing_comment_zip64_and_hidden_local_bytes_are_rejected(self):
        archive = self.api()
        source = self.exported()
        original = source.read_bytes()
        for label, data in (("preamble", b"Unbound bytes" + original),
                            ("trailing", original + b"Unbound bytes"),
                            ("truncated", original[:-1])):
            target = self.base / (label + ".zip")
            target.write_bytes(data)
            with self.subTest(label=label), self.assertRaises(IntegrityError):
                archive.verify_bundle(target)
        commented = self.base / "commented.zip"
        commented.write_bytes(original)
        with zipfile.ZipFile(commented, "a") as packed:
            packed.comment = b"Unbound archive comment"
        with self.assertRaises(IntegrityError):
            archive.verify_bundle(commented)
        zip64 = self.base / "zip64.zip"
        with zipfile.ZipFile(source) as incoming, zipfile.ZipFile(zip64, "w") as outgoing:
            for item in incoming.infolist():
                with outgoing.open(copy.copy(item), "w", force_zip64=True) as member:
                    member.write(incoming.read(item))
        with self.assertRaises(IntegrityError):
            archive.verify_bundle(zip64)
        # Insert an orphan local-record-sized gap and adjust EOCD's directory offset.
        offset = struct.unpack_from("<I", original, len(original) - 6)[0]
        gap = b"PK\x03\x04" + b"\0" * 26
        hidden = bytearray(original[:offset] + gap + original[offset:])
        struct.pack_into("<I", hidden, len(hidden) - 6, offset + len(gap))
        target = self.base / "hidden.zip"
        target.write_bytes(hidden)
        with self.assertRaisesRegex(IntegrityError, "unaccounted bytes"):
            archive.verify_bundle(target)

    def test_central_count_is_checked_before_zip_reader_allocation(self):
        archive = self.api()
        source = self.exported()
        data = bytearray(source.read_bytes())
        struct.pack_into("<2H", data, len(data) - 14, 60_000, 60_000)
        target = self.base / "many-members.zip"
        target.write_bytes(data)
        with mock.patch.object(zipfile, "ZipFile", side_effect=AssertionError("must refuse before ZIP allocation")):
            with self.assertRaisesRegex(IntegrityError, "member-count cap"):
                archive.verify_bundle(target)

    def test_verifier_removes_private_storage_after_failure(self):
        archive = self.api()
        source = self.base / "invalid.zip"
        source.write_bytes(b"Malformed artificial input")
        original_factory, directories = tempfile.TemporaryDirectory, []

        def private_directory(*args, **kwargs):
            result = original_factory(*args, dir=self.base, **kwargs)
            directories.append(Path(result.name))
            return result

        with mock.patch.object(archive.tempfile, "TemporaryDirectory", side_effect=private_directory):
            with self.assertRaises(IntegrityError):
                archive.verify_bundle(source)
        self.assertEqual(len(directories), 1)
        self.assertFalse(directories[0].exists())

    def test_cli_reports_bad_bundle_and_bad_limits_without_success(self):
        source = self.base / "bad.zip"
        source.write_bytes(b"Invalid artificial ZIP bytes")
        for arguments in ([str(source)], [str(source), "--max-members", "0"]):
            result = subprocess.run([sys.executable, "-m", "research_pipeline", "verify-bundle", *arguments],
                                    cwd=REPO, text=True, capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
