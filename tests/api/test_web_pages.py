from __future__ import annotations

from tests.helpers import clear_provider_env


def get_signed_in_products_page(client):
    client.cookies.set("qa_user", "alice")
    return client.get("/products")


def test_dashboard_page_renders_portfolio_story(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "AI 自动化测试与缺陷诊断平台" in response.text
    assert "pytest / Playwright" in response.text
    assert "Failure Mode Matrix" in response.text
    assert "CI 报告包" in response.text
    assert "演示报告包" in response.text


def test_dashboard_explains_ai_and_artifact_boundaries(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "候选根因" in response.text
    assert "诊断假设" in response.text
    assert "安全演示样例" in response.text
    assert "不展示密钥或内部配置" in response.text
    assert "不代表当前真实故障" in response.text


def test_dashboard_hides_internal_implementation_details(client):
    response = client.get("/")

    assert response.status_code == 200
    for phrase in (
        "API Docs",
        "Provider Health API",
        "GitHub PR/Issues API",
        "raw logs",
        "stack traces",
        "provider preset",
        "reports/latest",
        "reports/examples",
        "qa-reports",
        "demo-qa-reports",
        "pytest-report.html",
        "failure JSON",
        "pr-comment.md",
    ):
        assert phrase not in response.text


def test_dashboard_explains_interview_demo_path(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "面试演示路径" in response.text
    assert "先看 Dashboard" in response.text
    assert "进入 Demo Shop 下单" in response.text
    assert "再看 CI 报告包" in response.text
    assert "下单流程只是被测业务场景" in response.text


def test_dashboard_provider_status_is_redacted(client, monkeypatch):
    clear_provider_env(monkeypatch)
    monkeypatch.setenv("AI_PROVIDER", "openai-compatible")
    monkeypatch.setenv("AI_API_KEY", "fake-gateway-key")
    monkeypatch.setenv("AI_MODEL", "tenant-routed-model")
    monkeypatch.setenv("AI_BASE_URL", "https://tenant.internal.example/v1")

    response = client.get("/")

    assert response.status_code == 200
    assert "AI 服务状态" in response.text
    assert "已就绪" in response.text
    assert "openai-compatible" in response.text
    assert "隐藏内部配置" in response.text
    assert "API 风格" not in response.text
    assert "密钥状态" not in response.text
    assert "fake-gateway-key" not in response.text
    assert "AI_API_KEY" not in response.text
    assert "tenant-routed-model" not in response.text
    assert "tenant.internal.example" not in response.text


def test_login_page_renders(client):
    response = client.get("/login")

    assert response.status_code == 200
    assert "AI QA 演示商店" in response.text
    assert "用户名" in response.text
    assert "密码" in response.text


def test_login_page_links_stylesheet(client):
    response = client.get("/login")

    assert response.status_code == 200
    assert 'href="/static/styles.css"' in response.text


def test_web_login_redirects_to_products(client):
    response = client.post(
        "/login",
        data={"username": "alice", "password": "password123"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/products"


def test_products_page_requires_login(client):
    response = client.get("/products", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_order_success_page_explains_qa_next_steps(client):
    client.cookies.set("qa_user", "alice")

    response = client.post("/orders", data={"product_id": "1", "quantity": "1"})

    assert response.status_code == 200
    assert "订单创建成功" in response.text
    assert "这一步证明 Demo Shop 是真实被测系统" in response.text
    assert "下单成功不是终点" in response.text
    assert "如果这里失败" in response.text
    assert "失败证据" in response.text
    assert "AI 诊断" in response.text
    assert "PR 摘要预览" in response.text
    assert "返回 Dashboard" in response.text
    assert "继续测试下单" in response.text


def test_order_success_page_hides_file_paths_and_raw_api_links(client):
    client.cookies.set("qa_user", "alice")

    response = client.post("/orders", data={"product_id": "1", "quantity": "1"})

    assert response.status_code == 200
    for phrase in (
        "API Docs",
        "Provider Health API",
        "reports/latest",
        "reports/examples",
        "pr-comment.md",
    ):
        assert phrase not in response.text


def test_demo_pages_hide_api_docs_nav(client):
    login_response = client.get("/login")
    client.cookies.set("qa_user", "alice")
    products_response = client.get("/products")

    assert login_response.status_code == 200
    assert products_response.status_code == 200
    assert "API Docs" not in login_response.text
    assert "API Docs" not in products_response.text


def test_products_page_shows_redacted_provider_status(client, monkeypatch):
    clear_provider_env(monkeypatch)
    monkeypatch.setenv("AI_PROVIDER", "openai-compatible")
    monkeypatch.setenv("AI_API_KEY", "fake-gateway-key")
    monkeypatch.setenv("AI_MODEL", "tenant-routed-model")
    monkeypatch.setenv("AI_BASE_URL", "https://tenant.internal.example/v1")

    response = get_signed_in_products_page(client)

    assert response.status_code == 200
    assert "AI 服务状态" in response.text
    assert "已就绪" in response.text
    assert "openai-compatible" in response.text
    assert "隐藏内部配置" in response.text
    assert "API 风格" not in response.text
    assert "密钥状态" not in response.text
    assert "fake-gateway-key" not in response.text
    assert "AI_API_KEY" not in response.text
    assert "tenant-routed-model" not in response.text
    assert "tenant.internal.example" not in response.text


def test_products_page_shows_missing_base_url_provider_status(client, monkeypatch):
    clear_provider_env(monkeypatch)
    monkeypatch.setenv("AI_PROVIDER", "openai-compatible")
    monkeypatch.setenv("AI_API_KEY", "fake-gateway-key")

    response = get_signed_in_products_page(client)

    assert response.status_code == 200
    assert "AI 服务状态" in response.text
    assert "AI 服务未连接" in response.text
    assert "如需使用兼容网关，请先完成服务连接配置。" in response.text


def test_products_page_shows_unsupported_provider_status(client, monkeypatch):
    clear_provider_env(monkeypatch)
    monkeypatch.setenv("AI_PROVIDER", "deepssek")
    monkeypatch.setenv("AI_API_KEY", "fake-key")

    response = get_signed_in_products_page(client)

    assert response.status_code == 200
    assert "AI 服务状态" in response.text
    assert "不支持的 AI 服务" in response.text
    assert "检查 AI 服务名称是否拼写正确。" in response.text
    assert "fake-key" not in response.text


def test_products_page_shows_unsupported_api_style_status(client, monkeypatch):
    clear_provider_env(monkeypatch)
    monkeypatch.setenv("AI_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "fake-deepseek-key")
    monkeypatch.setenv("AI_API_STYLE", "chta")

    response = get_signed_in_products_page(client)

    assert response.status_code == 200
    assert "AI 服务状态" in response.text
    assert "AI 服务配置需检查" in response.text
    assert "检查 AI 服务调用方式配置。" in response.text
    assert "fake-deepseek-key" not in response.text
