from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
def test_user_can_login_and_create_order(page: Page, live_server: str):
    page.goto(live_server)

    expect(page.get_by_role("heading", name="AI 自动化测试与缺陷诊断平台")).to_be_visible()
    expect(page.get_by_role("heading", name="Failure Mode Matrix 示例")).to_be_visible()
    page.get_by_role("link", name="进入 Demo Shop").click()

    expect(page.get_by_role("heading", name="AI QA 演示商店")).to_be_visible()
    page.get_by_label("用户名").fill("alice")
    page.get_by_label("密码").fill("password123")
    page.get_by_role("button", name="登录").click()

    expect(page.get_by_role("heading", name="商品列表")).to_be_visible()
    provider_status = page.get_by_role("region", name="AI 服务状态")
    expect(provider_status.get_by_role("heading", name="AI 服务状态")).to_be_visible()
    expect(provider_status.locator(".provider-status-summary")).to_have_text("AI 服务未连接")
    first_product = page.get_by_role("article").filter(has_text="无线鼠标")
    first_product.get_by_role("button", name="创建订单").click()

    expect(page.get_by_role("heading", name="订单创建成功")).to_be_visible()
    expect(page.get_by_text("alice 已购买 1 件 无线鼠标。")).to_be_visible()
    expect(page.get_by_role("heading", name="下单成功不是终点")).to_be_visible()
    expect(page.get_by_role("link", name="返回 Dashboard")).to_be_visible()


@pytest.mark.e2e
def test_user_sees_error_for_bad_login(page: Page, live_server: str):
    page.goto(f"{live_server}/login")

    page.get_by_label("用户名").fill("alice")
    page.get_by_label("密码").fill("bad-password")
    page.get_by_role("button", name="登录").click()

    expect(page.get_by_role("alert")).to_have_text("用户名或密码错误")
