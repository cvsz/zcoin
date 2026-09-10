from pathlib import Path
from fastapi.testclient import TestClient
import app.storage as storage
from app.main import app


def test_ingest_idempotent_and_unverified_evidence_is_blocked(tmp_path: Path):
    storage.DB_PATH = str(tmp_path / "auditor.db")
    csv = "client_seed,nonce,reported_result,payout_multiplier\ndemo,1,1,1.98\ndemo,2,0,1.98\n"
    with TestClient(app) as client:
        first = client.post('/api/ingest', data={'dataset':'case','algorithm':'new'}, files={'file':('case.csv',csv,'text/csv')})
        second = client.post('/api/ingest', data={'dataset':'case','algorithm':'new'}, files={'file':('case.csv',csv,'text/csv')})
        assert first.status_code == 200 and first.json()['inserted'] == 2
        assert second.json()['inserted'] == 0 and second.json()['skipped_duplicates'] == 2
        assert client.get('/healthz').json()['version'] == '0.3.1'
        evidence = client.get('/api/evidence/case').json()['evidence']
        assert evidence['classification'] == 'IMPLEMENTATION_MISMATCH_OR_UNVERIFIED'


def test_ingest_rejects_bad_numeric_data(tmp_path: Path):
    storage.DB_PATH = str(tmp_path / 'bad.db')
    with TestClient(app) as client:
        response = client.post('/api/ingest', data={'dataset':'bad','algorithm':'new'}, files={'file':('bad.csv','client_seed,nonce,reported_result\ndemo,nope,0\n','text/csv')})
        assert response.status_code == 400


def test_report_escapes_dataset(tmp_path: Path):
    storage.DB_PATH = str(tmp_path / 'xss.db')
    dataset = '<img src=x onerror=alert(1)>'
    with TestClient(app) as client:
        client.post('/api/ingest', data={'dataset':dataset,'algorithm':'new'}, files={'file':('a.csv','client_seed,nonce,reported_result\ndemo,1,0\n','text/csv')})
        report = client.get('/report/' + dataset)
        assert report.status_code == 200
        assert dataset not in report.text
        assert '&lt;img src=x onerror=alert(1)&gt;' in report.text
