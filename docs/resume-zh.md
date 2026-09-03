# 中文求职说明

## 项目定位

这个项目可以在简历里定位为：

> AI 自动化测试与缺陷诊断平台：基于 Python、FastAPI、pytest、Playwright、GitHub Actions 和 LLM Provider Adapter，构建从接口测试、浏览器 E2E 测试、失败产物收集到 AI 诊断报告生成的完整 QA 工程闭环。

它的价值不是“写了几个测试脚本”，而是展示你能把自动化测试做成一个可运行、可复现、可展示、可扩展的工程项目：

- 有真实被测系统，而不是只写孤立测试脚本。
- 有 API 测试、服务层测试和浏览器 E2E 测试。
- 有 CI、测试报告、失败 JSON、截图和 trace 引用。
- 有 AI diagnosis CLI，把失败上下文整理成结构化诊断报告。
- 有 OpenAI、DeepSeek、OpenAI-compatible provider adapter。
- 有 Provider Status UI，并且默认脱敏，不暴露 API key、base URL、model 或 key source。
- 有 Failure Mode Matrix，可以把失败归类为 Product/API、API contract、UI/E2E、Flaky/timing、Environment/setup。

## 简历写法

可以写成：

```text
AI 自动化测试与缺陷诊断平台 | Python / FastAPI / pytest / Playwright / GitHub Actions / LLM Provider Adapter
- 使用 FastAPI 构建电商 Demo 系统，覆盖登录、商品查询、创建订单、库存不足等可复现业务场景。
- 基于 pytest 设计接口自动化测试和服务层测试，使用 fixture 隔离测试数据库，并通过 hook 收集失败 JSON 产物。
- 使用 Playwright Python 实现浏览器 E2E 测试，覆盖登录和下单核心流程，并在失败时保留截图、trace 引用和测试上下文。
- 接入 GitHub Actions 自动运行 lint、API 测试、E2E 测试和 AI diagnosis，并上传测试报告、失败产物和诊断报告。
- 设计 AI diagnosis CLI，按 failure mode 生成包含证据、分类、候选根因、复现步骤和修复建议的 Failure Mode Matrix。
- 实现 OpenAI / DeepSeek / OpenAI-compatible provider adapter 与 Provider Status UI，默认脱敏 API key、base URL、model 和 key source。
```

## 面试讲解思路

面试时可以按这个顺序讲：

1. 我先做了一个小型 FastAPI 电商系统，作为稳定的被测对象。
2. 我用 pytest 覆盖接口和业务逻辑，用 fixture 保证每个测试有独立数据环境。
3. 我用 Playwright 测真实浏览器流程，验证登录和下单不只是接口层可用。
4. 当测试失败时，pytest hook 会把失败用例、phase、耗时、longrepr 和 keywords 写成 JSON artifact。
5. AI diagnosis 会读取这些 failure artifacts，并按 Failure Mode Matrix 输出证据、分类、候选根因和修复建议。
6. Provider 层支持 OpenAI、DeepSeek 和 OpenAI-compatible gateway，同时用 health check 和 Provider Status UI 展示 readiness。
7. Provider Status 和公开 API 默认脱敏，不暴露 API key、base URL、model 或 key source，适合 public portfolio 展示。
8. README、portfolio walkthrough、截图和截图复现脚本把项目包装成面试官可以快速理解的演示路径。

## 跳槽 AI 应用开发的说法

你可以强调：

> 我不是单独做一个聊天机器人 demo，而是把 AI 放进自动化测试失败分析这个具体工程场景里。这个项目展示了我能把 Python 自动化测试、CI、结构化 failure artifact、provider adapter、安全脱敏和 LLM 输出组织成一个完整 AI 应用流程。

这个说法能同时连接两个方向：

- 自动化测试方向：pytest、Playwright、fixture、CI、报告、失败产物、E2E 流程。
- AI 应用开发方向：provider adapter、配置健康检查、fallback report、prompt 组织、Failure Mode Matrix、安全脱敏。

## 可以重点展示的亮点

- **Provider Status**：页面能显示 provider 是否 ready，但不暴露 API key、base URL、model 或 key source。
- **Failure Mode Matrix**：报告不是散文，而是把失败按模式分组，方便判断优先级和责任边界。
- **DeepSeek / OpenAI-compatible 适配**：不是只写死 OpenAI，而是抽出 provider adapter，适合国内外不同模型服务。
- **CI 产物闭环**：测试失败后仍保留 pytest report、failure JSON 和 AI diagnosis report，AI 调用失败不会掩盖测试结果。
- **CI artifact 证据链**：GitHub Actions 会上传 `qa-reports`，包含 pytest HTML 报告、failure JSON、AI diagnosis report 和 dry-run PR comment preview，展示从测试失败到团队 review 摘要的完整闭环。
- **portfolio walkthrough**：项目有中文 Dashboard、3 分钟演示路线、下单成功后的 QA next steps、截图和截图复现脚本，面试官不跑项目也能看懂核心价值。
