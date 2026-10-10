from __future__ import annotations

import copy
import fcntl
import hashlib
import json
import math
import os
import re
import stat
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

CHECKPOINTS = (
    "INITIALIZED", "IDEA READY", "MODEL SPECIFICATION READY", "METHODOLOGY READY",
    "MODEL IMPLEMENTED", "EXPERIMENT SYSTEM IMPLEMENTED", "RUN READY",
    "CONFIRMATORY PROTOCOL FROZEN", "EVIDENCE LOCKED", "VERIFIED", "RESEARCH COMPLETE",
)
OUTCOMES = {"SUPPORTED", "MIXED", "NEGATIVE", "INCONCLUSIVE"}
KINDS = {"specification", "protocol", "code", "config", "dataset", "split", "environment",
         "raw", "log", "analysis", "figure", "table", "paper", "verification", "release", "other"}
POST_FREEZE_KINDS = {"raw", "log", "analysis", "figure", "table", "paper", "verification", "release", "other"}
CONTRACT_KEYS = {"project_id", "title", "owner", "question", "objective", "hypothesis", "contribution",
                 "scope", "development_budget", "compute_budget", "protected_boundary", "repositories",
                 "datasets", "known_history", "definition_of_done", "next_action"}
PROTOCOL_KEYS = {"version", "question", "hypothesis", "code", "architecture_artifact", "datasets",
                 "baselines", "hyperparameters", "metrics", "primary_endpoint", "direction",
                 "practical_effect_threshold", "statistics", "seeds", "independent_unit",
                 "exclusion_rules", "stopping_rules", "environment_artifact", "compute_protocol",
                 "expected_runs", "protected_boundary", "protected_outcomes_unobserved"}
RUN_KEYS = {"run_id", "phase", "status", "source_commit", "config_artifact", "dataset_artifact",
            "split_artifact", "environment_artifact", "seed", "variant", "runtime_seconds",
            "peak_memory_bytes", "compute", "metrics", "raw_artifacts", "log_artifacts",
            "failure_reason", "deviations", "protocol_hash"}
CLAIM_KEYS = {"claim_id", "text", "scope", "status", "limitations", "uncertainty", "paper_location",
              "phase", "run_ids", "raw_artifacts", "analysis_artifact", "display_artifacts"}
VERIFY_CHECKS = {"build", "tests", "reproduction", "figures", "tables", "paper_numbers",
                 "mathematics", "citations", "claim_scope"}
RELEASE_ROLES = {"paper", "code", "configuration", "environment", "reproduction", "data_instructions"}
RELEASE_REVIEWS = {"bibliography", "supplement", "authorship", "licensing", "ethics", "venue", "arxiv", "submission"}
MARKER = "\n## Canonical event ledger\n\n```json\n"


class GateError(ValueError):
    """The requested scientific-state transition is not admitted."""


class IntegrityError(ValueError):
    """Existing state or retained object bytes do not match their identities."""


class BusyError(RuntimeError):
    """Another cooperating process holds the project write lock."""


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def strict_json(text: str):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise GateError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def constant(value):
        raise GateError(f"non-finite JSON value: {value}")

    def floating(value):
        parsed = float(value)
        if not math.isfinite(parsed):
            raise GateError(f"out-of-range JSON number: {value}")
        return parsed

    try:
        return json.loads(text, object_pairs_hook=pairs, parse_constant=constant, parse_float=floating)
    except json.JSONDecodeError as exc:
        raise GateError(f"invalid JSON: {exc}") from exc


def _require(condition, message):
    if not condition:
        raise GateError(message)


def _text(value, label):
    _require(isinstance(value, str) and bool(value.strip()), f"{label} must be nonempty text")
    return value


def _keys(value, required, label):
    _require(isinstance(value, dict) and set(value) == set(required), f"{label} fields must be exactly {sorted(required)}")


def _finite(value):
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _number(value, label, *, integer=False, positive=False):
    ok = type(value) is int if integer else type(value) in (int, float)
    _require(ok and _finite(value) and (value > 0 if positive else value >= 0), f"{label} must be finite and {'positive' if positive else 'nonnegative'}")


def _seconds_text(value):
    # Compare exact rational values; round only the human-readable projection.
    with localcontext() as context:
        context.prec = 20
        return str(Decimal(value.numerator) / Decimal(value.denominator))


def _budgets(state):
    runs = list(state["runs"].values())
    count = sum(run["phase"] == "DEVELOPMENT" for run in runs)
    max_runs = state["contract"]["development_budget"]["max_runs"]

    def seconds_budget(selected, limit):
        used = sum((Fraction(run["runtime_seconds"]) for run in selected), Fraction())
        limit = Fraction(limit)
        return {"used_seconds": _seconds_text(used), "limit_seconds": _seconds_text(limit),
                "remaining_seconds": _seconds_text(max(limit - used, Fraction())), "overrun": used > limit}

    result = {"development": {"used_runs": count, "limit_runs": max_runs,
                              "remaining_runs": max(max_runs - count, 0), "overrun": count > max_runs},
              "project_compute": seconds_budget(runs, state["contract"]["compute_budget"]["seconds"]),
              "confirmatory_compute": None}
    if state["freeze"]:
        result["confirmatory_compute"] = seconds_budget(
            [run for run in runs if run["phase"] == "CONFIRMATORY"],
            state["freeze"]["protocol"]["compute_protocol"]["max_seconds"])
    result["blocked"] = any(item and item["overrun"] for item in result.values())
    result["can_plan_development_run"] = (state["status"] == "ACTIVE" and state["freeze"] is None
                                          and not result["blocked"] and count < max_runs
                                          and Fraction(state["contract"]["compute_budget"]["seconds"])
                                          > sum((Fraction(run["runtime_seconds"]) for run in runs), Fraction()))
    return result


