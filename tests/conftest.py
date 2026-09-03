from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from tests.helpers import PROVIDER_ENV_NAMES

REPORT_ROOT = Path("reports/latest")
FAILURE_ROOT = REPORT_ROOT / "failures"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[object]):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return

    FAILURE_ROOT.mkdir(parents=True, exist_ok=True)
    safe_name = item.nodeid.replace("/", "__").replace("::", "__")
    safe_name = safe_name.replace("[", "_").replace("]", "_")
    payload = {
        "nodeid": item.nodeid,
        "failed_at": datetime.now(UTC).isoformat(),
        "phase": report.when,
        "duration_seconds": report.duration,
        "longrepr": str(report.longrepr),
        "keywords": sorted(str(keyword) for keyword in item.keywords),
    }
    (FAILURE_ROOT / f"{safe_name}.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


@pytest.fixture()
def client(tmp_path: Path):
    db_path = tmp_path / "test.sqlite"
    with TestClient(create_app(db_path)) as test_client:
        yield test_client


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture(scope="session")
def live_server(tmp_path_factory: pytest.TempPathFactory):
    port = _free_port()
    db_path = tmp_path_factory.mktemp("e2e-db") / "shop.sqlite"
    env = os.environ.copy()
    env["AI_QA_DB_PATH"] = str(db_path)
    for name in PROVIDER_ENV_NAMES:
        env.pop(name, None)
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    base_url = f"http://127.0.0.1:{port}"
    try:
        deadline = time.time() + 15
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(f"{base_url}/health", timeout=1) as response:
                    if response.status == 200:
                        yield base_url
                        return
            except OSError as exc:
                if process.poll() is not None:
                    output = process.stdout.read() if process.stdout else ""
                    raise RuntimeError(f"Server exited early. Output: {output}") from exc
                time.sleep(0.2)
        raise RuntimeError("Server did not start within 15 seconds.")
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=10)
