from __future__ import annotations

from pathlib import Path

README = Path("README.md")
WALKTHROUGH = Path("docs/portfolio-walkthrough.md")
SCREENSHOTS_DOC = Path("docs/screenshots.md")
SCREENSHOT_SCRIPT = Path("scripts/capture-portfolio-screenshots.ps1")
RESUME_ZH = Path("docs/resume-zh.md")
INTERVIEW_QA_ZH = Path("docs/interview-qa.md")
INTERVIEW_WALKTHROUGH_ZH = Path("docs/interview-walkthrough-zh.md")
INTERVIEW_DEMO_SCRIPT_ZH = Path("docs/interview-demo-script-zh.md")
APPLICATION_PACKAGE_ZH = Path("docs/application-package-zh.md")
DEMO_FLOW = Path("docs/demo-flow.md")
SAMPLE_PR_COMMENT = Path("reports/examples/sample-pr-comment.md")
CI_WORKFLOW = Path(".github/workflows/ci.yml")
DEMO_WORKFLOW = Path(".github/workflows/demo-artifacts.yml")
CI_ARTIFACTS_DOC = Path("docs/ci-artifacts.md")
VISUAL_ASSETS = (
    Path("docs/assets/provider-status.png"),
    Path("docs/assets/failure-mode-matrix.png"),
)
CHINESE_INTERVIEW_DOCS = (
    README,
    RESUME_ZH,
    INTERVIEW_QA_ZH,
    INTERVIEW_WALKTHROUGH_ZH,
    INTERVIEW_DEMO_SCRIPT_ZH,
    APPLICATION_PACKAGE_ZH,
)
MOJIBAKE_PATTERNS = (
    "锟",
    "娑",
    "鐠",
    "閸",
    "閻",
    "閿",
    "閵",
    "缁",
    "鈧",
)


def test_readme_links_portfolio_walkthrough():
    readme = README.read_text(encoding="utf-8")

    assert "[Portfolio Walkthrough](docs/portfolio-walkthrough.md)" in readme
    assert "3-minute interview path" in readme
    assert "Chinese Showcase Dashboard" in readme
    assert "http://127.0.0.1:8000/login" in readme


def test_readme_front_page_summarizes_portfolio_value():
    readme = README.read_text(encoding="utf-8")

    for phrase in (
        "End-to-end QA automation",
        "Failure evidence pipeline",
        "AI-assisted diagnosis",
        "Provider safety",
        "CI portfolio artifacts",
    ):
        assert phrase in readme


def test_portfolio_walkthrough_covers_demo_story():
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")

    assert "Provider Status" in walkthrough
    assert "python -m qa_copilot.cli --input reports/examples" in walkthrough
    assert "Failure Mode Matrix" in walkthrough
    assert "reports/examples/sample-ai-diagnosis.md" in walkthrough
    assert "DeepSeek" in walkthrough


def test_portfolio_walkthrough_mentions_demo_security_boundaries():
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")

    assert "local demo credentials only" in walkthrough
    assert "avoid sending proprietary logs to third-party providers" in walkthrough


def test_portfolio_visual_assets_are_documented():
    readme = README.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")

    assert "docs/assets/provider-status.png" in readme
    assert "docs/assets/failure-mode-matrix.png" in readme
    assert "assets/provider-status.png" in walkthrough
    assert "assets/failure-mode-matrix.png" in walkthrough
    for asset in VISUAL_ASSETS:
        assert asset.exists()
        assert asset.stat().st_size > 5_000


def test_portfolio_screenshot_capture_process_is_documented():
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")
    screenshots_doc = SCREENSHOTS_DOC.read_text(encoding="utf-8")
    script = SCREENSHOT_SCRIPT.read_text(encoding="utf-8")

    assert "[Screenshot Capture](screenshots.md)" in walkthrough
    assert "scripts\\capture-portfolio-screenshots.ps1" in screenshots_doc
    assert "docs/assets/provider-status.png" in screenshots_doc
    assert "docs/assets/failure-mode-matrix.png" in screenshots_doc
    assert "demo-provider-key-for-screenshot-only" in script
    assert "fake key text leaked into Provider Status screenshot" in script
    assert "tenant.internal.example" in script
    assert "$LASTEXITCODE" in script
    assert "Screenshot capture failed" in script


def test_chinese_interview_docs_do_not_contain_common_mojibake():
    for path in CHINESE_INTERVIEW_DOCS:
        text = path.read_text(encoding="utf-8")
        for pattern in MOJIBAKE_PATTERNS:
            assert pattern not in text, f"{path} contains mojibake-like text: {pattern}"


