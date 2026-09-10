from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone


def dataset_fingerprint(rows: list[dict]) -> str:
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def score_evidence(integrity_ok: bool, corrected_significant: bool,
                   effect_large_enough: bool, holdout_confirms: bool,
                   cross_epoch_confirms: bool, economically_positive: bool) -> dict:
    weights = {"integrity": 25, "corrected_significance": 15, "effect_size": 10,
               "holdout": 20, "cross_epoch": 20, "economic_significance": 10}
    checks = {
        "integrity": integrity_ok,
        "corrected_significance": corrected_significant,
        "effect_size": effect_large_enough,
        "holdout": holdout_confirms,
        "cross_epoch": cross_epoch_confirms,
        "economic_significance": economically_positive,
    }
    score = sum(weights[key] for key, value in checks.items() if value)
    if not integrity_ok:
        classification = "IMPLEMENTATION_MISMATCH_OR_UNVERIFIED"
    elif score >= 85:
        classification = "REPLICATED_POSITIVE_EV_EVIDENCE"
    elif score >= 65:
        classification = "STRONG_STATISTICAL_ANOMALY"
    elif score >= 40:
        classification = "CANDIDATE_ANOMALY"
    else:
        classification = "NO_ACTIONABLE_EVIDENCE"
    return {"score": score, "classification": classification,
            "checks": checks, "weights": weights}


def build_report(dataset: str, version: str, analysis: dict, advanced: dict,
                 evidence: dict, rows: list[dict]) -> dict:
    return {
        "report_schema": "coinflip-evidence-report/1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "auditor_version": version,
        "dataset": dataset,
        "dataset_sha256": dataset_fingerprint(rows),
        "analysis": analysis,
        "advanced_validation": advanced,
        "evidence": evidence,
        "limitations": [
            "Historical anomalies do not guarantee future predictability.",
            "Statistical findings depend on data quality and correct epoch attribution.",
            "Paper-play results are simulation-only and are not live betting instructions.",
        ],
    }
