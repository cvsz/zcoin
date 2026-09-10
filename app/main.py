from __future__ import annotations

import csv
import hashlib
import html
import io
import json
from contextlib import asynccontextmanager
from pathlib import Path
from statistics import mean

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field

from .advanced_stats import (autocorrelation_binary, beta_posterior, bh_fdr,
    bootstrap_rate, epoch_segments, holdout_split, simple_change_points,
    transition_matrix)
from .evidence import build_report, score_evidence
from .stats import edge_assessment, longest_streak, nonce_audit, proportion_z_test, runs_test
from .storage import connect, init_db
from .strategy import compare_strategies, monte_carlo_null, walk_forward_bias_strategy
from .verifier import verify_result, verify_server_seed

VERSION = "0.3.1"
STATIC_DIR = Path(__file__).parent / "static"

@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield

app = FastAPI(title="zCoin CoinFlip Evidence Auditor", version=VERSION,
              description="Historical revealed-seed verification, evidence analysis, and paper simulation only.",
              lifespan=lifespan)

class VerifyRequest(BaseModel):
    server_seed: str
    server_seed_hash: str | None = None
    client_seed: str
    nonce: int = Field(ge=0)
    round_no: int = Field(default=1, ge=1)
    reported_result: int = Field(ge=0, le=1)
    algorithm: str = Field(default="new", pattern="^(new|old)$")

@app.get("/healthz")
def healthz():
    return {"status": "ok", "version": VERSION, "mode": "audit-paper-only"}

@app.get("/api/version")
def api_version():
    return {"name": "zcoin", "version": VERSION, "mode": "audit-paper-only"}

@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")

@app.post("/api/verify")
def api_verify(req: VerifyRequest):
    result = verify_result(req.server_seed, req.client_seed, req.nonce, req.round_no,
                           req.reported_result, req.algorithm)
    result["server_seed_hash_match"] = (verify_server_seed(req.server_seed, req.server_seed_hash)
                                             if req.server_seed_hash else None)
    return result

