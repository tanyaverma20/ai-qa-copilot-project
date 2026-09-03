# 中文面试 Walkthrough

## 30 秒项目介绍

这是一个把自动化测试和 AI 缺陷诊断结合起来的 Python portfolio 项目。它先用 FastAPI 做一个可复现的电商 Demo，再用 pytest 和 Playwright 跑 API 与浏览器 E2E 测试。测试失败后，项目会收集 failure artifact，并通过 AI diagnosis 生成包含证据、分类、诊断假设和修复建议的报告。

我想展示的不是“会写几条测试”，而是能把被测系统、测试框架、CI、失败产物、LLM provider、安全脱敏和面试展示串成完整工程闭环。

## 本地演示顺序

面试时我会按这个顺序演示：

1. 先打开 Dashboard：`http://127.0.0.1:8000`，用 30 秒讲清平台能力。
2. 点击“进入 Demo Shop”，登录 `alice / password123`。
3. 创建一笔订单，说明 Demo Shop 是真实被测业务系统。
4. 在订单成功页解释：下单成功不是终点，它只是 E2E 测试场景。
5. 如果这个流程失败，项目会把失败整理成 failure JSON、AI diagnosis 和 `pr-comment.md`。
6. 最后打开 `qa-reports` 或 `reports/examples/sample-ai-diagnosis.md`，讲 Failure Mode Matrix。

这条线可以总结成：

```text
Dashboard -> Demo Shop 下单 -> failure artifacts -> AI diagnosis -> PR comment preview -> qa-reports
```

## 技术栈

- Python
- FastAPI
- pytest
- Playwright Python
- GitHub Actions
- OpenAI / DeepSeek / OpenAI-compatible provider adapter
- Markdown report
- PowerShell verification script

## 自动化测试价值

这个项目里的自动化测试分三层：

- 服务层测试：验证登录、库存、下单等业务逻辑。
- API 测试：验证 HTTP 状态码、响应体、鉴权和错误处理。
- 浏览器 E2E 测试：用 Playwright 跑真实登录和下单流程。

它的价值在于测试失败后不是只留一段 traceback，而是把 nodeid、phase、duration、longrepr、keywords、截图和 trace 引用整理成 failure artifact。这样后续 AI diagnosis 和人工排查都有结构化证据。

## AI diagnosis 价值

AI diagnosis 不负责决定测试是否通过，pytest 和 Playwright 才是质量门禁。AI 的价值是把失败上下文变成更容易读的诊断材料。

报告会输出：

- 失败证据
- 候选根因 / 诊断假设
- 复现步骤
- 修复建议
- 风险提示
- Failure Mode Matrix

如果没有 API key、provider 配置无效或外部模型调用失败，项目会生成 fallback report，不影响 CI 保留测试报告和失败产物。

## Provider 安全设计

项目支持 OpenAI、DeepSeek 和 OpenAI-compatible provider。因为这是 public portfolio，provider 配置必须可观察但不能泄漏。

所以项目做了 Provider Status：

- 显示 provider 是否 ready。
- 显示 provider 和 API style。
- 显示 API key 是否 configured。
- 显示缺少哪些配置或配置错误。
- 不暴露 API key、base URL、model 或 key source。

这体现的是 AI 应用开发里的安全边界：页面和公开 API 可以告诉你系统是否可用，但不能把 secret、内部 gateway 地址或租户模型名展示出来。

## Failure Mode Matrix 怎么讲

Failure Mode Matrix 是这个项目最适合截图展示的部分。它把失败按模式分组，而不是只给一段长文本。

当前示例覆盖五类：

- Product/API behavior：业务或接口行为不符合预期。
- API contract：请求/响应契约和测试预期不一致。
- UI/E2E behavior：浏览器流程或页面状态异常。
- Flaky/timing：偶发失败、等待条件或 race condition。
- Environment/setup：fixture、数据库或测试环境 setup 失败。

面试时可以这样讲：普通测试报告告诉我“哪里失败”，Failure Mode Matrix 帮我进一步判断“这类失败应该怎么分流、证据是什么、下一步做什么”。

## CI Artifacts 证据链怎么讲

面试时我会把 CI artifact 当作项目闭环的证据来讲。GitHub Actions 跑完后会上传 `qa-reports` artifact，里面包含：

- `reports/latest/pytest-report.html`：pytest HTML 报告，说明自动化测试真实执行过。
- `reports/latest/failures/*.json`：结构化失败产物，是 AI diagnosis 的输入。
- `reports/latest/ai-diagnosis.md`：完整 AI 诊断报告或 fallback report。
- `reports/latest/pr-comment.md`：dry-run PR comment preview，展示未来接入 PR review workflow 的形态，但不会自动发真实评论。
- Playwright screenshots / traces：如 CI artifact 中存在，可以作为浏览器失败时的可视化证据。

这条链路可以这样总结：pytest / Playwright 发现问题 → failure artifacts 保存证据 → AI diagnosis 生成 Failure Mode Matrix → `pr-comment.md` 变成 review-friendly 摘要 → `qa-reports` artifact 保留完整证据链。

如果只是面试前想稳定演示，可以在 GitHub Actions 里手动触发 Demo Artifacts workflow。它通过 `workflow_dispatch` 生成基于 curated examples 的 `demo-qa-reports`，不调用 GitHub PR/Issues API，也不会自动评论 PR。

安全边界也要讲清楚：`pr-comment.md` 有 basic redaction，但完整 `qa-reports` artifact 可能包含 raw test logs、failure JSON、screenshots、traces、request/response snippets 或 stack traces。真实 proprietary systems 使用前必须 Review artifact，不能直接把内部日志公开。

## 我在项目里做了什么

可以这样表达：

我负责定义这个 portfolio 项目的目标和验收标准，把自动化测试能力和 AI 应用开发能力放在同一个工程场景里展示。我推动了这些重点：

- 设计 FastAPI demo shop，保证测试场景可复现。
- 用 pytest 和 Playwright 建立 API 与 E2E 测试闭环。
- 设计 failure artifact，让 AI diagnosis 有结构化输入。
- 推进 DeepSeek、OpenAI 和 OpenAI-compatible provider adapter。
- 要求 Provider Status 和 API health response 做脱敏，不暴露敏感配置。
- 用 CI、verify script、README、walkthrough 和截图资产把项目做成可 review 的 public portfolio。

Codex 作为实现助手参与编码，但需求选择、review 问题、安全边界和合并验收由我来主导。

## 后续扩展方向

如果继续做，我会按这个顺序扩展：

1. GitHub PR comment demo：CI 失败时把 AI diagnosis 摘要评论到 PR。
2. Diagnosis dashboard：展示历史失败、failure mode 趋势和修复建议。
3. Trace summarization：解析真实 Playwright trace、JUnit XML 或 Allure report，提供更完整证据。
4. Provider config resolver：把 provider 配置解析和 health 展示进一步拆成独立模块。
5. Public deployment：部署一个只读 demo，让面试官不用本地运行也能体验 Provider Status 和 Failure Mode Matrix。