def _sync_directory(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _strings(value, label, *, nonempty=True):
    _require(isinstance(value, list) and (value or not nonempty), f"{label} must be a list")
    for item in value:
        _text(item, label)
    _require(len(set(value)) == len(value), f"{label} contains duplicates")


def _sha(value, label, length=64):
    _require(isinstance(value, str) and re.fullmatch(f"[0-9a-f]{{{length}}}", value), f"{label} must be a full {length}-character lowercase hex identity")


def _contract(contract):
    _keys(contract, CONTRACT_KEYS, "contract")
    for key in CONTRACT_KEYS - {"development_budget", "compute_budget", "repositories", "datasets", "known_history"}:
        _text(contract[key], key)
    _require(re.fullmatch(r"[a-z0-9][a-z0-9_-]*", contract["project_id"]), "project_id must be a slug")
    _keys(contract["development_budget"], {"max_runs"}, "development_budget")
    _number(contract["development_budget"]["max_runs"], "max_runs", integer=True)
    _keys(contract["compute_budget"], {"seconds", "description"}, "compute_budget")
    _number(contract["compute_budget"]["seconds"], "compute seconds")
    _text(contract["compute_budget"]["description"], "compute description")
    _strings(contract["repositories"], "repositories")
    _strings(contract["datasets"], "datasets", nonempty=False)
    _strings(contract["known_history"], "known_history", nonempty=False)


def _artifact(state, artifact_id, kinds=None):
    _require(artifact_id in state["artifacts"], f"unknown artifact: {artifact_id}")
    item = state["artifacts"][artifact_id]
    if kinds:
        _require(item["kind"] in kinds, f"artifact {artifact_id} must have kind {sorted(kinds)}")
    return item


def _artifact_list(state, ids, kinds, label, *, nonempty=True):
    _strings(ids, label, nonempty=nonempty)
    for artifact_id in ids:
        _artifact(state, artifact_id, kinds)


def _object_path(root, sha):
    for parent in (root / ".research", root / ".research" / "objects"):
        if parent.is_symlink():
            raise IntegrityError("object-store directories cannot be symlinks")
    return root / ".research" / "objects" / sha


def _verify_object(root, item, *, capture=False):
    path = _object_path(root, item["sha256"])
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, "rb") as handle:
            mode = os.fstat(handle.fileno()).st_mode
            if not stat.S_ISREG(mode):
                raise IntegrityError(f"object is not a regular file: {path.name}")
            sha = hashlib.sha256()
            size = 0
            chunks = [] if capture else None
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                sha.update(chunk)
                size += len(chunk)
                if chunks is not None:
                    chunks.append(chunk)
    except OSError as exc:
        raise IntegrityError(f"cannot read object {path.name}: {exc}") from exc
    if sha.hexdigest() != item["sha256"] or size != item["bytes"]:
        raise IntegrityError(f"object identity mismatch: {path.name}")
    return b"".join(chunks) if chunks is not None else None


def _artifact_json(root, state, artifact_id, kinds):
    item = _artifact(state, artifact_id, kinds)
    # Decode the verified descriptor's bytes, never a second path read that
    # could refer to a different object after concurrent replacement.
    raw = _verify_object(root, item, capture=True)
    return strict_json(raw.decode("utf-8"))


def _protocol(root, state, protocol):
    _keys(protocol, PROTOCOL_KEYS, "protocol")
    for key in ("version", "independent_unit", "exclusion_rules", "stopping_rules"):
        _text(protocol[key], key)
    for key in ("question", "hypothesis", "protected_boundary"):
        _require(protocol[key] == state["contract"][key], f"protocol {key} differs from the current contract")
    _require(protocol["protected_outcomes_unobserved"] is True, "freeze requires an explicit unobserved-protected-outcomes attestation")
    _keys(protocol["code"], {"repository", "commit", "artifact"}, "code")
    _require(protocol["code"]["repository"] in state["contract"]["repositories"], "code repository is outside the project contract")
    _sha(protocol["code"]["commit"], "code commit", 40)
    _artifact(state, protocol["code"]["artifact"], {"code"})
    _artifact(state, protocol["architecture_artifact"], {"specification"})
    _artifact(state, protocol["environment_artifact"], {"environment"})
    datasets = protocol["datasets"]
    _require(isinstance(datasets, list) and datasets, "datasets must be a nonempty list")
    dataset_ids = set()
    for item in datasets:
        _keys(item, {"id", "version", "license", "artifact", "split_artifact"}, "dataset")
        for key in ("id", "version", "license"):
            _text(item[key], f"dataset {key}")
        _require(item["id"] not in dataset_ids, "duplicate dataset identity")
        dataset_ids.add(item["id"])
        _artifact(state, item["artifact"], {"dataset"})
        _artifact(state, item["split_artifact"], {"split"})
    _strings(protocol["baselines"], "baselines")
    _require("proposed" not in protocol["baselines"], "proposed is reserved for the tested arm")
    _require(isinstance(protocol["hyperparameters"], dict), "hyperparameters must be an explicit object")
    canonical(protocol["hyperparameters"])
    _strings(protocol["metrics"], "metrics")
    _require(protocol["primary_endpoint"] in protocol["metrics"], "primary_endpoint must be a declared metric")
    _require(protocol["direction"] in {"lower", "higher"}, "metric direction must be lower or higher")
    _number(protocol["practical_effect_threshold"], "practical_effect_threshold")
    _keys(protocol["statistics"], {"procedure", "uncertainty", "aggregation", "multiplicity", "decision_rule"}, "statistics")
    for key, value in protocol["statistics"].items():
        _text(value, key)
    seeds = protocol["seeds"]
    _require(isinstance(seeds, list) and seeds, "seeds must be a nonempty list")
    for seed in seeds:
        _number(seed, "seed", integer=True)
    _require(len(set(seeds)) == len(seeds), "duplicate seeds")
    _keys(protocol["compute_protocol"], {"hardware", "max_seconds", "measurement"}, "compute_protocol")
    _text(protocol["compute_protocol"]["hardware"], "hardware")
    _text(protocol["compute_protocol"]["measurement"], "measurement")
    _number(protocol["compute_protocol"]["max_seconds"], "max_seconds", positive=True)
    expected = protocol["expected_runs"]
    _require(isinstance(expected, list) and expected, "expected_runs must be a nonempty list")
    ids, cells = set(), set()
    for run in expected:
        _keys(run, {"run_id", "seed", "variant", "dataset_id", "config_artifact"}, "expected run")
        _text(run["run_id"], "run_id")
        _require(run["run_id"] not in ids and run["run_id"] not in state["runs"], "expected run ID is reused")
        _require(type(run["seed"]) is int and run["seed"] in seeds, "expected run seed is undeclared")
        _require(run["variant"] in ["proposed"] + protocol["baselines"], "expected run variant is undeclared")
        _require(run["dataset_id"] in dataset_ids, "expected run dataset is undeclared")
        _artifact(state, run["config_artifact"], {"config"})
        cell = (run["seed"], run["variant"], run["dataset_id"])
        _require(cell not in cells, "duplicate expected matrix cell")
        ids.add(run["run_id"])
        cells.add(cell)
    required_cells = {(seed, arm, data) for seed in seeds for arm in ["proposed"] + protocol["baselines"] for data in dataset_ids}
    _require(cells == required_cells, "expected matrix must cover every declared seed x variant x dataset")