def test_readme_links_chinese_interview_materials():
    readme = README.read_text(encoding="utf-8")

    assert "中文面试材料 / Chinese Interview Prep" in readme
    assert "docs/resume-zh.md" in readme
    assert "docs/interview-qa.md" in readme
    assert "docs/interview-walkthrough-zh.md" in readme
    assert "docs/interview-demo-script-zh.md" in readme
    assert "docs/application-package-zh.md" in readme


def test_chinese_interview_docs_cover_current_project_story():
    resume = RESUME_ZH.read_text(encoding="utf-8")
    qa = INTERVIEW_QA_ZH.read_text(encoding="utf-8")
    walkthrough = INTERVIEW_WALKTHROUGH_ZH.read_text(encoding="utf-8")

    combined = "\n".join((resume, qa, walkthrough))

    for phrase in (
        "FastAPI",
        "pytest",
        "Playwright",
        "GitHub Actions",
        "Provider Status",
        "Failure Mode Matrix",
        "DeepSeek",
        "OpenAI-compatible",
        "API key",
        "脱敏",
        "不暴露",
    ):
        assert phrase in combined


def test_chinese_interview_docs_cover_ci_artifact_story():
    combined = "\n".join(
        (
            RESUME_ZH.read_text(encoding="utf-8"),
            INTERVIEW_QA_ZH.read_text(encoding="utf-8"),
            INTERVIEW_WALKTHROUGH_ZH.read_text(encoding="utf-8"),
        )
    )

    for phrase in (
        "qa-reports",
        "pytest-report.html",
        "failures/*.json",
        "ai-diagnosis.md",
        "pr-comment.md",
        "Failure Mode Matrix",
        "dry-run",
        "证据链",
    ):
        assert phrase in combined


def test_chinese_interview_docs_explain_artifact_safety_boundary():
    combined = "\n".join(
        (
            INTERVIEW_QA_ZH.read_text(encoding="utf-8"),
            INTERVIEW_WALKTHROUGH_ZH.read_text(encoding="utf-8"),
        )
    )

    for phrase in (
        "basic redaction",
        "raw test logs",
        "screenshots",
        "traces",
        "Review artifact",
        "proprietary",
    ):
        assert phrase in combined


def test_chinese_walkthrough_is_a_three_minute_interview_script():
    walkthrough = INTERVIEW_WALKTHROUGH_ZH.read_text(encoding="utf-8")

    for heading in (
        "## 30 秒项目介绍",
        "## 本地演示顺序",
        "## 技术栈",
        "## 自动化测试价值",
        "## AI diagnosis 价值",
        "## Provider 安全设计",
        "## Failure Mode Matrix 怎么讲",
        "## CI Artifacts 证据链怎么讲",
        "## 我在项目里做了什么",
        "## 后续扩展方向",
    ):
        assert heading in walkthrough


def test_chinese_demo_script_explains_order_flow_and_next_steps():
    script = INTERVIEW_DEMO_SCRIPT_ZH.read_text(encoding="utf-8")

    for phrase in (
        "买商品只是被测业务场景",
        "下单成功不是终点",
        "Dashboard -> Demo Shop order -> QA reports",
        "failure JSON",
        "AI diagnosis",
        "pr-comment.md",
        "Failure Mode Matrix",
        "Provider Status",
        "不调用 GitHub PR/Issues API",
        "不会自动发评论",
    ):
        assert phrase in script


def test_application_package_is_copy_ready_for_job_search():
    package = APPLICATION_PACKAGE_ZH.read_text(encoding="utf-8")

    for phrase in (
        "简历项目经历 4 条 bullet",
        "3 分钟演示讲稿",
        "Dashboard -> Demo Shop 下单 -> failure artifacts",
        "候选根因 / 诊断假设",
        "不调用 GitHub PR/Issues API",
        "不会自动评论 PR",
        "Provider Status",
        "DeepSeek",
        "pytest",
        "Playwright",
        "投递前检查清单",
        "项目级别定位",
    ):
        assert phrase in package


def test_portfolio_walkthrough_explains_order_flow_purpose():
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")

    assert "Dashboard -> Demo Shop order -> QA reports" in walkthrough
    assert "What Happens After Buying A Product" in walkthrough
    assert "Buying a product is not the product goal." in walkthrough
    assert "system under test" in walkthrough


def test_pr_comment_preview_is_documented():
    readme = README.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")
    demo_flow = DEMO_FLOW.read_text(encoding="utf-8")

    assert "python -m qa_copilot.pr_comment" in readme
    assert "reports/examples/sample-pr-comment.md" in readme
    assert "Optional PR Comment Preview" in walkthrough
    assert "sample-pr-comment.md" in walkthrough
    assert "PR comment preview" in demo_flow


