"""Artificial filesystem fixtures; none of these receipts are research outcomes."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from research_pipeline import CHECKPOINTS, GateError, IntegrityError, Project
from research_pipeline.ledger import MARKER, VERIFY_CHECKS, strict_json

REPO = Path(__file__).resolve().parents[1]


def toy_contract(slug="artificial-study"):
    return {
        "project_id": slug, "title": "ARTIFICIAL ledger test fixture", "owner": "Fixture owner",
        "question": "Does the fictional proposed arm lower the declared fixture metric?",
        "objective": "Exercise durable lifecycle mechanics, without executing a scientific study.",
        "hypothesis": "The fictional proposed arm improves the fixture metric.",
        "contribution": "Engineering fixture only; no scientific contribution is claimed.",
        "scope": "Two artificial receipts and deterministic temporary files.",
        "development_budget": {"max_runs": 2},
        "compute_budget": {"seconds": 100, "description": "Artificial fixture accounting"},
        "protected_boundary": "No actual protected data exists in this artificial fixture.",
        "repositories": ["https://example.invalid/artificial"], "datasets": ["fixture"],
        "known_history": [], "definition_of_done": "All ten ledger gates are exercised.",
        "next_action": "Inspect the next fixture gate.",
    }


def toy_protocol(contract=None):
    contract = contract or toy_contract()
    return {
        "version": "artificial-v1", "question": contract["question"], "hypothesis": contract["hypothesis"],
        "code": {"repository": contract["repositories"][0], "commit": "a" * 40, "artifact": "code"},
        "architecture_artifact": "spec", "datasets": [{"id": "fixture", "version": "1", "license": "CC0 artificial fixture", "artifact": "data", "split_artifact": "split"}],
        "baselines": ["baseline"], "hyperparameters": {}, "metrics": ["mse"], "primary_endpoint": "mse",
        "direction": "lower", "practical_effect_threshold": 0.1,
        "statistics": {"procedure": "Artificial paired difference", "uncertainty": "No scientific inference", "aggregation": "One independent fixture unit", "multiplicity": "One fixture comparison", "decision_rule": "Fictional proposed metric must be smaller"},
        "seeds": [7], "independent_unit": "Artificial receipt pair",
        "exclusion_rules": "Retain every fixture receipt", "stopping_rules": "Exactly two receipts",
        "environment_artifact": "env", "compute_protocol": {"hardware": "Fictional CPU", "max_seconds": 10, "measurement": "Receipt field only"},
        "expected_runs": [{"run_id": arm, "seed": 7, "variant": arm, "dataset_id": "fixture", "config_artifact": "config"} for arm in ("proposed", "baseline")],
        "protected_boundary": contract["protected_boundary"], "protected_outcomes_unobserved": True,
    }


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.project = Project(self.base / "project")
        self.counter = 0

    def file(self, value, suffix=".txt"):
        self.counter += 1
        path = self.base / f"input-{self.counter}{suffix}"
        path.write_text(json.dumps(value, allow_nan=False) if isinstance(value, (dict, list)) else value, encoding="utf-8")
        return path

    def add(self, artifact_id, kind, value, parents=()):
        return self.project.add_artifact(artifact_id, kind, self.file(value), parents)

    def prepare(self, *, freeze=True, protocol=None):
        self.project.initialize(toy_contract())
        for artifact_id, kind, value in [
            ("spec", "specification", "ARTIFICIAL complete model/specification fixture"),
            ("code", "code", "print('artificial fixture only')\n"),
            ("config", "config", {"fixture": True}),
            ("data", "dataset", "ARTIFICIAL data bytes"),
            ("split", "split", {"train": [1], "development": [2], "protected": [3]}),
            ("env", "environment", {"fixture": True, "python": "declared, not executed"}),
            ("dry", "verification", "ARTIFICIAL dry-run receipt"),
        ]:
            self.add(artifact_id, kind, value)
        self.add("protocol", "protocol", protocol or toy_protocol())
        for number, evidence in enumerate(["spec", "spec", "protocol", "code", "code", "dry"], start=1):
            self.project.apply("checkpoint", {"number": number, "evidence": evidence, "reviewer": "Fixture reviewer", "note": "Artificial qualification, not a scientific review."})
        if freeze:
            self.project.apply("freeze", {"protocol_artifact": "protocol"})

    def run_manifest(self, arm, status="SUCCESS", phase="CONFIRMATORY"):
        raw_id, log_id = f"raw-{arm}", f"log-{arm}"
        self.add(raw_id, "raw", {"ARTIFICIAL": True, "arm": arm, "metric": 2.0 if arm == "proposed" else 1.0})
        self.add(log_id, "log", f"ARTIFICIAL {arm} {status} fixture log")
        state = self.project.read()["state"]
        return {
            "run_id": arm, "phase": phase, "status": status, "source_commit": "a" * 40,
            "config_artifact": "config", "dataset_artifact": "data", "split_artifact": "split", "environment_artifact": "env",
            "seed": 7, "variant": arm, "runtime_seconds": 0.01, "peak_memory_bytes": 128, "compute": {"fixture": True},
            "metrics": {"mse": 2.0 if arm == "proposed" else 1.0} if status == "SUCCESS" else {},
            "raw_artifacts": [raw_id] if status == "SUCCESS" else [], "log_artifacts": [log_id],
            "failure_reason": None if status == "SUCCESS" else "Artificial execution defect",
            "deviations": [], "protocol_hash": state["freeze"]["sha256"] if phase == "CONFIRMATORY" and state["freeze"] else None,
        }

    def claim(self, status="SUPPORTED", raw=None):
        raw = raw or ["raw-proposed", "raw-baseline"]
        self.add("analysis", "analysis", {"ARTIFICIAL": True, "difference": 1.0}, raw)
        self.add("table", "table", "ARTIFICIAL proposed=2, baseline=1", ["analysis"])
        return {"claim_id": "negative-finding", "text": "The artificial proposed metric is higher.",
                "scope": "Artificial fixture pair only", "status": status, "limitations": "Not a scientific experiment",
                "uncertainty": "No scientific uncertainty claim", "paper_location": "Artificial table 1", "phase": "CONFIRMATORY",
                "run_ids": ["proposed", "baseline"], "raw_artifacts": raw, "analysis_artifact": "analysis", "display_artifacts": ["table"]}

    def lock(self, disposition="NEGATIVE", statuses=("SUCCESS", "SUCCESS")):
        self.prepare()
        for arm, status in zip(("proposed", "baseline"), statuses):
            self.project.apply("run", self.run_manifest(arm, status))
        raw = [f"raw-{arm}" if status == "SUCCESS" else f"log-{arm}" for arm, status in zip(("proposed", "baseline"), statuses)]
        self.project.apply("claim", self.claim("SUPPORTED" if all(s == "SUCCESS" for s in statuses) else "UNSUPPORTED", raw))
        self.project.apply("lock_evidence", {"disposition": disposition, "scope": "Artificial fixture pair only", "reason": "Artificial adverse result, retained without tuning."})

    def verification_receipt(self):
        state = self.project.read()["state"]
        return {"reviewer": "Independent fixture reviewer", "evidence_sha256": state["evidence_lock"]["sha256"],
                "paper_sha256": state["artifacts"]["paper"]["sha256"], "environment_sha256": state["artifacts"]["env"]["sha256"],
                "paper_artifact": "paper", "environment_artifact": "env", "checks": {key: True for key in VERIFY_CHECKS},
                "reproduction_command": "Fictional receipt; do not execute", "limits": "ARTIFICIAL ledger fixture only"}

    def review(self):
        self.add("paper", "paper", "ARTIFICIAL paper fixture: proposed=2, baseline=1; negative.")
        self.add("independent", "verification", self.verification_receipt())
        self.project.apply("verify_review", {"verification_artifact": "independent"})

    def release_manifest(self):
        state = self.project.read()["state"]
        return {"release_commit": "b" * 40, "disposition": state["scientific_result"], "scope": "Artificial fixture pair only", "evidence_sha256": state["evidence_lock"]["sha256"],
                "roles": {"paper": "paper", "code": "code", "configuration": ["config"], "environment": "env", "reproduction": "instructions", "data_instructions": "instructions"},
                "reviews": {key: {"not_applicable": "ARTIFICIAL software fixture, no scientific submission"} for key in ("bibliography", "supplement", "authorship", "licensing", "ethics", "venue", "arxiv", "submission")}}

    def finish(self):
        self.lock()
        self.review()
        self.add("instructions", "other", "ARTIFICIAL instructions: use unittest, no science execution.")
        self.add("release", "release", self.release_manifest())
        self.project.apply("complete", {"release_artifact": "release"})

    def test_complete_negative_study_preserves_all_evidence(self):
        self.finish()
        result = self.project.read()
        self.assertEqual(result["state"]["scientific_result"], "NEGATIVE")
        self.assertEqual(result["state"]["status"], "COMPLETE")
        self.assertEqual(result["state"]["checkpoint"], 10)
        self.assertEqual(CHECKPOINTS[10], "RESEARCH COMPLETE")
        self.assertEqual(set(result["state"]["runs"]), {"proposed", "baseline"})
        self.assertIn("Canonical event ledger", self.project.path.read_text())

    def test_all_valid_outcomes_can_lock_without_requiring_a_positive_label(self):
        for disposition in ("SUPPORTED", "MIXED", "NEGATIVE", "INCONCLUSIVE"):
            with self.subTest(disposition=disposition):
                self.project = Project(self.base / disposition)
                self.lock(disposition)
                self.assertEqual(self.project.read()["state"]["scientific_result"], disposition)
                self.review()
                self.add("instructions", "other", "ARTIFICIAL instructions, no scientific execution")
                self.add("release", "release", self.release_manifest())
                self.project.apply("complete", {"release_artifact": "release"})
                self.assertEqual(self.project.read()["state"]["status"], "COMPLETE")

    def test_rejected_checkpoint_is_retained_without_advancing(self):
        self.project.initialize(toy_contract())
        before = self.project.read()
        with self.assertRaises(GateError):
            self.project.apply("checkpoint", {"number": 2, "evidence": "absent", "reviewer": "x", "note": "x"})
        after = self.project.read()
        self.assertEqual(after["event_count"], before["event_count"] + 1)
        self.assertEqual(after["state"]["checkpoint"], 0)
        self.assertIn("in order", after["state"]["rejections"][-1]["reason"])

    def test_artifact_snapshot_survives_source_mutation(self):
        self.project.initialize(toy_contract())
        source = self.file("first bytes")
        self.project.add_artifact("source", "other", source)
        source.write_text("later bytes")
        state = self.project.read()["state"]
        item = state["artifacts"]["source"]
        self.assertEqual(item["sha256"], hashlib.sha256(b"first bytes").hexdigest())
        self.assertEqual((self.project.root / ".research" / "objects" / item["sha256"]).read_bytes(), b"first bytes")

    def test_retained_object_mutation_blocks_read_and_new_writes(self):
        self.project.initialize(toy_contract())
        self.add("source", "other", "retained")
        item = self.project.read()["state"]["artifacts"]["source"]
        original = self.project.path.read_bytes()
        (self.project.root / ".research" / "objects" / item["sha256"]).write_bytes(b"tampered")
        with self.assertRaises(IntegrityError):
            self.project.read()
        with self.assertRaises(IntegrityError):
            self.project.apply("note", {})
        self.assertEqual(self.project.path.read_bytes(), original)

    def test_state_projection_and_event_mutations_are_detected(self):
        self.project.initialize(toy_contract())
        original = self.project.path.read_text()
        self.project.path.write_text(original.replace("ARTIFICIAL ledger test fixture", "Changed", 1))
        with self.assertRaises(IntegrityError):
            self.project.read()
        # Mutate an event payload, leaving its recorded hash unchanged.
        self.project.path.write_text(original.replace('"owner": "Fixture owner"', '"owner": "Other owner"'))
        with self.assertRaises(IntegrityError):
            self.project.read()

    def test_external_head_detects_a_valid_history_rollback(self):
        self.project.initialize(toy_contract())
        original = self.project.path.read_bytes()
        self.project.apply("note", {key: "artificial" for key in ("observation", "cause", "change", "prediction", "experiment", "result")})
        trusted = self.project.read()["head"]
        self.project.path.write_bytes(original)
        self.project.read()  # A self-consistent older chain needs an external anchor.
        with self.assertRaises(IntegrityError):
            self.project.read(expected_head=trusted)

    def test_duplicate_artifact_and_run_ids_never_replace_prior_evidence(self):
        self.prepare()
        self.project.apply("run", self.run_manifest("proposed", "FAILED"))
        prior = copy.deepcopy(self.project.read()["state"]["runs"]["proposed"])
        with self.assertRaises(GateError):
            self.project.apply("run", {**prior, "status": "SUCCESS"})
        with self.assertRaises(GateError):
            self.add("data", "dataset", "replacement")
        self.assertEqual(self.project.read()["state"]["runs"]["proposed"], prior)

    def test_development_revision_retains_history_and_resets_qualifications(self):
        self.prepare(freeze=False)
        manifest = self.run_manifest("development", phase="DEVELOPMENT")
        self.project.apply("run", manifest)
        revised = toy_contract()
        revised["hypothesis"] = "An explicitly revised development hypothesis."
        self.project.apply("revise", {"contract": revised, "reason": "Recorded scientific revision"})
        state = self.project.read()["state"]
        self.assertEqual(state["checkpoint"], 0)
        self.assertEqual(state["version"], 2)
        self.assertIn("development", state["runs"])

    def test_freeze_is_immutable_and_closes_development(self):
        self.prepare()
        frozen = copy.deepcopy(self.project.read()["state"]["freeze"])
        for action, payload in [("freeze", {"protocol_artifact": "protocol"}), ("revise", {"contract": toy_contract(), "reason": "late change"})]:
            with self.subTest(action=action), self.assertRaises(GateError):
                self.project.apply(action, payload)
        manifest = self.run_manifest("late-development", phase="DEVELOPMENT")
        with self.assertRaises(GateError):
            self.project.apply("run", manifest)
        self.assertEqual(self.project.read()["state"]["freeze"], frozen)

    def test_freeze_rejects_missing_metadata_and_an_incomplete_matrix(self):
        for defect in ("commit", "matrix", "unobserved", "statistic"):
            with self.subTest(defect=defect):
                self.project = Project(self.base / defect)
                protocol = toy_protocol()
                if defect == "commit":
                    protocol["code"]["commit"] = "short"
                elif defect == "matrix":
                    protocol["expected_runs"].pop()
                elif defect == "unobserved":
                    protocol["protected_outcomes_unobserved"] = False
                else:
                    del protocol["statistics"]["uncertainty"]
                self.prepare(freeze=False, protocol=protocol)
                with self.assertRaises(GateError):
                    self.project.apply("freeze", {"protocol_artifact": "protocol"})
                self.assertEqual(self.project.read()["state"]["checkpoint"], 6)

    def test_confirmatory_receipts_match_exact_frozen_provenance(self):
        self.prepare()
        good = self.run_manifest("proposed")
        for key, value in [("source_commit", "c" * 40), ("seed", 8), ("variant", "baseline"), ("protocol_hash", "c" * 64), ("metrics", {"other": 1.0}), ("run_id", "unplanned")]:
            with self.subTest(key=key), self.assertRaises(GateError):
                self.project.apply("run", {**good, key: value})
        self.assertFalse(self.project.read()["state"]["runs"])
        self.project.apply("run", good)

    def test_nonfinite_metrics_are_rejected_and_attempt_retained(self):
        self.prepare()
        manifest = self.run_manifest("proposed")
        manifest["metrics"]["mse"] = float("nan")
        with self.assertRaises(GateError):
            self.project.apply("run", manifest)
        self.assertEqual(len(self.project.read()["state"]["rejections"]), 1)

    def test_missing_run_prevents_evidence_lock(self):
        self.prepare()
        self.project.apply("run", self.run_manifest("proposed"))
        with self.assertRaisesRegex(GateError, "missing"):
            self.project.apply("lock_evidence", {"disposition": "NEGATIVE", "scope": "fixture", "reason": "fixture"})

    def test_failed_runs_can_end_inconclusive_but_remain_retained(self):
        self.lock("INCONCLUSIVE", ("FAILED", "FAILED"))
        state = self.project.read()["state"]
        self.assertEqual(state["scientific_result"], "INCONCLUSIVE")
        self.assertTrue(all(run["status"] == "FAILED" for run in state["runs"].values()))

    def test_failed_runs_cannot_alone_be_promoted_to_negative(self):
        with self.assertRaisesRegex(GateError, "failed executions"):
            self.lock("NEGATIVE", ("FAILED", "FAILED"))

    def test_invalid_results_require_separate_invalid_closure(self):
        self.prepare()
        self.project.apply("run", self.run_manifest("proposed", "INVALID"))
        self.project.apply("run", self.run_manifest("baseline"))
        with self.assertRaisesRegex(GateError, "invalid evidence"):
            self.project.apply("lock_evidence", {"disposition": "NEGATIVE", "scope": "fixture", "reason": "fixture"})
        self.project.apply("close_invalid", {"reason": "Artificial invalid source", "report_artifact": "dry"})
        state = self.project.read()["state"]
        self.assertEqual(state["status"], "INVALID_CLOSED")
        self.assertNotEqual(state["checkpoint"], 10)
        self.assertEqual(state["runs"]["proposed"]["status"], "INVALID")

    def test_claim_requires_actual_run_raw_analysis_and_display_links(self):
        self.prepare()
        for arm in ("proposed", "baseline"):
            self.project.apply("run", self.run_manifest(arm))
        claim = self.claim()
        self.add("unrelated", "analysis", "unrelated fixture analysis")
        self.add("unlinked", "table", "unrelated fixture table")
        for change in ({"analysis_artifact": "unrelated"}, {"display_artifacts": ["unlinked"]}, {"phase": "DEVELOPMENT"}):
            with self.subTest(change=change), self.assertRaises(GateError):
                self.project.apply("claim", {**claim, **change})
        self.project.apply("claim", claim)

    def test_locked_evidence_rejects_extra_outcomes(self):
        self.lock()
        manifest = copy.deepcopy(self.project.read()["state"]["runs"]["proposed"])
        manifest["run_id"] = "late"
        with self.assertRaisesRegex(GateError, "locked"):
            self.project.apply("run", manifest)

    def test_independent_verification_requires_exact_evidence_and_checks(self):
        self.lock()
        self.add("paper", "paper", "ARTIFICIAL paper")
        for key, value in [("reviewer", "Fixture owner"), ("evidence_sha256", "f" * 64), ("checks", {key: False for key in VERIFY_CHECKS})]:
            with self.subTest(key=key):
                receipt = self.verification_receipt()
                receipt[key] = value
                artifact_id = "invalid-review-" + key
                self.add(artifact_id, "verification", receipt)
                with self.assertRaises(GateError):
                    self.project.apply("verify_review", {"verification_artifact": artifact_id})
        self.assertEqual(self.project.read()["state"]["checkpoint"], 8)

    def test_release_cannot_change_conclusion_or_skip_required_roles(self):
        self.lock()
        self.review()
        self.add("instructions", "other", "ARTIFICIAL instructions")
        release = self.release_manifest()
        release["disposition"] = "SUPPORTED"
        self.add("wrong-result", "release", release)
        with self.assertRaises(GateError):
            self.project.apply("complete", {"release_artifact": "wrong-result"})
        release = self.release_manifest()
        del release["roles"]["code"]
        self.add("missing-code", "release", release)
        with self.assertRaises(GateError):
            self.project.apply("complete", {"release_artifact": "missing-code"})
        self.assertEqual(self.project.read()["state"]["checkpoint"], 9)

    def test_successor_preserves_terminal_predecessor_exactly(self):
        self.finish()
        before = {str(path.relative_to(self.project.root)): path.read_bytes() for path in self.project.root.rglob("*") if path.is_file()}
        contract = toy_contract("artificial-successor")
        contract["hypothesis"] = "A materially different artificial mechanism is proposed."
        protocol = self.file(toy_protocol(contract), ".json")
        relationship = {"previous_finding": "Artificial negative result", "remaining_problem": "Artificial unresolved mechanism", "new_hypothesis": contract["hypothesis"], "material_difference": "A distinct fictional mechanism", "new_falsifier": "Independent fixture result"}
        target = self.base / "successor"
        created = self.project.successor(target, contract, relationship, protocol)
        self.assertEqual(created["state"]["checkpoint"], 0)
        self.assertEqual(created["state"]["predecessor"]["head"], self.project.read()["head"])
        after = {str(path.relative_to(self.project.root)): path.read_bytes() for path in self.project.root.rglob("*") if path.is_file()}
        self.assertEqual(before, after)
        self.assertIn("successor-protocol", created["state"]["artifacts"])

    def test_terminal_state_rejects_updates_without_rewriting_history(self):
        self.finish()
        before = self.project.path.read_bytes()
        with self.assertRaises(GateError):
            self.project.apply("note", {key: "late" for key in ("observation", "cause", "change", "prediction", "experiment", "result")})
        self.assertEqual(self.project.path.read_bytes(), before)

    def test_atomic_replacement_failure_preserves_old_state_and_cleans_staging(self):
        self.project.initialize(toy_contract())
        before = self.project.path.read_bytes()
        note = {key: "fixture" for key in ("observation", "cause", "change", "prediction", "experiment", "result")}
        for method in ("replace", "fsync"):
            with self.subTest(method=method), mock.patch(f"research_pipeline.ledger.os.{method}", side_effect=OSError("injected storage failure")):
                with self.assertRaises(OSError):
                    self.project.apply("note", note)
            self.assertEqual(self.project.path.read_bytes(), before)
            self.assertFalse(list(self.project.root.glob(".STATE-*")))
            self.project.read()

    def test_stale_writer_is_rejected_and_rejection_is_monotonic(self):
        self.project.initialize(toy_contract())
        stale = self.project.read()["head"]
        note = {key: "fixture" for key in ("observation", "cause", "change", "prediction", "experiment", "result")}
        self.project.apply("note", note)
        with self.assertRaisesRegex(GateError, "stale"):
            self.project.apply("note", note, expected_head=stale)
        self.assertEqual(len(self.project.read()["state"]["notes"]), 1)
        self.assertEqual(len(self.project.read()["state"]["rejections"]), 1)

    def test_two_processes_cannot_write_through_the_same_lock(self):
        self.project.initialize(toy_contract())
        note = self.file({key: "fixture" for key in ("observation", "cause", "change", "prediction", "experiment", "result")}, ".json")
        command = [sys.executable, "-m", "research_pipeline", "note", str(self.project.root), "--json", str(note)]
        before = self.project.path.read_bytes()
        with self.project._lock():
            blocked = subprocess.run(command, cwd=REPO, capture_output=True, text=True, timeout=10)
        self.assertEqual(blocked.returncode, 2)
        self.assertIn("BusyError", blocked.stderr)
        self.assertEqual(self.project.path.read_bytes(), before)
        admitted = subprocess.run(command, cwd=REPO, capture_output=True, text=True, timeout=10)
        self.assertEqual(admitted.returncode, 0, admitted.stderr)
        self.assertEqual(len(self.project.read()["state"]["notes"]), 1)

    def test_cli_init_verify_and_duplicate_keys(self):
        path = self.file(toy_contract(), ".json")
        init = subprocess.run([sys.executable, "-m", "research_pipeline", "init", str(self.project.root), "--contract", str(path)], cwd=REPO, capture_output=True, text=True, timeout=10)
        self.assertEqual(init.returncode, 0, init.stderr)
        verified = subprocess.run([sys.executable, "-m", "research_pipeline", "verify", str(self.project.root)], cwd=REPO, capture_output=True, text=True, timeout=10)
        self.assertTrue(json.loads(verified.stdout)["valid"])
        with self.assertRaises(GateError):
            strict_json('{"same": 1, "same": 2}')
        with self.assertRaises(GateError):
            strict_json('{"value": NaN}')
        with self.assertRaises(GateError):
            strict_json('{"value": 1e999}')

    def test_state_symlink_is_rejected(self):
        self.project.initialize(toy_contract())
        other = self.file(self.project.path.read_text())
        self.project.path.unlink()
        self.project.path.symlink_to(other)
        with self.assertRaises(IntegrityError):
            self.project.read()

    def test_contract_can_contain_the_markdown_ledger_delimiter(self):
        contract = toy_contract()
        contract["question"] += MARKER + "Literal scientific text, not the ledger."
        self.project.initialize(contract)
        self.assertEqual(self.project.read()["state"]["contract"], contract)
        self.project.apply("note", {key: "fixture" for key in ("observation", "cause", "change", "prediction", "experiment", "result")})
        self.assertEqual(self.project.read()["event_count"], 2)

    def test_direct_artifact_admission_cannot_commit_missing_or_mismatched_bytes(self):
        self.project.initialize(toy_contract())
        payload = {"artifact_id": "absent", "kind": "other", "sha256": "0" * 64, "bytes": 8, "source_name": "fictional", "parents": []}
        with self.assertRaisesRegex(GateError, "cannot read object"):
            self.project.apply("artifact", payload)
        self.assertFalse(self.project.read()["state"]["artifacts"])
        self.add("present", "other", "actual bytes")
        item = self.project.read()["state"]["artifacts"]["present"]
        with self.assertRaisesRegex(GateError, "identity mismatch"):
            self.project.apply("artifact", {**item, "artifact_id": "wrong-size", "bytes": item["bytes"] + 1})
        state = self.project.read()["state"]
        self.assertEqual(set(state["artifacts"]), {"present"})
        self.assertEqual(len(state["rejections"]), 2)

    def test_huge_integers_are_domain_errors_and_do_not_corrupt_state(self):
        contract = toy_contract()
        contract["compute_budget"]["seconds"] = 10 ** 1000
        with self.assertRaisesRegex(GateError, "finite"):
            self.project.initialize(contract)
        self.assertFalse(self.project.path.exists())
        self.prepare()
        good = self.run_manifest("proposed")
        for change in ({"runtime_seconds": 10 ** 1000}, {"metrics": {"mse": 10 ** 1000}}):
            with self.subTest(change=list(change)), self.assertRaisesRegex(GateError, "finite"):
                self.project.apply("run", {**good, **change})
        self.assertEqual(len(self.project.read()["state"]["rejections"]), 2)

    def test_every_declared_run_contributes_actual_evidence_to_the_claim(self):
        self.prepare()
        for arm in ("proposed", "baseline"):
            self.project.apply("run", self.run_manifest(arm))
        claim = self.claim(raw=["raw-proposed"])
        with self.assertRaisesRegex(GateError, "omits evidence from run baseline"):
            self.project.apply("claim", claim)
        self.assertFalse(self.project.read()["state"]["claims"])

    def test_supported_claim_cannot_replace_outcome_bytes_with_only_logs(self):
        self.prepare()
        for arm in ("proposed", "baseline"):
            self.project.apply("run", self.run_manifest(arm))
        with self.assertRaisesRegex(GateError, "omits evidence"):
            self.project.apply("claim", self.claim(raw=["log-proposed", "log-baseline"]))

    def test_supported_closure_requires_a_supported_confirmatory_statement(self):
        self.prepare()
        for arm in ("proposed", "baseline"):
            self.project.apply("run", self.run_manifest(arm))
        self.project.apply("claim", self.claim("UNSUPPORTED"))
        with self.assertRaisesRegex(GateError, "supported evidentiary"):
            self.project.apply("lock_evidence", {"disposition": "SUPPORTED", "scope": "fixture", "reason": "fixture"})

    def test_freeze_binds_the_qualified_protocol_architecture_and_code(self):
        for replacement in ("protocol", "architecture", "code"):
            with self.subTest(replacement=replacement):
                self.project = Project(self.base / replacement)
                protocol = toy_protocol()
                if replacement == "architecture":
                    protocol["architecture_artifact"] = "new-spec"
                elif replacement == "code":
                    protocol["code"]["artifact"] = "new-code"
                self.prepare(freeze=False, protocol=protocol)
                self.add("new-spec", "specification", "Unqualified artificial architecture")
                self.add("new-code", "code", "Unqualified artificial code")
                self.add("new-protocol", "protocol", protocol)
                selected = "new-protocol" if replacement == "protocol" else "protocol"
                with self.assertRaisesRegex(GateError, "qualified"):
                    self.project.apply("freeze", {"protocol_artifact": selected})
                self.assertEqual(self.project.read()["state"]["checkpoint"], 6)

    def test_budgets_count_failures_and_revisions_without_losing_overrun_receipts(self):
        self.prepare(freeze=False)
        for arm in ("development-a", "development-b"):
            manifest = self.run_manifest(arm, "FAILED", "DEVELOPMENT")
            manifest["runtime_seconds"] = 50
            self.project.apply("run", manifest)
        state = self.project.read()["state"]
        self.assertFalse(state["budget_accounting"]["blocked"])
        self.assertFalse(state["budget_accounting"]["can_plan_development_run"])
        self.assertEqual(state["budget_accounting"]["project_compute"]["remaining_seconds"], "0")
        third = self.run_manifest("development-c", "FAILED", "DEVELOPMENT")
        third["runtime_seconds"] = 1
        self.project.apply("run", third)
        with self.assertRaisesRegex(GateError, "budget overrun"):
            self.project.apply("freeze", {"protocol_artifact": "protocol"})
        self.project.apply("revise", {"contract": toy_contract(), "reason": "Unchanged budget cannot erase expenditures"})
        qualification = {"number": 1, "evidence": "spec", "reviewer": "Fixture", "note": "Fixture"}
        with self.assertRaisesRegex(GateError, "budget overrun"):
            self.project.apply("checkpoint", qualification)
        amended = toy_contract()
        amended["development_budget"]["max_runs"] = 5
        amended["compute_budget"]["seconds"] = 200
        self.project.apply("revise", {"contract": amended, "reason": "Explicit artificial budget amendment with prior spending retained"})
        self.project.apply("checkpoint", qualification)
        state = self.project.read()["state"]
        self.assertEqual(len(state["runs"]), 3)
        self.assertEqual(len(state["budget_overruns"]), 2)
        self.assertEqual(state["budget_accounting"]["development"]["remaining_runs"], 2)
        self.assertEqual(state["budget_accounting"]["project_compute"]["used_seconds"], "101")
        self.assertFalse(state["budget_accounting"]["blocked"])
        self.assertEqual(state["run_versions"], {arm: 1 for arm in ("development-a", "development-b", "development-c")})

    def test_frozen_overrun_is_retained_and_restricts_closure(self):
        self.prepare()
        for arm in ("proposed", "baseline"):
            manifest = self.run_manifest(arm)
            manifest["runtime_seconds"] = 6
            self.project.apply("run", manifest)
        self.project.apply("claim", self.claim())
        state = self.project.read()["state"]
        self.assertEqual(state["budget_accounting"]["confirmatory_compute"]["used_seconds"], "12")
        self.assertTrue(state["budget_accounting"]["blocked"])
        with self.assertRaisesRegex(GateError, "budget overrun"):
            self.project.apply("lock_evidence", {"disposition": "NEGATIVE", "scope": "fixture", "reason": "fixture"})
        self.project.apply("lock_evidence", {"disposition": "INCONCLUSIVE", "scope": "fixture", "reason": "Frozen resource restriction exceeded; no conclusive finding admitted."})
        self.assertEqual(len(self.project.read()["state"]["runs"]), 2)

    def test_frozen_compute_cap_must_fit_remaining_project_budget(self):
        self.prepare(freeze=False)
        manifest = self.run_manifest("development", "SUCCESS", "DEVELOPMENT")
        manifest["runtime_seconds"] = 95
        self.project.apply("run", manifest)
        with self.assertRaisesRegex(GateError, "remaining project"):
            self.project.apply("freeze", {"protocol_artifact": "protocol"})

    def test_large_finite_receipts_do_not_overflow_budget_accounting(self):
        self.prepare(freeze=False)
        revised = toy_contract()
        revised["compute_budget"]["seconds"] = 1e308
        self.project.apply("revise", {"contract": revised, "reason": "Artificial numeric-boundary fixture"})
        for arm in ("large-a", "large-b"):
            manifest = self.run_manifest(arm, "FAILED", "DEVELOPMENT")
            manifest["runtime_seconds"] = 1e308
            self.project.apply("run", manifest)
        state = self.project.read()["state"]
        self.assertEqual(len(state["runs"]), 2)
        self.assertTrue(state["budget_accounting"]["project_compute"]["overrun"])
        json.dumps(state, allow_nan=False)

    def test_explicit_invalid_closure_preserves_previously_locked_evidence(self):
        self.lock()
        locked = copy.deepcopy(self.project.read()["state"]["evidence_lock"])
        self.add("defect", "verification", "ARTIFICIAL later-discovered measurement defect")
        self.project.apply("close_invalid", {"reason": "Explicit withdrawal after validity defect", "report_artifact": "defect"})
        state = self.project.read()["state"]
        self.assertEqual(state["evidence_lock"], locked)
        self.assertEqual(state["scientific_result"], "INVALID")
        self.assertEqual(state["status"], "INVALID_CLOSED")
        self.assertNotEqual(state["checkpoint"], 10)

    def test_directory_fsync_failure_after_replace_reports_installed_state(self):
        self.project.initialize(toy_contract())
        before = self.project.read()["head"]
        note = {key: "fixture" for key in ("observation", "cause", "change", "prediction", "experiment", "result")}
        with mock.patch("research_pipeline.ledger._sync_directory", side_effect=OSError("injected directory fsync failure")):
            with self.assertRaisesRegex(OSError, "was installed"):
                self.project.apply("note", note)
        result = self.project.read()
        self.assertNotEqual(result["head"], before)
        self.assertEqual(len(result["state"]["notes"]), 1)
        self.assertFalse(list(self.project.root.glob(".STATE-*")))

    def test_object_fsync_failure_keeps_ledger_usable_and_retry_deduplicates(self):
        self.project.initialize(toy_contract())
        before = self.project.path.read_bytes()
        source = self.file("retained orphan after injected storage error")
        with mock.patch("research_pipeline.ledger._sync_directory", side_effect=OSError("injected object directory failure")):
            with self.assertRaises(OSError):
                self.project.add_artifact("source", "other", source)
        self.assertEqual(self.project.path.read_bytes(), before)
        self.assertFalse(list((self.project.root / ".research" / "objects").glob(".object-*")))
        self.project.add_artifact("source", "other", source)
        self.assertEqual(len(self.project.read()["state"]["artifacts"]), 1)

    def test_object_store_directory_and_leaf_symlinks_are_rejected(self):
        for level in ("parent", "leaf"):
            with self.subTest(level=level):
                self.project = Project(self.base / level)
                self.project.initialize(toy_contract())
                self.add("source", "other", "original bytes")
                item = self.project.read()["state"]["artifacts"]["source"]
                if level == "parent":
                    location = self.project.root / ".research"
                    moved = self.base / "moved-store"
                    location.rename(moved)
                    location.symlink_to(moved, target_is_directory=True)
                else:
                    location = self.project.root / ".research" / "objects" / item["sha256"]
                    location.unlink()
                    location.symlink_to(self.file("original bytes"))
                with self.assertRaises(IntegrityError):
                    self.project.read()

    def test_terminal_artifact_registration_does_not_write_even_an_orphan(self):
        self.finish()
        before = {str(path.relative_to(self.project.root)): path.read_bytes() for path in self.project.root.rglob("*") if path.is_file()}
        with self.assertRaises(GateError):
            self.add("late", "other", "previously unseen late fixture bytes")
        after = {str(path.relative_to(self.project.root)): path.read_bytes() for path in self.project.root.rglob("*") if path.is_file()}
        self.assertEqual(before, after)

    def test_nonregular_or_empty_artifact_sources_retain_rejected_attempts(self):
        self.project.initialize(toy_contract())
        for source in (self.base, self.file("")):
            with self.subTest(source=source.name), self.assertRaises(GateError):
                self.project.add_artifact("invalid", "other", source)
        state = self.project.read()["state"]
        self.assertFalse(state["artifacts"])
        self.assertEqual(len(state["rejections"]), 2)
        self.assertFalse(list(self.project.root.rglob(".object-*")))

    def test_validity_correction_preserves_hypothesis_and_invalid_predecessor(self):
        self.prepare()
        self.project.apply("run", self.run_manifest("proposed", "INVALID"))
        self.project.apply("close_invalid", {"reason": "ARTIFICIAL metric defect", "report_artifact": "dry"})
        before = {str(path.relative_to(self.project.root)): path.read_bytes() for path in self.project.root.rglob("*") if path.is_file()}
        contract = toy_contract("artificial-correction")
        protocol = toy_protocol(contract)
        protocol["version"] = "artificial-corrected-v2"
        protocol["code"]["commit"] = "c" * 40
        relationship = {"previous_finding": "INVALID artificial metric", "validity_defect": "Invented metric indexing defect", "repair": "Correct the declared code and metric implementation", "affected_work": "Both artificial arms", "justification": "Retest the unchanged hypothesis after a validity repair"}
        result = self.project.successor(self.base / "corrected", contract, relationship, self.file(protocol), validity_correction=True)
        self.assertEqual(result["state"]["contract"]["hypothesis"], toy_contract()["hypothesis"])
        self.assertEqual(result["state"]["predecessor"]["relationship_kind"], "VALIDITY_CORRECTION")
        self.assertEqual(result["state"]["checkpoint"], 0)
        after = {str(path.relative_to(self.project.root)): path.read_bytes() for path in self.project.root.rglob("*") if path.is_file()}
        self.assertEqual(before, after)

    def test_validity_correction_rejects_a_valid_completed_predecessor(self):
        self.finish()
        contract = toy_contract("invalid-correction-request")
        relationship = {key: "ARTIFICIAL" for key in ("previous_finding", "validity_defect", "repair", "affected_work", "justification")}
        before = self.project.path.read_bytes()
        with self.assertRaisesRegex(GateError, "invalid predecessor"):
            self.project.successor(self.base / "forbidden", contract, relationship, self.file(toy_protocol(contract)), validity_correction=True)
        self.assertEqual(self.project.path.read_bytes(), before)
        self.assertFalse((self.base / "forbidden" / "STATE.md").exists())

    def test_validity_correction_requires_a_changed_protocol_identity(self):
        self.prepare()
        state = self.project.read()["state"]
        protocol_bytes = (self.project.root / ".research" / "objects" / state["freeze"]["sha256"]).read_text()
        self.project.apply("close_invalid", {"reason": "ARTIFICIAL defect", "report_artifact": "dry"})
        relationship = {key: "ARTIFICIAL" for key in ("previous_finding", "validity_defect", "repair", "affected_work", "justification")}
        with self.assertRaisesRegex(GateError, "changed protocol identity"):
            self.project.successor(self.base / "unchanged", toy_contract("artificial-corrected"), relationship, self.file(protocol_bytes), validity_correction=True)

    def test_ordinary_successor_cannot_relabel_the_same_hypothesis(self):
        self.finish()
        contract = toy_contract("same-hypothesis")
        relationship = {key: "ARTIFICIAL" for key in ("previous_finding", "remaining_problem", "material_difference", "new_falsifier")}
        relationship["new_hypothesis"] = contract["hypothesis"]
        with self.assertRaisesRegex(GateError, "materially different"):
            self.project.successor(self.base / "same", contract, relationship, self.file(toy_protocol(contract)))

    def test_successor_cannot_add_files_inside_the_preserved_predecessor(self):
        self.finish()
        contract = toy_contract("nested-successor")
        contract["hypothesis"] = "Materially different artificial hypothesis"
        relationship = {key: "ARTIFICIAL" for key in ("previous_finding", "remaining_problem", "material_difference", "new_falsifier")}
        relationship["new_hypothesis"] = contract["hypothesis"]
        for target in (self.project.root / "child", self.project.root.parent):
            with self.subTest(target=target), self.assertRaisesRegex(GateError, "without nesting"):
                self.project.successor(target, contract, relationship, self.file(toy_protocol(contract)))
        self.assertFalse((self.project.root / "child").exists())

    def test_nonregular_retained_object_fails_promptly_instead_of_blocking(self):
        self.project.initialize(toy_contract())
        self.add("source", "other", "regular initial object")
        item = self.project.read()["state"]["artifacts"]["source"]
        path = self.project.root / ".research" / "objects" / item["sha256"]
        path.unlink()
        os.mkfifo(path)
        result = subprocess.run([sys.executable, "-m", "research_pipeline", "verify", str(self.project.root)], cwd=REPO, capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 2)
        self.assertIn("not a regular file", result.stderr)

    def test_executable_artificial_demo_and_cli_verification(self):
        target = self.base / "complete-demo"
        command = [sys.executable, "-m", "research_pipeline.demo", "--output", str(target)]
        example = subprocess.run(command, cwd=REPO, capture_output=True, text=True, timeout=20)
        self.assertEqual(example.returncode, 0, example.stderr)
        receipt = json.loads(example.stdout)
        self.assertTrue(receipt["artificial_fixture"])
        self.assertEqual(receipt["checkpoint"], 10)
        self.assertEqual(receipt["disposition"], "NEGATIVE")
        verified = subprocess.run([sys.executable, "-m", "research_pipeline", "verify", str(target / "study"), "--expected-head", receipt["head"]], cwd=REPO, capture_output=True, text=True, timeout=10)
        self.assertEqual(verified.returncode, 0, verified.stderr)
        self.assertTrue(json.loads(verified.stdout)["valid"])
        before = (target / "study" / "STATE.md").read_bytes()
        second = subprocess.run(command, cwd=REPO, capture_output=True, text=True, timeout=20)
        self.assertEqual(second.returncode, 2)
        self.assertEqual((target / "study" / "STATE.md").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