def _run(root, state, run):
    _keys(run, RUN_KEYS, "run manifest")
    _text(run["run_id"], "run_id")
    _require(run["run_id"] not in state["runs"], "run_id is immutable, including failed attempts")
    _require(state["checkpoint"] < 8, "evidence is locked; new outcomes need a successor")
    _require(run["phase"] in {"DEVELOPMENT", "CONFIRMATORY"}, "run phase is invalid")
    _require(run["status"] in {"SUCCESS", "FAILED", "INVALID"}, "run status is invalid")
    _sha(run["source_commit"], "source_commit", 40)
    for key, kind in (("config_artifact", "config"), ("dataset_artifact", "dataset"), ("split_artifact", "split"), ("environment_artifact", "environment")):
        _artifact(state, run[key], {kind})
    _number(run["seed"], "seed", integer=True)
    _text(run["variant"], "variant")
    _number(run["runtime_seconds"], "runtime_seconds")
    _number(run["peak_memory_bytes"], "peak_memory_bytes", integer=True)
    _require(isinstance(run["compute"], dict) and run["compute"], "compute measurement must be explicit")
    canonical(run["compute"])
    _require(isinstance(run["metrics"], dict), "metrics must be an object")
    for key, value in run["metrics"].items():
        _text(key, "metric name")
        _require(_finite(value), "metrics must be finite real numbers")
    _artifact_list(state, run["raw_artifacts"], {"raw"}, "raw_artifacts", nonempty=run["status"] == "SUCCESS")
    _artifact_list(state, run["log_artifacts"], {"log"}, "log_artifacts")
    _strings(run["deviations"], "deviations", nonempty=False)
    if run["status"] == "SUCCESS":
        _require(run["metrics"] and run["failure_reason"] is None, "success requires metrics and no failure_reason")
    else:
        _text(run["failure_reason"], "failure_reason")
    if run["phase"] == "DEVELOPMENT":
        _require(state["freeze"] is None, "development is closed after freeze")
        _require(run["protocol_hash"] is None, "development may not impersonate a frozen protocol")
    else:
        _require(state["freeze"] is not None, "confirmation requires a frozen protocol")
        frozen = state["freeze"]
        protocol = frozen["protocol"]
        _require(run["protocol_hash"] == frozen["sha256"], "run protocol hash differs from freeze")
        expected = next((item for item in protocol["expected_runs"] if item["run_id"] == run["run_id"]), None)
        _require(expected is not None, "run is outside the frozen matrix")
        data = next(item for item in protocol["datasets"] if item["id"] == expected["dataset_id"])
        required = {"source_commit": protocol["code"]["commit"], "config_artifact": expected["config_artifact"],
                    "dataset_artifact": data["artifact"], "split_artifact": data["split_artifact"],
                    "environment_artifact": protocol["environment_artifact"], "seed": expected["seed"], "variant": expected["variant"]}
        for key, value in required.items():
            _require(run[key] == value, f"run {key} differs from frozen provenance")
        if run["status"] == "SUCCESS":
            _require(set(run["metrics"]) == set(protocol["metrics"]), "successful confirmation must retain all declared metrics")


def _claim(state, claim):
    _keys(claim, CLAIM_KEYS, "claim")
    for key in ("claim_id", "text", "scope", "limitations", "uncertainty", "paper_location"):
        _text(claim[key], key)
    _require(claim["claim_id"] not in state["claims"], "claim_id is immutable; revisions need a new ID")
    _require(state["checkpoint"] < 8, "claims are locked")
    _require(claim["status"] in {"SUPPORTED", "PARTIALLY_SUPPORTED", "UNSUPPORTED", "REJECTED"}, "invalid claim status")
    _require(claim["phase"] in {"DEVELOPMENT", "CONFIRMATORY"}, "invalid claim phase")
    _strings(claim["run_ids"], "run_ids")
    raw = set()
    for run_id in claim["run_ids"]:
        _require(run_id in state["runs"], f"unknown run: {run_id}")
        run = state["runs"][run_id]
        _require(run["phase"] == claim["phase"], "claim mixes scientific phases")
        _require(run["status"] != "INVALID", "invalid run cannot support a claim")
        if claim["status"] in {"SUPPORTED", "PARTIALLY_SUPPORTED"}:
            _require(run["status"] == "SUCCESS", "a supported claim requires successful valid evidence")
            eligible = run["raw_artifacts"]
        else:
            eligible = run["raw_artifacts"] + run["log_artifacts"]
        _require(set(claim["raw_artifacts"]) & set(eligible), f"claim omits evidence from run {run_id}")
        raw.update(run["raw_artifacts"] + run["log_artifacts"])
    _artifact_list(state, claim["raw_artifacts"], {"raw", "log"}, "raw_artifacts")
    _require(set(claim["raw_artifacts"]) <= raw, "claim raw artifacts are not from its runs")
    analysis = _artifact(state, claim["analysis_artifact"], {"analysis"})
    _require(set(claim["raw_artifacts"]) <= set(analysis["parents"]), "analysis does not trace to every claimed raw artifact")
    _artifact_list(state, claim["display_artifacts"], {"figure", "table"}, "display_artifacts")
    for artifact_id in claim["display_artifacts"]:
        _require(claim["analysis_artifact"] in _artifact(state, artifact_id)["parents"], "figure/table does not trace to the claim analysis")


