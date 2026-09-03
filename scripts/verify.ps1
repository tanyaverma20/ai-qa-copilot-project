$ErrorActionPreference = "Stop"

function Invoke-Checked {
  param(
    [Parameter(Mandatory = $true)]
    [string] $Command,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $Arguments
  )

  & $Command @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "Command failed with exit code ${LASTEXITCODE}: $Command $($Arguments -join ' ')"
  }
}

Write-Host "==> Running Ruff"
Invoke-Checked ruff check .

Write-Host "==> Running pytest and Playwright"
Invoke-Checked pytest -q --browser chromium --tracing retain-on-failure --screenshot only-on-failure

Write-Host "==> Generating demo AI diagnosis report"
Invoke-Checked python -m qa_copilot.cli --input reports/examples --output reports/latest/demo-ai-diagnosis.md

if (-not (Test-Path "reports/latest/demo-ai-diagnosis.md")) {
  throw "Demo AI diagnosis report was not generated."
}

Write-Host "==> Verification complete"
