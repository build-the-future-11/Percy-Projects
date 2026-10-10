"""Generate an explicitly artificial, complete ledger fixture; run no research."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .ledger import RELEASE_REVIEWS, VERIFY_CHECKS, Project


def build_fixture(output):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    inputs = output / "inputs"
    inputs.mkdir()
    project = Project(output / "study")

    def write(name, value):
        path = inputs / name
        path.write_text(json.dumps(value, indent=2) + "\n" if isinstance(value, (dict, list)) else value, encoding="utf-8")
        return path

    def artifact(name, kind, value, parents=()):
        project.add_artifact(name, kind, write(name + ".txt", value), parents)

    contract = {
        "project_id": "artificial-negative-example", "title": "ARTIFICIAL lifecycle demonstration",
        "owner": "Fictional fixture author", "question": "Does fictional arm P improve the fixture score?",
        "objective": "Demonstrate artifact retention and all ten software gates.",
        "hypothesis": "Fictional arm P lowers the fixture score relative to B.",
        "contribution": "No scientific contribution: these are artificial software fixtures.",
        "scope": "Two invented receipts, without training, evaluation, real datasets, or scientific inference.",
        "development_budget": {"max_runs": 2},
        "compute_budget": {"seconds": 60, "description": "ARTIFICIAL receipt accounting; no scientific compute"},
        "protected_boundary": "No protected scientific outcomes exist in this fixture.",
        "repositories": ["https://example.invalid/artificial-fixture"], "datasets": ["fixture"],
        "known_history": ["Every receipt and reviewer name in this example is fictional."],
        "definition_of_done": "Exercise the software gates while retaining the artificial adverse outcome.",
        "next_action": "Inspect the generated state and inputs; do not cite them as scientific evidence.",
    }
    project.initialize(contract)
    write("contract.json", contract)
    artifact("spec", "specification", "ARTIFICIAL specification: compare invented scores 2 and 1. No model is implemented here.")
    artifact("code", "code", "ARTIFICIAL code receipt. The repeated-a commit is fictional and is not a verified Git revision.")
    artifact("config", "config", {"artificial_fixture": True, "parameters": {}})
    artifact("data", "dataset", "ARTIFICIAL fixture values only; no real dataset.")
    artifact("split", "split", {"artificial_fixture": True, "training": [], "development": [], "protected": ["invented-pair"]})
    artifact("env", "environment", {"artificial_fixture": True, "description": "Fictional runner receipt, no scientific execution"})
    artifact("dry", "verification", "ARTIFICIAL qualification receipt, no research verification performed.")
    protocol = {
        "version": "artificial-v1", "question": contract["question"], "hypothesis": contract["hypothesis"],
        "code": {"repository": contract["repositories"][0], "commit": "a" * 40, "artifact": "code"},
        "architecture_artifact": "spec",
        "datasets": [{"id": "fixture", "version": "artificial-1", "license": "Artificial values authored by this demonstration", "artifact": "data", "split_artifact": "split"}],
        "baselines": ["baseline"], "hyperparameters": {}, "metrics": ["score"], "primary_endpoint": "score",
        "direction": "lower", "practical_effect_threshold": 0.1,
        "statistics": {"procedure": "Invented paired difference", "uncertainty": "No scientific uncertainty inference", "aggregation": "Single invented pair", "multiplicity": "Single fixture comparison", "decision_rule": "Invented P score must be smaller than B"},
        "seeds": [7], "independent_unit": "One artificial receipt pair",
        "exclusion_rules": "Retain both invented receipts", "stopping_rules": "Exactly two invented receipts",
        "environment_artifact": "env", "compute_protocol": {"hardware": "Fictional CPU", "max_seconds": 10, "measurement": "Invented runtime field"},
        "expected_runs": [{"run_id": arm, "seed": 7, "variant": arm, "dataset_id": "fixture", "config_artifact": "config"} for arm in ("proposed", "baseline")],
        "protected_boundary": contract["protected_boundary"], "protected_outcomes_unobserved": True,
    }
    artifact("protocol", "protocol", protocol)
    write("protocol.json", protocol)
    for number, evidence in enumerate(("spec", "spec", "protocol", "code", "code", "dry"), start=1):
        project.apply("checkpoint", {"number": number, "evidence": evidence,
                                     "reviewer": "Fictional fixture reviewer", "note": "ARTIFICIAL attestation; not actual scientific review."})
    project.apply("freeze", {"protocol_artifact": "protocol"})
    for arm, value in (("proposed", 2), ("baseline", 1)):
        artifact("raw-" + arm, "raw", {"artificial_fixture": True, "score": value})
        artifact("log-" + arm, "log", "ARTIFICIAL receipt; no process was executed.")
        receipt = {
            "run_id": arm, "phase": "CONFIRMATORY", "status": "SUCCESS", "source_commit": "a" * 40,
            "config_artifact": "config", "dataset_artifact": "data", "split_artifact": "split", "environment_artifact": "env",
            "seed": 7, "variant": arm, "runtime_seconds": 0, "peak_memory_bytes": 0,
            "compute": {"artificial_fixture": True, "scientific_jobs_executed": 0}, "metrics": {"score": value},
            "raw_artifacts": ["raw-" + arm], "log_artifacts": ["log-" + arm], "failure_reason": None, "deviations": [],
            "protocol_hash": project.read()["state"]["freeze"]["sha256"],
        }
        write("run-" + arm + ".json", receipt)
        project.apply("run", receipt)
    artifact("analysis", "analysis", {"artificial_fixture": True, "invented_difference": 1}, ["raw-proposed", "raw-baseline"])
    artifact("table", "table", "ARTIFICIAL table: P=2, B=1; P is worse in the invented pair.", ["analysis"])
    claim = {
        "claim_id": "artificial-adverse-finding", "text": "The invented proposed score is higher by 1.",
        "scope": "This artificial software fixture only", "status": "SUPPORTED",
        "limitations": "No real experiment, independent units, or statistical evidence.",
        "uncertainty": "No scientific uncertainty estimate", "paper_location": "Artificial table",
        "phase": "CONFIRMATORY", "run_ids": ["proposed", "baseline"], "raw_artifacts": ["raw-proposed", "raw-baseline"],
        "analysis_artifact": "analysis", "display_artifacts": ["table"],
    }
    write("claim.json", claim)
    project.apply("claim", claim)
    conclusion = {"disposition": "NEGATIVE", "scope": "This artificial software fixture only", "reason": "The invented outcome fails the fictional hypothesis. This is a fixture classification, not a research finding."}
    write("conclusion.json", conclusion)
    project.apply("lock_evidence", conclusion)
    artifact("paper", "paper", "ARTIFICIAL paper receipt: fictional proposed=2, baseline=1. No scientific result is claimed.", ["analysis", "table"])
    review = {
        "reviewer": "Fictional independent fixture reviewer", "evidence_sha256": project.read()["state"]["evidence_lock"]["sha256"],
        "paper_artifact": "paper", "environment_artifact": "env", "checks": {key: True for key in VERIFY_CHECKS},
        "reproduction_command": "python -m research_pipeline.demo --output A_NEW_EMPTY_PATH",
        "limits": "ARTIFICIAL attestations. No independent scientific verification was performed; boolean values exercise software gates only.",
    }
    artifact("review", "verification", review)
    write("review.json", review)
    project.apply("verify_review", {"verification_artifact": "review"})
    artifact("instructions", "other", "Reproduce this artificial ledger fixture using python -m research_pipeline.demo; it executes no research.")
    release = {
        "release_commit": "b" * 40, "disposition": conclusion["disposition"], "scope": conclusion["scope"],
        "evidence_sha256": project.read()["state"]["evidence_lock"]["sha256"],
        "roles": {"paper": "paper", "code": "code", "configuration": ["config"], "environment": "env", "reproduction": "instructions", "data_instructions": "instructions"},
        "reviews": {key: {"not_applicable": "Artificial software fixture; no scientific release or submission is being made."} for key in RELEASE_REVIEWS},
    }
    artifact("release", "release", release)
    write("release.json", release)
    result = project.apply("complete", {"release_artifact": "release"})
    return {"artificial_fixture": True, "project": str(project.root), "head": result["head"],
            "checkpoint": result["state"]["checkpoint"], "disposition": result["state"]["scientific_result"],
            "warning": "Generated fictional receipts demonstrate software only. They do not complete or verify any real research project."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="A new directory; existing paths are never overwritten")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(build_fixture(args.output), indent=2))
    except (OSError, ValueError) as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