def _seal_evidence(state, conclusion, *, previous_seal=None):
    """Bind retained bytes and study identity, not just reusable artifact IDs."""
    manifest = copy.deepcopy({
        "schema_version": 2, "contract": state["contract"], "study_version": state["version"],
        "freeze": state["freeze"], "artifacts": state["artifacts"],
        "runs": state["runs"], "run_versions": state["run_versions"],
        "claims": state["claims"], "claim_versions": state["claim_versions"],
        "qualifications": state["qualifications"], "conclusion": conclusion,
        "predecessor": state["predecessor"],
        "previous_seal": previous_seal,
    })
    claims = [key for key, claim in state["claims"].items() if claim["phase"] == "CONFIRMATORY"]
    return {"schema_version": 2, "sha256": digest(manifest), "manifest": manifest,
            "conclusion": copy.deepcopy(conclusion), "claim_ids": sorted(claims)}


def _transition(root, state, action, payload):
    if action == "initialized":
        _require(state is None, "project already initialized")
        _keys(payload, {"contract", "predecessor", "initial_artifacts"}, "initialization")
        _contract(payload["contract"])
        state = {"contract": copy.deepcopy(payload["contract"]), "version": 1, "checkpoint": 0, "status": "ACTIVE",
                 "scientific_result": "NOT_YET_TESTED", "artifacts": {}, "runs": {}, "claims": {}, "qualifications": {},
                 "freeze": None, "evidence_lock": None, "verification": None, "release": None,
                 "notes": [], "rejections": [], "budget_overruns": [], "run_versions": {}, "claim_versions": {},
                 "predecessor": payload["predecessor"]}
        if payload["predecessor"] is not None:
            predecessor = payload["predecessor"]
            _keys(predecessor, {"project_id", "head", "scientific_result", "relationship", "relationship_kind", "new_protocol_sha256"}, "predecessor")
            _text(predecessor["project_id"], "predecessor project_id")
            _sha(predecessor["head"], "predecessor head")
            _sha(predecessor["new_protocol_sha256"], "successor protocol SHA-256")
            _require(predecessor["scientific_result"] in OUTCOMES | {"INVALID"}, "predecessor is not terminal")
            _require(predecessor["relationship_kind"] in {"NEW_HYPOTHESIS", "VALIDITY_CORRECTION"}, "invalid predecessor relationship kind")
            if predecessor["relationship_kind"] == "VALIDITY_CORRECTION":
                _require(predecessor["scientific_result"] == "INVALID", "validity correction requires an invalid predecessor")
        for artifact in payload["initial_artifacts"]:
            state = _transition(root, state, "artifact", artifact)
        return state
    _require(state is not None, "project is not initialized")
    _require(state["status"] == "ACTIVE", "terminal project state is immutable")
    if action == "attempt_rejected":
        state["rejections"].append(copy.deepcopy(payload))
    elif action == "artifact":
        _keys(payload, {"artifact_id", "kind", "sha256", "bytes", "source_name", "parents"}, "artifact")
        _text(payload["artifact_id"], "artifact_id")
        _require(payload["artifact_id"] not in state["artifacts"], "artifact_id is immutable")
        _require(payload["kind"] in KINDS, "unknown artifact kind")
        if state["freeze"]:
            _require(payload["kind"] in POST_FREEZE_KINDS, "scientific input artifacts cannot change after freeze")
        _sha(payload["sha256"], "artifact SHA-256")
        _number(payload["bytes"], "artifact bytes", integer=True, positive=True)
        _text(payload["source_name"], "source_name")
        _strings(payload["parents"], "artifact parents", nonempty=False)
        for parent in payload["parents"]:
            _artifact(state, parent)
        _verify_object(root, payload)
        state["artifacts"][payload["artifact_id"]] = copy.deepcopy(payload)
    elif action == "note":
        _keys(payload, {"observation", "cause", "change", "prediction", "experiment", "result"}, "development note")
        for key, value in payload.items():
            _text(value, key)
        state["notes"].append(copy.deepcopy(payload))
    elif action == "revise":
        _keys(payload, {"contract", "reason"}, "revision")
        _require(state["freeze"] is None, "contract is frozen; create a successor")
        _contract(payload["contract"])
        _text(payload["reason"], "revision reason")
        _require(payload["contract"]["project_id"] == state["contract"]["project_id"], "revision cannot change project identity")
        state["contract"] = copy.deepcopy(payload["contract"])
        state["version"] += 1
        state["checkpoint"] = 0
        state["qualifications"] = {}
    elif action == "checkpoint":
        _keys(payload, {"number", "evidence", "reviewer", "note"}, "checkpoint")
        number = payload["number"]
        _require(type(number) is int and 1 <= number <= 6, "checkpoint command admits only checkpoints 1 through 6")
        _require(number == state["checkpoint"] + 1, "checkpoints must advance in order")
        _require(not _budgets(state)["blocked"], "recorded budget overrun blocks qualification; revise the prefreeze contract explicitly")
        allowed = {1: {"specification"}, 2: {"specification"}, 3: {"protocol"}, 4: {"code"}, 5: {"code", "verification"}, 6: {"verification"}}
        _artifact(state, payload["evidence"], allowed[number])
        _text(payload["reviewer"], "reviewer")
        _text(payload["note"], "qualification note")
        state["checkpoint"] = number
        state["qualifications"][str(number)] = copy.deepcopy(payload)
    elif action == "freeze":
        _keys(payload, {"protocol_artifact"}, "freeze")
        _require(state["checkpoint"] == 6 and state["freeze"] is None, "freeze requires RUN READY and no earlier freeze")
        _require(not _budgets(state)["blocked"], "recorded budget overrun blocks freeze; revise the prefreeze contract explicitly")
        artifact_id = payload["protocol_artifact"]
        protocol = _artifact_json(root, state, artifact_id, {"protocol"})
        _protocol(root, state, protocol)
        _require(artifact_id == state["qualifications"]["3"]["evidence"], "frozen protocol must be the qualified methodology artifact")
        _require(protocol["architecture_artifact"] == state["qualifications"]["2"]["evidence"], "frozen architecture differs from the qualified specification")
        _require(protocol["code"]["artifact"] == state["qualifications"]["4"]["evidence"], "frozen code differs from the qualified implementation")
        spent = sum((Fraction(run["runtime_seconds"]) for run in state["runs"].values()), Fraction())
        _require(Fraction(protocol["compute_protocol"]["max_seconds"]) <= Fraction(state["contract"]["compute_budget"]["seconds"]) - spent,
                 "frozen compute cap exceeds the remaining project compute budget")
        item = _artifact(state, artifact_id)
        if state["predecessor"]:
            _require(item["sha256"] == state["predecessor"]["new_protocol_sha256"], "successor freeze differs from its declared new protocol")
        state["freeze"] = {"artifact_id": artifact_id, "sha256": item["sha256"], "protocol": protocol}
        state["checkpoint"] = 7
    elif action == "run":
        _run(root, state, payload)
        state["runs"][payload["run_id"]] = copy.deepcopy(payload)
        state["run_versions"][payload["run_id"]] = state["version"]
        for budget, accounting in _budgets(state).items():
            if isinstance(accounting, dict) and accounting["overrun"]:
                state["budget_overruns"].append({"run_id": payload["run_id"], "version": state["version"],
                                                  "budget": budget, "accounting": accounting})
    elif action == "claim":
        _claim(state, payload)
        state["claims"][payload["claim_id"]] = copy.deepcopy(payload)
        state["claim_versions"][payload["claim_id"]] = state["version"]
    elif action in {"lock_evidence", "lock_evidence_v2"}:
        _keys(payload, {"disposition", "scope", "reason"}, "conclusion")
        _require(state["checkpoint"] == 7, "evidence locking requires frozen confirmation")
        _require(payload["disposition"] in OUTCOMES, "INVALID cannot masquerade as a valid terminal result")
        _require(not _budgets(state)["blocked"] or payload["disposition"] == "INCONCLUSIVE",
                 "frozen budget overrun permits only inconclusive or explicit invalid closure; retain every receipt")
        _text(payload["scope"], "conclusion scope")
        _text(payload["reason"], "conclusion reason")
        expected = {item["run_id"] for item in state["freeze"]["protocol"]["expected_runs"]}
        actual = {key for key, run in state["runs"].items() if run["phase"] == "CONFIRMATORY"}
        _require(actual == expected, "the frozen matrix has missing or unexpected runs")
        runs = [state["runs"][key] for key in expected]
        _require(all(run["status"] != "INVALID" for run in runs), "invalid evidence requires correction or explicit invalid closure")
        if payload["disposition"] != "INCONCLUSIVE":
            _require(any(run["status"] == "SUCCESS" for run in runs), "failed executions alone cannot establish this scientific conclusion")
        claims = {key: value for key, value in state["claims"].items() if value["phase"] == "CONFIRMATORY"}
        _require(claims, "evidence locking requires a traceable confirmatory claim or failure-analysis claim")
        if payload["disposition"] != "INCONCLUSIVE":
            _require(any(claim["status"] in {"SUPPORTED", "PARTIALLY_SUPPORTED"} for claim in claims.values()), "this conclusion requires at least one supported evidentiary statement")
        bound = {"freeze": state["freeze"], "runs": {key: state["runs"][key] for key in sorted(expected)}, "claims": claims, "conclusion": payload}
        # Original event semantics remain replayable. Public writes select v2.
        state["evidence_lock"] = (_seal_evidence(state, payload) if action == "lock_evidence_v2" else
                                  {"sha256": digest(bound), "conclusion": copy.deepcopy(payload), "claim_ids": sorted(claims)})
        state["scientific_result"] = payload["disposition"]
        state["checkpoint"] = 8
    elif action == "reseal_evidence":
        _keys(payload, {"reason"}, "evidence reseal")
        _text(payload["reason"], "reseal reason")
        _require(state["checkpoint"] in {8, 9}, "reseal requires an active locked or verified study")
        previous = state["evidence_lock"]
        _require(previous.get("schema_version", 1) == 1, "evidence already uses a byte-bound seal")
        state["evidence_lock"] = _seal_evidence(state, previous["conclusion"], previous_seal=previous)
        # Old receipts and events remain retained, but attest to the old digest.
        state["verification"] = None
        state["checkpoint"] = 8
    elif action in {"verify_review", "verify_review_v2"}:
        _keys(payload, {"verification_artifact"}, "verification")
        _require(state["checkpoint"] == 8, "independent review requires locked evidence")
        if action == "verify_review_v2":
            _require(state["evidence_lock"].get("schema_version", 1) == 2,
                     "legacy evidence requires explicit reseal-evidence before a new review")
        receipt = _artifact_json(root, state, payload["verification_artifact"], {"verification"})
        receipt_keys = {"reviewer", "evidence_sha256", "paper_artifact", "environment_artifact", "checks", "reproduction_command", "limits"}
        if action == "verify_review_v2":
            receipt_keys |= {"paper_sha256", "environment_sha256"}
        _keys(receipt, receipt_keys, "verification receipt")
        _text(receipt["reviewer"], "independent reviewer")
        _require(receipt["reviewer"].strip().casefold() != state["contract"]["owner"].strip().casefold(), "independent reviewer must differ from project owner")
        _require(receipt["evidence_sha256"] == state["evidence_lock"]["sha256"], "verification is not bound to the locked evidence")
        _artifact(state, receipt["paper_artifact"], {"paper"})
        _artifact(state, receipt["environment_artifact"], {"environment"})
        if action == "verify_review_v2":
            _require(receipt["environment_artifact"] == state["freeze"]["protocol"]["environment_artifact"],
                     "review environment must be the frozen release environment")
            for role in ("paper", "environment"):
                recorded = receipt[role + "_sha256"]
                _sha(recorded, role + " identity")
                _require(recorded == _artifact(state, receipt[role + "_artifact"])["sha256"],
                         f"review {role} identity differs from the retained bytes")
        _keys(receipt["checks"], VERIFY_CHECKS, "verification checks")
        _require(all(value is True for value in receipt["checks"].values()), "all declared independent verification checks must pass")
        _text(receipt["reproduction_command"], "reproduction command")
        _text(receipt["limits"], "verification limits")
        state["verification"] = {"artifact_id": payload["verification_artifact"], "receipt": receipt}
        state["checkpoint"] = 9
    elif action in {"complete", "complete_v2"}:
        _keys(payload, {"release_artifact"}, "release")
        _require(state["checkpoint"] == 9, "completion requires independent verification")
        if action == "complete_v2":
            _require(state["evidence_lock"].get("schema_version", 1) == 2,
                     "legacy evidence requires explicit reseal-evidence and a new review before release")
        release = _artifact_json(root, state, payload["release_artifact"], {"release"})
        _keys(release, {"release_commit", "disposition", "scope", "evidence_sha256", "roles", "reviews"}, "release manifest")
        _sha(release["release_commit"], "release commit", 40)
        conclusion = state["evidence_lock"]["conclusion"]
        _require(release["disposition"] == conclusion["disposition"] and release["scope"] == conclusion["scope"], "release must preserve the locked disposition and scope")
        _require(release["evidence_sha256"] == state["evidence_lock"]["sha256"], "release evidence identity differs")
        _keys(release["roles"], RELEASE_ROLES, "release roles")
        protocol = state["freeze"]["protocol"]
        _require(release["roles"]["paper"] == state["verification"]["receipt"]["paper_artifact"], "release paper was not independently verified")
        _require(release["roles"]["code"] == protocol["code"]["artifact"], "release code differs from frozen code")
        _require(release["roles"]["environment"] == protocol["environment_artifact"], "release environment differs from frozen environment")
        configs = {run["config_artifact"] for run in protocol["expected_runs"]}
        _artifact_list(state, release["roles"]["configuration"], {"config"}, "release configuration")
        _require(set(release["roles"]["configuration"]) == configs, "release must include every frozen configuration")
        for role in ("reproduction", "data_instructions"):
            _artifact(state, release["roles"][role], {"other"})
        _keys(release["reviews"], RELEASE_REVIEWS, "release reviews")
        for key, review in release["reviews"].items():
            _require(isinstance(review, dict), f"release {key} review must be an object")
            if set(review) == {"artifact_id"}:
                _artifact(state, review["artifact_id"])
            else:
                _keys(review, {"not_applicable"}, f"release {key}")
                _text(review["not_applicable"], f"{key} inapplicability reason")
        state["release"] = {"artifact_id": payload["release_artifact"], "manifest": release}
        state["checkpoint"] = 10
        state["status"] = "COMPLETE"
    elif action == "close_invalid":
        _keys(payload, {"reason", "report_artifact"}, "invalid closure")
        _text(payload["reason"], "invalid closure reason")
        _artifact(state, payload["report_artifact"], {"verification", "analysis"})
        state["status"] = "INVALID_CLOSED"
        state["scientific_result"] = "INVALID"
        state["invalid_closure"] = copy.deepcopy(payload)
    else:
        raise GateError(f"unknown action: {action}")
    return state


