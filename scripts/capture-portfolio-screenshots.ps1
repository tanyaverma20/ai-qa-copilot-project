param(
    [int]$Port = 8010
)

$ErrorActionPreference = "Stop"

function Wait-ForHealth {
    param([string]$Url)

    $deadline = (Get-Date).AddSeconds(30)
    do {
        try {
            $response = Invoke-RestMethod -Uri $Url -TimeoutSec 2
            if ($response.status -eq "ok") {
                return
            }
        } catch {
            Start-Sleep -Milliseconds 500
        }
    } while ((Get-Date) -lt $deadline)

    throw "Timed out waiting for $Url"
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$reportsDir = Join-Path $repoRoot "reports\latest"
New-Item -ItemType Directory -Force -Path $reportsDir | Out-Null

$outLog = Join-Path $reportsDir "portfolio-screenshots-server.out.log"
$errLog = Join-Path $reportsDir "portfolio-screenshots-server.err.log"
$server = $null
$previousProvider = $env:AI_PROVIDER
$previousDeepSeekKey = $env:DEEPSEEK_API_KEY
$previousBaseUrl = $env:AI_BASE_URL

try {
    $env:AI_PROVIDER = "deepseek"
    $env:DEEPSEEK_API_KEY = "demo-provider-key-for-screenshot-only"
    $env:AI_BASE_URL = "https://tenant.internal.example/v1"

    $server = Start-Process `
        -FilePath python `
        -ArgumentList @(
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "$Port"
        ) `
        -WorkingDirectory $repoRoot `
        -PassThru `
        -WindowStyle Hidden `
        -RedirectStandardOutput $outLog `
        -RedirectStandardError $errLog

    Wait-ForHealth "http://127.0.0.1:$Port/health"

    $python = @'
from pathlib import Path
import html
import re
import sys
from playwright.sync_api import sync_playwright

port = int(sys.argv[1])
assets = Path("docs/assets")
assets.mkdir(parents=True, exist_ok=True)

sample = Path("reports/examples/sample-ai-diagnosis.md").read_text(encoding="utf-8")
lines = sample.splitlines()
start = lines.index("| Failure Mode | Affected Test / Artifact | Evidence | Likely Classification | Next Action |")
end = start
while end < len(lines) and lines[end].startswith("|"):
    end += 1
rows = []
for line in lines[start:end]:
    rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])

headers = rows[0]
body_rows = rows[2:]

def inline_markdown(value: str) -> str:
    escaped = html.escape(value)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)

matrix_rows = []
for row in body_rows:
    matrix_rows.append("<tr>" + "".join(f"<td>{inline_markdown(cell)}</td>" for cell in row) + "</tr>")

matrix_html = f"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
  :root {{
    color-scheme: light;
    --bg: #f7f8fb;
    --surface: #ffffff;
    --text: #18212f;
    --muted: #647084;
    --border: #d7dde8;
    --soft: #eef6f4;
  }}
  body {{
    margin: 0;
    padding: 32px;
    background: var(--bg);
    color: var(--text);
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  }}
  .frame {{
    width: 1180px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    box-shadow: 0 14px 30px rgba(24, 33, 47, 0.08);
    overflow: hidden;
  }}
  header {{
    padding: 22px 26px;
    border-bottom: 1px solid var(--border);
  }}
  h1 {{
    margin: 0;
    font-size: 25px;
    line-height: 1.2;
  }}
  p {{
    margin: 8px 0 0;
    color: var(--muted);
    font-size: 14px;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
  }}
  th, td {{
    border-bottom: 1px solid var(--border);
    padding: 14px 16px;
    text-align: left;
    vertical-align: top;
    font-size: 13px;
    line-height: 1.42;
  }}
  th {{
    background: var(--soft);
    color: var(--muted);
    font-size: 12px;
    font-weight: 750;
    text-transform: uppercase;
  }}
  th:nth-child(1), td:nth-child(1) {{ width: 14%; }}
  th:nth-child(2), td:nth-child(2) {{ width: 27%; }}
  th:nth-child(3), td:nth-child(3) {{ width: 22%; }}
  th:nth-child(4), td:nth-child(4) {{ width: 17%; }}
  th:nth-child(5), td:nth-child(5) {{ width: 20%; }}
  tr:last-child td {{ border-bottom: 0; }}
  code {{
    padding: 2px 5px;
    border-radius: 4px;
    background: #f1f4f8;
    color: #0f513f;
    font-family: "Cascadia Code", Consolas, monospace;
    font-size: 12px;
    overflow-wrap: anywhere;
  }}
</style>
</head>
<body>
  <section class="frame">
    <header>
      <h1>Failure Mode Matrix</h1>
      <p>Curated QA failures grouped into actionable diagnosis categories.</p>
    </header>
    <table aria-label="Failure Mode Matrix">
      <thead><tr>{''.join(f'<th>{html.escape(header)}</th>' for header in headers)}</tr></thead>
      <tbody>{''.join(matrix_rows)}</tbody>
    </table>
  </section>
</body>
</html>
"""

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(viewport={"width": 1440, "height": 1100}, device_scale_factor=1)

    page = context.new_page()
    page.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
    page.get_by_role("button", name="Sign in").click()
    page.wait_for_url("**/products")
    provider = page.get_by_role("region", name="Provider Status")
    provider.wait_for(state="visible")
    provider_text = provider.inner_text()
    assert "Provider Status" in provider_text
    assert "Ready" in provider_text
    assert "demo-provider-key-for-screenshot-only" not in provider_text, "fake key text leaked into Provider Status screenshot"
    assert "DEEPSEEK_API_KEY" not in provider_text, "provider env var source leaked into Provider Status screenshot"
    assert "tenant.internal.example" not in provider_text, "internal base URL leaked into Provider Status screenshot"
    provider.screenshot(path=str(assets / "provider-status.png"))

    matrix_page = context.new_page()
    matrix_page.set_content(matrix_html, wait_until="load")
    matrix_page.locator(".frame").screenshot(path=str(assets / "failure-mode-matrix.png"))
    browser.close()

print("wrote docs/assets/provider-status.png")
print("wrote docs/assets/failure-mode-matrix.png")
'@

    $python | python - $Port
    if ($LASTEXITCODE -ne 0) {
        throw "Screenshot capture failed with exit code $LASTEXITCODE"
    }
} finally {
    if ($server) {
        Stop-Process -Id $server.Id -Force -ErrorAction SilentlyContinue
    }
    $env:AI_PROVIDER = $previousProvider
    $env:DEEPSEEK_API_KEY = $previousDeepSeekKey
    $env:AI_BASE_URL = $previousBaseUrl
}