@app.post("/api/ingest")
async def ingest_csv(file: UploadFile = File(...), dataset: str = Form(...),
                     algorithm: str = Form("new")):
    if algorithm not in {"old", "new"}: raise HTTPException(400, "algorithm must be old or new")
    if not dataset.strip(): raise HTTPException(400, "dataset is required")
    try: text = (await file.read()).decode("utf-8-sig")
    except UnicodeDecodeError as exc: raise HTTPException(400, "CSV must be UTF-8") from exc
    reader = csv.DictReader(io.StringIO(text))
    required = {"client_seed", "nonce", "reported_result"}
    missing = required - set(reader.fieldnames or [])
    if missing: raise HTTPException(400, f"Missing CSV columns: {sorted(missing)}")
    inserted = skipped = verified = 0
    with connect() as con:
        for row in reader:
            client_seed = (row.get("client_seed") or "").strip()
            if not client_seed: raise HTTPException(400, f"row {reader.line_num}: client_seed is required")
            try:
                nonce = int(row["nonce"]); round_no = int(row.get("round") or row.get("round_no") or 1)
                reported = int(row["reported_result"])
                amount = float(row["amount"]) if row.get("amount") else None
                payout = float(row["payout_multiplier"]) if row.get("payout_multiplier") else None
            except (TypeError, ValueError) as exc:
                raise HTTPException(400, f"row {reader.line_num}: invalid numeric field") from exc
            if nonce < 0 or round_no < 1 or reported not in (0, 1):
                raise HTTPException(400, f"row {reader.line_num}: invalid nonce/round/result")
            if payout is not None and payout <= 1.0: raise HTTPException(400, "payout_multiplier must be > 1")
            if amount is not None and amount < 0: raise HTTPException(400, "amount must be >= 0")
            server_seed = (row.get("server_seed") or "").strip()
            seed_hash = (row.get("server_seed_hash") or "").strip()
            expected = result_match = seed_match = None
            if server_seed:
                vr = verify_result(server_seed, client_seed, nonce, round_no, reported, algorithm)
                expected, result_match = vr["expected_result"], int(vr["result_match"]); verified += 1
                if seed_hash: seed_match = int(verify_server_seed(server_seed, seed_hash))
            fp = hashlib.sha256(json.dumps({"bet_id": row.get("bet_id"), "ts": row.get("ts"),
                "server_seed_hash": seed_hash or None, "client_seed": client_seed, "nonce": nonce,
                "round_no": round_no, "reported_result": reported, "algorithm": algorithm},
                sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            cur = con.execute("""INSERT OR IGNORE INTO bets
                (dataset,ts,bet_id,server_seed,server_seed_hash,client_seed,nonce,round_no,
                 reported_result,algorithm,expected_result,result_match,seed_hash_match,amount,
                 payout_multiplier,row_fingerprint) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (dataset,row.get("ts"),row.get("bet_id"),server_seed or None,seed_hash or None,
                 client_seed,nonce,round_no,reported,algorithm,expected,result_match,seed_match,
                 amount,payout,fp))
            inserted += int(cur.rowcount > 0); skipped += int(cur.rowcount == 0)
    return {"dataset": dataset, "inserted": inserted, "skipped_duplicates": skipped,
            "cryptographically_verified": verified}

def _rows(dataset: str):
    with connect() as con: rows = con.execute("SELECT * FROM bets WHERE dataset=? ORDER BY id", (dataset,)).fetchall()
    if not rows: raise HTTPException(404, "dataset not found")
    return rows

@app.get("/api/datasets")
def datasets():
    with connect() as con: return [dict(r) for r in con.execute("SELECT dataset,COUNT(*) n FROM bets GROUP BY dataset ORDER BY dataset")]

@app.delete("/api/datasets/{dataset}")
def delete_dataset(dataset: str):
    with connect() as con: cur = con.execute("DELETE FROM bets WHERE dataset=?", (dataset,))
    return {"dataset": dataset, "deleted": cur.rowcount}

@app.get("/api/analysis/{dataset}")
def analysis(dataset: str):
    rows = _rows(dataset); values = [int(r["reported_result"]) for r in rows]
    matches = [r["result_match"] for r in rows if r["result_match"] is not None]
    seeds = [r["seed_hash_match"] for r in rows if r["seed_hash_match"] is not None]
    payouts = [float(r["payout_multiplier"]) for r in rows if r["payout_multiplier"] is not None]
    edge = edge_assessment(values, mean(payouts) if payouts else 1.98)
    integrity = {"rows_with_result_verification": len(matches),
        "result_match_rate": sum(matches)/len(matches) if matches else None,
        "rows_with_seed_hash_verification": len(seeds),
        "seed_hash_match_rate": sum(seeds)/len(seeds) if seeds else None}
    if (matches and not all(matches)) or (seeds and not all(seeds)):
        edge["positive_edge_evidence"] = False
    return {"dataset": dataset, "counts": {"n": len(values), "result_0": values.count(0), "result_1": values.count(1)},
        "cryptographic_integrity": integrity, "nonce_audit": nonce_audit([r["nonce"] for r in rows]),
        "proportion_test": proportion_z_test(values), "runs_test": runs_test(values),
        "longest_streak": longest_streak(values), "edge_assessment": edge,
        "warning": "Historical anomalies do not predict the next flip."}

@app.get("/api/advanced/{dataset}")
def advanced_analysis(dataset: str):
    rows = [dict(r) for r in _rows(dataset)]; values = [int(r["reported_result"]) for r in rows]
    payouts = [float(r["payout_multiplier"]) for r in rows if r["payout_multiplier"] is not None]
    break_even = 1.0/(mean(payouts) if payouts else 1.98)
    ac = autocorrelation_binary(values, 20); split = holdout_split(values, .7)
    epochs = epoch_segments(rows); epoch_tests = []
    for epoch in epochs:
        test = proportion_z_test([int(r["reported_result"]) for r in epoch["rows"]])
        epoch_tests.append({"epoch_key": epoch["epoch_key"], "start_index": epoch["start_index"],
            "end_index": epoch["end_index"], "n": epoch["n"], "rate_1": epoch["rate_1"], "p_value": test["p_value"]})
    return {"dataset": dataset, "break_even_probability": break_even,
        "bootstrap": bootstrap_rate(values), "bayesian": beta_posterior(values, break_even=break_even),
        "autocorrelation": ac, "autocorrelation_fdr": bh_fdr([x["p_value"] for x in ac]),
        "transitions": transition_matrix(values), "change_points": simple_change_points(values),
        "holdout": {"train_n": len(split["train"]), "holdout_n": len(split["holdout"]),
            "train": proportion_z_test(split["train"]) if split["train"] else None,
            "holdout": proportion_z_test(split["holdout"]) if split["holdout"] else None},
        "epochs": epoch_tests, "epoch_fdr": bh_fdr([x["p_value"] for x in epoch_tests])}

@app.get("/api/evidence/{dataset}")
def evidence_report(dataset: str):
    base, adv = analysis(dataset), advanced_analysis(dataset); rows = [dict(r) for r in _rows(dataset)]
    integrity = base["cryptographic_integrity"]; total = base["counts"]["n"]
    expected_seed_checks = sum(bool(r.get("server_seed_hash")) for r in rows)
    integrity_ok = (integrity["rows_with_result_verification"] == total and integrity["result_match_rate"] == 1.0
        and (expected_seed_checks == 0 or (integrity["rows_with_seed_hash_verification"] == expected_seed_checks and integrity["seed_hash_match_rate"] == 1.0)))
    favored = base["edge_assessment"]["favored_side"]; break_even = adv["break_even_probability"]
    discoveries = []
    for i in adv["epoch_fdr"]["discoveries"]:
        ep = adv["epochs"][i]; rate = ep["rate_1"] if favored == 1 else 1-ep["rate_1"]
        if ep["n"] >= 300 and rate > break_even: discoveries.append(i)
    hold = adv["holdout"]["holdout"]; hold_ok = False
    if hold and hold["n"] >= 300 and hold["p_hat"] is not None and hold["p_value"] is not None:
        rate = hold["p_hat"] if favored == 1 else 1-hold["p_hat"]
        hold_ok = hold["p_value"] < .01 and rate > break_even
    bayes = adv["bayesian"]; key = "probability_result_1_above_break_even" if favored == 1 else "probability_result_0_above_break_even"
    prob = bayes.get(key); post_rate = bayes["posterior_mean"] if favored == 1 else 1-bayes["posterior_mean"]
    evidence = score_evidence(integrity_ok, bool(discoveries),
        (base["edge_assessment"]["absolute_effect_vs_50_50"] or 0) >= .02,
        hold_ok, len(discoveries) >= 2, bool(prob is not None and prob >= .99 and post_rate > break_even))
    evidence.update({"favored_side": favored, "consistent_epoch_discoveries": discoveries,
        "posterior_probability_favored_side_above_break_even": prob,
        "cryptographic_coverage": {"result_rows_verified": integrity["rows_with_result_verification"],
        "total_rows": total, "seed_commitments_expected": expected_seed_checks,
        "seed_commitments_verified": integrity["rows_with_seed_hash_verification"]}})
    return build_report(dataset, VERSION, base, adv, evidence, rows)

@app.get("/api/paper/compare/{dataset}")
def paper_compare(dataset: str):
    rows = _rows(dataset); values = [int(r["reported_result"]) for r in rows]
    payouts = [float(r["payout_multiplier"]) for r in rows if r["payout_multiplier"] is not None]
    return {"mode": "paper-only", "strategies": compare_strategies(values, payout_multiplier=mean(payouts) if payouts else 1.98)}

@app.get("/api/paper/walk-forward/{dataset}")
def paper_walk_forward(dataset: str, train_window: int = 500, min_edge: float = .03):
    if train_window < 100: raise HTTPException(400, "train_window must be >= 100")
    return {"mode": "paper-only", "result": walk_forward_bias_strategy([int(r["reported_result"]) for r in _rows(dataset)], train_window, min_edge)}

@app.get("/api/paper/monte-carlo/{dataset}")
def paper_monte_carlo(dataset: str, simulations: int = 2000):
    rows = _rows(dataset); sims = min(max(simulations, 100), 10000)
    return {"mode": "paper-only", "null_model": monte_carlo_null(len(rows), sims)}

@app.get("/report/{dataset}", response_class=HTMLResponse)
def report_html(dataset: str):
    rep = evidence_report(dataset); evidence = rep["evidence"]
    body = html.escape(json.dumps({"analysis": rep["analysis"], "advanced_validation": rep["advanced_validation"]}, indent=2))
    page = f"""<!doctype html><html><head><meta charset='utf-8'><title>zCoin Evidence Report</title>
<style>body{{font-family:system-ui;max-width:1100px;margin:auto;padding:24px}}pre{{white-space:pre-wrap;background:#f4f4f4;padding:16px;border-radius:10px}}</style></head><body>
<h1>zCoin Evidence Report</h1><p><b>Dataset:</b> {html.escape(dataset)}<br><b>SHA256:</b> {html.escape(rep['dataset_sha256'])}<br>
<b>Score:</b> {evidence['score']}/100<br><b>Classification:</b> {html.escape(evidence['classification'])}</p><pre>{body}</pre>
<p>Historical audit only. This report does not predict future outcomes.</p></body></html>"""
    return HTMLResponse(page)