def _render(events, state):
    contract = state["contract"]
    heading_map = [("Identity", f"{contract['title']} (`{contract['project_id']}`), owner: {contract['owner']}"),
                   ("Research Question", contract["question"]), ("Scientific Objective", contract["objective"]),
                   ("Current Hypothesis", contract["hypothesis"]), ("Intended Contribution", contract["contribution"]),
                   ("Project Scope", contract["scope"]), ("Current Phase", CHECKPOINTS[state["checkpoint"]]),
                   ("Project Status", state["status"]), ("Current Scientific Result", state["scientific_result"]),
                   ("Development Budget", json.dumps(contract["development_budget"], sort_keys=True)),
                   ("Compute Budget", json.dumps(contract["compute_budget"], sort_keys=True)),
                   ("Budget Accounting", json.dumps(_budgets(state), sort_keys=True)),
                   ("Recorded Budget Overruns", json.dumps(state["budget_overruns"], sort_keys=True)),
                   ("Protected Evaluation Boundary", contract["protected_boundary"]),
                   ("Datasets", json.dumps(contract["datasets"])), ("Repositories", json.dumps(contract["repositories"])),
                   ("Inherited Historical Record", json.dumps(contract["known_history"])),
                   ("Important Artifacts", ", ".join(state["artifacts"]) or "None registered"),
                   ("Current Best Evidence", json.dumps(state["evidence_lock"], sort_keys=True)),
                   ("Claims Currently Supported", ", ".join(f"{key} [{value['phase']}]" for key, value in state["claims"].items() if state["claim_versions"][key] == state["version"] and value["status"] in {"SUPPORTED", "PARTIALLY_SUPPORTED"}) or "None recorded"),
                   ("Claims Not Yet Supported", ", ".join(f"{key} [{value['phase']}]" for key, value in state["claims"].items() if state["claim_versions"][key] == state["version"] and value["status"] in {"UNSUPPORTED", "REJECTED"}) or "None recorded"),
                   ("All Historical Claims", ", ".join(f"{key}: version {state['claim_versions'][key]}, {value['phase']}, {value['status']}" for key, value in state["claims"].items()) or "None recorded"),
                   ("Completed Work", f"{state['checkpoint']} of 10 current qualifications; prior versions remain in the event ledger."),
                   ("Missing Work", "No later checkpoint remains." if state["checkpoint"] == 10 else CHECKPOINTS[state["checkpoint"] + 1]),
                   ("Known Failures", ", ".join(key for key, value in state["runs"].items() if value["status"] != "SUCCESS") or "No failed runs recorded"),
                   ("Important Decisions", f"{len(state['notes'])} notes and {len(state['rejections'])} rejected attempts retained; see full ledger."),
                   ("Blockers", "See incomplete checkpoint, failed/invalid runs, and rejected transitions below."),
                   ("Next Executable Action", contract["next_action"]), ("Definition of Done", contract["definition_of_done"]),
                   ("Last Updated", events[-1]["timestamp"]), ("History Head SHA-256", events[-1]["sha256"])]
    body = "# Project State\n\nThis file is generated from its canonical event ledger. Use the research_pipeline CLI; manual edits are rejected.\n"
    for title, value in heading_map:
        body += f"\n## {title}\n\n{value}\n"
    return body + MARKER + json.dumps({"schema_version": 1, "events": events}, indent=2, ensure_ascii=False, allow_nan=False) + "\n```\n"


