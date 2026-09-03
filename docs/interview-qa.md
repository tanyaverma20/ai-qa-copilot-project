# 面试问答准备

## 1. 这个项目解决什么问题？

这个项目解决的是自动化测试失败后的分析效率问题。传统自动化测试通常只能告诉我们“哪个用例失败了”，但排查时还要人工去看日志、断言、接口响应、截图和 trace。这个项目把失败上下文收集成结构化 JSON，再用 AI diagnosis 生成缺陷诊断报告，帮助快速判断是产品 bug、接口契约漂移、UI/E2E 行为问题、flaky timing 问题，还是环境和 fixture setup 问题。

## 2. 为什么要自己写一个 FastAPI Demo 系统？

因为只写测试脚本不容易展示完整测试工程能力。自己构建被测系统后，可以稳定复现登录、商品查询、下单、库存不足等场景，也能控制测试数据和失败样例。这样面试官能看到从被测服务、自动化测试、CI 到失败分析的完整闭环。

## 3. pytest 在项目里负责什么？

pytest 是统一测试入口。项目里用它跑三类测试：

- 服务层测试，验证登录、库存、下单等业务逻辑。
- API 测试，验证 HTTP 状态码、响应体和鉴权行为。
- Playwright E2E 测试，验证真实浏览器里的登录和下单流程。

同时 `tests/conftest.py` 里使用 pytest hook，在用例失败时自动保存 nodeid、phase、duration、longrepr 和 keywords，形成后续 AI diagnosis 可以读取的 failure artifact。

## 4. Playwright 在项目里负责什么？

Playwright 负责浏览器端到端测试。它不是只调接口，而是真的启动浏览器访问页面，完成登录、进入商品页、创建订单等用户流程。这样可以发现接口正常但页面流程异常的问题。失败时还可以保留截图和 trace 引用，让 AI diagnosis 和人工排查都有证据。

## 5. AI diagnosis 模块怎么工作？

AI diagnosis 模块分成五步：

1. 读取 `reports/latest/failures/*.json` 或 `reports/examples/*.json` 里的失败产物。
2. 把失败用例、phase、报错、耗时、keywords 和证据引用组装成 prompt。
3. 按 failure mode 分组，让输出包含 Failure Mode Matrix。
4. 如果配置了 OpenAI、DeepSeek 或 OpenAI-compatible provider，就通过 provider adapter 调用模型。
5. 如果没有 API key、provider 配置无效或 AI 调用失败，就生成 fallback report，不影响测试和 CI。

## 6. 为什么 AI 调用失败不能让 CI 失败？

因为自动化测试本身才是核心质量门禁，AI 是辅助分析能力。如果 AI 服务超时、限流、没有配置 API key，CI 仍然应该保留 pytest 报告和失败产物，不能因为辅助功能失败而遮住真正的测试结果。这个项目把测试执行和 AI diagnosis 解耦，AI 不稳定时仍能生成 fallback report。

## 7. Provider Status 为什么要做脱敏？

Provider Status 的作用是让面试官或维护者看到当前 AI provider 是否 ready，比如 provider、API style、API key 是否配置、缺少哪些配置。但它不能暴露敏感信息，所以公开 API 和 UI 都只显示 redacted readiness，不显示 API key、base URL、model 或 key source。

这个设计体现了 AI 应用开发里的安全边界：演示环境需要可观察性，但不能把 secret、内部 gateway 地址或租户模型名放到页面上。

## 8. Failure Mode Matrix 有什么价值？

普通测试报告主要告诉你哪条测试失败。Failure Mode Matrix 更进一步，把失败按模式归类：

- Product/API behavior
- API contract
- UI/E2E behavior
- Flaky/timing
- Environment/setup

这样报告可以同时回答三个问题：失败证据是什么，可能属于哪类问题，下一步应该谁去处理。对 QA 自动化来说，这比单纯堆日志更适合团队协作和面试展示。

## 9. CI artifacts 怎么展示项目价值？

CI 不是只看绿不绿。这个项目会在 GitHub Actions 里上传 `qa-reports` artifact，把测试执行和失败分析的证据链保留下来。

我会重点展示这些文件：`reports/latest/pytest-report.html` 说明 pytest / Playwright 真实执行过；`reports/latest/failures/*.json` 保存结构化失败证据；`reports/latest/ai-diagnosis.md` 输出 AI diagnosis 或 fallback report；`reports/latest/pr-comment.md` 是 dry-run PR comment preview，展示未来接入 PR review workflow 的形态，但当前不会自动评论 PR，也不需要 GitHub token。

这条链路说明项目不只是跑测试，而是把测试失败转成可审阅的工程产物：failure JSON 作为输入，AI diagnosis 生成 Failure Mode Matrix，`pr-comment.md` 生成 review-friendly 摘要，最后由 `qa-reports` artifact 保留完整证据链。

安全边界也要说清楚：`pr-comment.md` 有 basic redaction，但完整 artifact 仍可能包含 raw test logs、screenshots、traces、request/response snippets 或 stack traces。真实 proprietary systems 使用前必须 Review artifact，不能直接公开内部日志。

## 10. AI diagnosis 和普通测试报告有什么区别？

普通测试报告更偏原始事实，比如 nodeid、assertion、traceback、截图和耗时。AI diagnosis 会把这些事实组织成可读诊断：证据、分类、候选根因/诊断假设、复现步骤、修复建议和风险。它不替代 pytest 或 Playwright，而是把失败产物变成更容易行动的分析材料。

## 11. 这个项目体现了哪些自动化测试能力？

- pytest fixture 管理测试数据库。
- 参数清晰的 API 测试。
- Playwright 浏览器 E2E 测试。
- 测试失败产物收集。
- pytest HTML 报告。
- GitHub Actions CI。
- 失败场景样例和可复现 demo flow。

## 12. 这个项目体现了哪些 AI 应用开发能力？

- 把 AI 放入真实工程流程，而不是单独做聊天 demo。
- 设计 prompt，把测试失败上下文转成结构化输入。
- 支持 OpenAI、DeepSeek 和 OpenAI-compatible provider。
- 做 provider health validation，避免配置错误时仍尝试调用模型。
- 做 Provider Status redaction，不暴露 API key、base URL、model 或 key source。
- 输出 Markdown 报告，方便 CI 上传和人工阅读。
- 在 AI 不可用时生成 fallback report，保证主流程可靠。

## 13. 你在项目里具体做了什么？

可以这样回答：

我负责定义项目目标和验收标准，把它从“自动化测试 demo”推进成“AI QA Copilot portfolio 项目”。我重点把控了几个方向：被测系统和测试闭环、失败 artifact schema、AI diagnosis 输出结构、DeepSeek/OpenAI-compatible provider adapter、Provider Status 的安全脱敏、CI 验证、README walkthrough 和面试展示材料。Codex 作为实现助手参与编码，但需求取舍、review 重点、安全边界和最终验收由我来推动。

## 14. 如果继续扩展，你会做什么？

可以继续扩展四个方向：

- 增加 GitHub PR comment demo，在 CI 失败时自动评论 AI diagnosis 摘要。
- 增加 diagnosis dashboard，展示历史失败、分类趋势和修复建议。
- 解析真实 Playwright trace、JUnit XML 或 Allure report，让证据更完整。
- 把 provider config resolver 从 health 模块中进一步抽出，做成更清晰的配置层。

## 15. 面试时一句话总结

这是一个面向求职展示的 AI 自动化测试平台：它用 Python 完成真实 Web/API 测试工程流程，并把 AI 接入失败分析环节，展示我从自动化测试向 AI 应用开发迁移的能力。
