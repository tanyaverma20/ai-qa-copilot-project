# Screenshot Capture

The README and portfolio walkthrough use two committed screenshots:

- `docs/assets/provider-status.png`
- `docs/assets/failure-mode-matrix.png`

Regenerate them from the repo root:

```powershell
scripts\capture-portfolio-screenshots.ps1
```

The script starts the FastAPI demo app on `127.0.0.1:8010`, logs in with the local demo account, captures the Provider Status card, renders the curated Failure Mode Matrix from `reports/examples/sample-ai-diagnosis.md`, and writes both PNG files into `docs/assets/`.

## Safety Checks

The Provider Status capture uses a fake key value, `demo-provider-key-for-screenshot-only`, only inside the local screenshot process. The script asserts that the screenshot DOM text does not expose:

- the fake key value
- `DEEPSEEK_API_KEY`
- `tenant.internal.example`

Use temporary demo credentials and avoid sending proprietary logs to third-party providers when generating public portfolio assets.