def _new_event(events, action, payload):
    event = {"sequence": len(events), "previous": events[-1]["sha256"] if events else None,
             "timestamp": datetime.now(timezone.utc).isoformat(), "action": action, "payload": copy.deepcopy(payload)}
    event["sha256"] = digest(event)
    return event


class Project:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.path = self.root / "STATE.md"

    @contextmanager
    def _lock(self):
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / ".research-state.lock"
        fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise IntegrityError("project lock must be a regular file")
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise BusyError("project is busy; no update was committed") from exc
            yield
        finally:
            os.close(fd)

    def _write(self, events, state):
        if self.path.is_symlink() or (self.path.exists() and not self.path.is_file()):
            raise IntegrityError("STATE.md must be a regular file")
        fd, name = tempfile.mkstemp(prefix=".STATE-", dir=self.root)
        staging = Path(name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(_render(events, state))
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(staging, self.path)
            try:
                _sync_directory(self.root)
            except OSError as exc:
                raise OSError("STATE.md was installed but directory fsync failed; verify the current state before retrying") from exc
        finally:
            staging.unlink(missing_ok=True)

    def _load(self):
        try:
            if self.path.is_symlink() or not self.path.is_file():
                raise IntegrityError("STATE.md must exist as a regular file")
            text = self.path.read_text(encoding="utf-8")
            _require(MARKER in text and text.endswith("\n```\n"), "canonical ledger framing is missing")
            payload = strict_json(text.rpartition(MARKER)[2][:-5])
            _keys(payload, {"schema_version", "events"}, "ledger")
            _require(type(payload["schema_version"]) is int and payload["schema_version"] == 1, "unsupported ledger schema")
            events = payload["events"]
            _require(isinstance(events, list) and events, "ledger has no initialization")
            state, previous = None, None
            for index, event in enumerate(events):
                _keys(event, {"sequence", "previous", "timestamp", "action", "payload", "sha256"}, "event")
                _require(type(event["sequence"]) is int and event["sequence"] == index and event["previous"] == previous, "event sequence or previous hash changed")
                _sha(event["sha256"], "event SHA-256")
                _require(event["sha256"] == digest({key: value for key, value in event.items() if key != "sha256"}), "event hash mismatch")
                _text(event["timestamp"], "event timestamp")
                state = _transition(self.root, state, event["action"], event["payload"])
                previous = event["sha256"]
            _require(text == _render(events, state), "STATE.md projection differs from its canonical ledger")
            return events, state
        except (GateError, OSError, UnicodeError, TypeError, KeyError) as exc:
            raise IntegrityError(f"state verification failed: {exc}") from exc

    def read(self, expected_head=None):
        events, state = self._load()
        if expected_head is not None and expected_head != events[-1]["sha256"]:
            raise IntegrityError("state head differs from the trusted expected head")
        state["budget_accounting"] = _budgets(state)
        return {"head": events[-1]["sha256"], "event_count": len(events), "state": state}

    def history(self, expected_head=None):
        events, _ = self._load()
        if expected_head is not None and expected_head != events[-1]["sha256"]:
            raise IntegrityError("state head differs from the trusted expected head")
        return {"head": events[-1]["sha256"], "events": events}

    def _snapshot(self, source):
        source = Path(source)
        _require(source.is_file(), "artifact source must be a regular file")
        objects = _object_path(self.root, "0" * 64).parent
        objects.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(prefix=".object-", dir=objects)
        staging = Path(name)
        try:
            sha, size = hashlib.sha256(), 0
            with os.fdopen(fd, "wb") as outgoing:
                with source.open("rb") as incoming:
                    _require(stat.S_ISREG(os.fstat(incoming.fileno()).st_mode), "artifact source must be a regular file")
                    for chunk in iter(lambda: incoming.read(1024 * 1024), b""):
                        outgoing.write(chunk)
                        sha.update(chunk)
                        size += len(chunk)
                    outgoing.flush()
                    os.fsync(outgoing.fileno())
            _require(size > 0, "artifact must be nonempty")
            item = {"sha256": sha.hexdigest(), "bytes": size, "source_name": source.name}
            target = objects / item["sha256"]
            try:
                os.link(staging, target)
            except FileExistsError:
                _verify_object(self.root, item)
            for directory in (objects, objects.parent, self.root):
                _sync_directory(directory)
            return item
        finally:
            staging.unlink(missing_ok=True)

    def initialize(self, contract, *, predecessor=None, protocol_source=None):
        _contract(contract)
        with self._lock():
            _require(not self.path.exists() and not self.path.is_symlink(), "project already has canonical state")
            initial = []
            if protocol_source is not None:
                item = self._snapshot(protocol_source)
                _require(item["sha256"] == predecessor["new_protocol_sha256"], "successor protocol changed while initializing")
                initial.append({**item, "artifact_id": "successor-protocol", "kind": "protocol", "parents": []})
            payload = {"contract": contract, "predecessor": predecessor, "initial_artifacts": initial}
            state = _transition(self.root, None, "initialized", payload)
            self._write([_new_event([], "initialized", payload)], state)
            return self.read()

    def _reject(self, events, state, action, payload, exc):
        if state["status"] == "ACTIVE":
            rejected = {"attempted_action": action, "reason": str(exc), "proposal_repr": repr(payload)}
            event = _new_event(events, "attempt_rejected", rejected)
            candidate = _transition(self.root, copy.deepcopy(state), "attempt_rejected", rejected)
            self._write(events + [event], candidate)

    def _admit(self, events, state, action, payload, expected_head):
        try:
            _require(state["status"] == "ACTIVE", "terminal project state is immutable")
            _require(expected_head is None or expected_head == events[-1]["sha256"], "stale expected head; scientific update rejected")
            canonical(payload)
            candidate = _transition(self.root, copy.deepcopy(state), action, payload)
        except (TypeError, ValueError) as exc:
            self._reject(events, state, action, payload, exc)
            raise GateError(str(exc)) from exc
        event = _new_event(events, action, payload)
        self._write(events + [event], candidate)

    def apply(self, action, payload, *, expected_head=None):
        # These v1 names are accepted only by history replay. Normal API/CLI
        # updates always use explicit v2 event semantics, even on old studies.
        action = {"lock_evidence": "lock_evidence_v2", "verify_review": "verify_review_v2",
                  "complete": "complete_v2"}.get(action, action)
        with self._lock():
            events, state = self._load()
            self._admit(events, state, action, payload, expected_head)
            return self.read()

    def add_artifact(self, artifact_id, kind, source, parents=(), *, expected_head=None):
        # Snapshot first; if admission is rejected the unreferenced object is an
        # orphan, never a replacement for earlier scientific state or evidence.
        with self._lock():
            events, state = self._load()
            proposal = {"artifact_id": artifact_id, "kind": kind, "source_name": Path(source).name, "parents": list(parents)}
            try:
                _require(state["status"] == "ACTIVE", "terminal project state is immutable")
                _require(expected_head is None or expected_head == events[-1]["sha256"], "stale expected head; scientific update rejected")
                snapshot = self._snapshot(source)
            except ValueError as exc:
                self._reject(events, state, "artifact", proposal, exc)
                raise GateError(str(exc)) from exc
            self._admit(events, state, "artifact", {**snapshot, **proposal}, expected_head)
            return self.read()

    def successor(self, target, contract, relationship, protocol_source, *, validity_correction=False):
        current = self.read()
        state = current["state"]
        _require(state["status"] in {"COMPLETE", "INVALID_CLOSED"}, "successor requires a preserved terminal predecessor")
        relationship_keys = ({"previous_finding", "validity_defect", "repair", "affected_work", "justification"} if validity_correction
                             else {"previous_finding", "remaining_problem", "new_hypothesis", "material_difference", "new_falsifier"})
        _keys(relationship, relationship_keys, "successor relationship")
        for key, value in relationship.items():
            _text(value, key)
        _contract(contract)
        _require(contract["project_id"] != state["contract"]["project_id"], "successor requires a new project identity")
        if validity_correction:
            _require(state["status"] == "INVALID_CLOSED", "validity correction requires an explicitly invalid predecessor")
            _require(contract["hypothesis"] == state["contract"]["hypothesis"] and contract["question"] == state["contract"]["question"],
                     "validity correction preserves the scientific question and hypothesis; a new idea uses an ordinary successor")
        else:
            _require(relationship["new_hypothesis"] == contract["hypothesis"] and contract["hypothesis"] != state["contract"]["hypothesis"], "successor requires its new, materially different hypothesis")
        target_root = Path(target).resolve()
        _require(target_root != self.root and self.root not in target_root.parents and target_root not in self.root.parents,
                 "successor directory must be separate from the predecessor, without nesting either project")
        raw = Path(protocol_source).read_bytes()
        protocol = strict_json(raw.decode("utf-8"))
        _keys(protocol, PROTOCOL_KEYS, "successor protocol")
        for key in ("question", "hypothesis", "protected_boundary"):
            _require(protocol[key] == contract[key], f"successor protocol {key} differs from its contract")
        protocol_sha = hashlib.sha256(raw).hexdigest()
        if validity_correction and state["freeze"]:
            _require(protocol_sha != state["freeze"]["sha256"], "validity correction requires a changed protocol identity")
        predecessor = {"project_id": state["contract"]["project_id"], "head": current["head"],
                       "scientific_result": state["scientific_result"], "relationship": relationship,
                       "relationship_kind": "VALIDITY_CORRECTION" if validity_correction else "NEW_HYPOTHESIS",
                       "new_protocol_sha256": protocol_sha}
        return Project(target).initialize(contract, predecessor=predecessor, protocol_source=protocol_source)