def test_sample_pr_comment_exists_and_is_safe():
    text = SAMPLE_PR_COMMENT.read_text(encoding="utf-8")

    assert "AI QA Copilot Diagnosis Preview" in text
    assert "Dry-run PR comment preview" in text
    assert "Failure Mode Matrix" in text
    assert "Recommended next steps" in text
    assert "reports/examples/sample-ai-diagnosis.md" in text
    assert "basic secret-like redaction" in text
    assert "Review generated comments before posting to public PRs" in text
    assert "sk-" not in text
    assert "Bearer " not in text


def test_ci_generates_pr_comment_preview_artifact():
    workflow = CI_WORKFLOW.read_text(encoding="utf-8")

    assert "Generate AI diagnosis" in workflow
    assert "Generate PR comment preview" in workflow
    assert "python -m qa_copilot.pr_comment" in workflow
    assert "reports/latest/ai-diagnosis.md" in workflow
    assert "reports/latest/pr-comment.md" in workflow
    assert "actions/upload-artifact" in workflow
    assert "path: reports/" in workflow
    assert workflow.index("Generate AI diagnosis") < workflow.index(
        "Generate PR comment preview"
    )
    assert workflow.index("Generate PR comment preview") < workflow.index("Upload reports")


def test_ci_pr_comment_preview_stays_dry_run():
    workflow = CI_WORKFLOW.read_text(encoding="utf-8")

    assert "GITHUB_TOKEN" not in workflow
    assert "github-script" not in workflow
    assert "createComment" not in workflow


def test_docs_describe_ci_pr_comment_preview_artifact():
    readme = README.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")
    demo_flow = DEMO_FLOW.read_text(encoding="utf-8")
    combined = "\n".join((readme, walkthrough, demo_flow))

    assert "reports/latest/pr-comment.md" in combined
    assert "qa-reports" in combined
    assert "does not call GitHub PR/Issues API" in combined
    assert "does not post comments" in combined
    assert "CI artifacts may still contain raw test logs or traces" in combined


def test_readme_links_ci_artifacts_guide():
    readme = README.read_text(encoding="utf-8")

    assert "CI Artifacts" in readme
    assert "qa-reports" in readme
    assert "docs/ci-artifacts.md" in readme


def test_ci_artifacts_guide_lists_key_outputs():
    text = CI_ARTIFACTS_DOC.read_text(encoding="utf-8")

    for phrase in (
        "qa-reports",
        "reports/latest/pytest-report.html",
        "reports/latest/ai-diagnosis.md",
        "reports/latest/pr-comment.md",
        "reports/latest/failures/*.json",
        "screenshots",
        "traces",
    ):
        assert phrase in text


def test_ci_artifacts_guide_explains_safety_boundary():
    text = CI_ARTIFACTS_DOC.read_text(encoding="utf-8")

    assert "basic redaction" in text
    assert "raw test logs" in text
    assert "traces" in text
    assert "Review artifacts" in text
    assert "proprietary systems" in text


def test_demo_artifacts_workflow_is_manual_only():
    workflow = DEMO_WORKFLOW.read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert "pull_request_target" not in workflow
    assert "pull_request:" not in workflow
    assert "push:" not in workflow


def test_demo_artifacts_workflow_uses_read_only_permissions():
    workflow = DEMO_WORKFLOW.read_text(encoding="utf-8")

    assert "permissions:" in workflow
    assert "contents: read" in workflow
    assert "persist-credentials: false" in workflow


def test_demo_artifacts_workflow_stays_dry_run():
    workflow = DEMO_WORKFLOW.read_text(encoding="utf-8")

    for phrase in (
        "GITHUB_TOKEN",
        "secrets.",
        "GH_TOKEN",
        "github-script",
        "createComment",
        "gh pr comment",
        "gh api",
        "issues: write",
        "pull-requests: write",
    ):
        assert phrase not in workflow


def test_demo_artifacts_workflow_uses_curated_examples():
    workflow = DEMO_WORKFLOW.read_text(encoding="utf-8")

    assert "reports/examples" in workflow
    assert "sample-ai-diagnosis.md" in workflow
    assert "reports/demo" in workflow
    assert "demo-qa-reports" in workflow
    assert "python -m qa_copilot.pr_comment" in workflow


def test_docs_explain_manual_demo_artifact_boundary():
    readme = README.read_text(encoding="utf-8")
    ci_artifacts = CI_ARTIFACTS_DOC.read_text(encoding="utf-8")
    combined = "\n".join((readme, ci_artifacts))

    assert "workflow_dispatch" in combined
    assert "demo-qa-reports" in combined
    assert "curated" in combined
    assert "does not post comments" in combined
    assert "does not call GitHub PR/Issues API" in combined
    assert "Review artifacts" in combined
