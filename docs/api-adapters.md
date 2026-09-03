# AI API Adapter Guide

AI QA Copilot keeps external AI calls behind a small provider layer so the test framework does not depend directly on one API call site.

## Provider Layer

The provider layer lives in:

```text
qa_copilot/providers.py
```

It currently includes:

- `DiagnosisProviderConfig`: reads API settings from environment variables.
- `DiagnosisProvider`: protocol for any diagnosis provider.
- `OpenAIResponsesProvider`: adapter for OpenAI's Responses API.

The diagnosis workflow uses the provider through:

```text
qa_copilot/diagnosis.py
```

This keeps failure handling and fallback behavior separate from API transport details.

## Recommended Environment Variables

```dotenv
AI_PROVIDER=openai
AI_API_KEY=
AI_MODEL=
AI_BASE_URL=
```

`AI_PROVIDER` selects the provider preset.

`AI_API_KEY` is the generic API key. Provider-specific keys are also supported.

`AI_MODEL` overrides the preset default model.

`AI_BASE_URL` overrides the preset base URL.

If no API key is configured, the CLI writes a fallback report instead of failing.

## Supported Provider Presets

List the same provider metadata from the CLI:

```powershell
python -m qa_copilot.cli --list-providers
```

Check the current provider configuration:

```powershell
python -m qa_copilot.cli --check-provider
```

The CLI prints detailed local diagnostics, including model, base URL, and which environment variable supplied the key. It never prints the key value itself.

Use `--fail-on-error` when a script should fail if the provider configuration is unhealthy:

```powershell
python -m qa_copilot.cli --check-provider --fail-on-error
```

Or from the demo app:

```text
GET /api/ai-providers
```

```text
GET /api/provider-health
```

The API health response is redacted for safe use in demos and future UI panels. It returns status fields such as `ok`, `provider`, `api_style`, `api_key_configured`, `missing`, and `errors`, but it does not expose model names, custom base URLs, or key environment variable names.

The demo products page renders the same redacted health status so the UI and diagnosis runtime share one view of provider readiness.

Known provider health errors:

- `unsupported_provider`: `AI_PROVIDER` is not one of the supported presets.
- `unsupported_api_style`: `AI_API_STYLE` is not `chat` or `responses`.

| Provider | API style | Default base URL | Default model | API key env |
| --- | --- | --- | --- | --- |
| `openai` | Responses API | OpenAI default | `gpt-4.1-mini` | `OPENAI_API_KEY` |
| `deepseek` | Chat Completions | `https://api.deepseek.com` | `deepseek-chat` | `DEEPSEEK_API_KEY` |
| `qwen` / `dashscope` | Chat Completions | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` | `DASHSCOPE_API_KEY` or `QWEN_API_KEY` |
| `kimi` / `moonshot` | Chat Completions | `https://api.moonshot.cn/v1` | `kimi-k2-0711-preview` | `MOONSHOT_API_KEY` or `KIMI_API_KEY` |
| `siliconflow` | Chat Completions | `https://api.siliconflow.cn/v1` | `deepseek-ai/DeepSeek-V3` | `SILICONFLOW_API_KEY` |
| `openrouter` | Chat Completions | `https://openrouter.ai/api/v1` | `deepseek/deepseek-chat-v3.1` | `OPENROUTER_API_KEY` |
| `doubao` | Chat Completions | `https://ark.cn-beijing.volces.com/api/v3` | `doubao-seed-1-6` | `ARK_API_KEY`, `VOLCENGINE_API_KEY`, or `DOUBAO_API_KEY` |
| `openai-compatible` | Chat Completions | set `AI_BASE_URL` | set `AI_MODEL` | `AI_API_KEY` |

## OpenAI Example

```powershell
$env:AI_PROVIDER="openai"
$env:AI_API_KEY="your-openai-key"
$env:AI_MODEL="gpt-4.1-mini"
python -m qa_copilot.cli --input reports/examples --output reports/latest/demo-ai-diagnosis.md
```

## DeepSeek Example

```powershell
$env:AI_PROVIDER="deepseek"
$env:DEEPSEEK_API_KEY="your-deepseek-key"
python -m qa_copilot.cli --input reports/examples --output reports/latest/demo-ai-diagnosis.md
```

## Qwen / DashScope Example

```powershell
$env:AI_PROVIDER="qwen"
$env:DASHSCOPE_API_KEY="your-dashscope-key"
python -m qa_copilot.cli --input reports/examples --output reports/latest/demo-ai-diagnosis.md
```

## Kimi / Moonshot Example

```powershell
$env:AI_PROVIDER="kimi"
$env:MOONSHOT_API_KEY="your-moonshot-key"
python -m qa_copilot.cli --input reports/examples --output reports/latest/demo-ai-diagnosis.md
```

## OpenRouter Example

```powershell
$env:AI_PROVIDER="openrouter"
$env:OPENROUTER_API_KEY="your-openrouter-key"
python -m qa_copilot.cli --input reports/examples --output reports/latest/demo-ai-diagnosis.md
```

## Custom OpenAI-Compatible Gateway Example

```powershell
$env:AI_PROVIDER="openai-compatible"
$env:AI_API_KEY="gateway-key"
$env:AI_MODEL="your-routed-model"
$env:AI_BASE_URL="https://gateway.example.com/v1"
python -m qa_copilot.cli --input reports/examples --output reports/latest/demo-ai-diagnosis.md
```

## Fallback Behavior

The AI diagnosis feature must not break CI. The CLI writes a fallback Markdown report when:

- `OPENAI_API_KEY` is missing
- `AI_PROVIDER` is unsupported
- `AI_API_STYLE` is not `chat` or `responses`
- a chat-style provider such as `openai-compatible` is missing `AI_BASE_URL`
- the API request times out
- the provider returns an error
- the configured gateway is unavailable

The normal pytest HTML report and JSON failure artifacts remain available even when AI diagnosis is skipped.

## Diagnosis HTTP Endpoint

The FastAPI demo app exposes `POST /api/diagnosis` for API-based integration demos.

Request body:

```json
{
  "nodeid": "tests/api/test_orders_api.py::test_create_order",
  "failed_at": "2026-07-02T10:00:00+00:00",
  "phase": "call",
  "duration_seconds": 0.12,
  "longrepr": "AssertionError: expected 409 but got 500",
  "keywords": ["api", "orders"]
}
```

Response body:

```json
{
  "artifact_count": 1,
  "report_markdown": "## Summary\n\n..."
}
```

This endpoint uses the same provider layer as the CLI, so it supports the same provider presets and environment variables.

## Adding Another Provider

To add another provider:

1. Create a class with `generate(prompt: str) -> str`.
2. Convert the provider's response into Markdown.
3. Inject that provider into `diagnose_with_ai()`.
4. Add unit tests that use a fake client and do not call the network.
