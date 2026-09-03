import os
import sqlite3
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.db import connect, initialize_database, seed_database
from app.schemas import (
    DiagnosisRequest,
    DiagnosisResponse,
    LoginRequest,
    LoginResponse,
    OrderRequest,
    ProviderHealthResponse,
)
from app.services import (
    AuthenticationError,
    InsufficientStockError,
    ProductNotFoundError,
    authenticate_user,
    create_order,
    get_product,
    list_products,
    token_for_username,
    username_from_token,
)
from qa_copilot.artifacts import FailureArtifact, load_failure_artifacts
from qa_copilot.diagnosis import diagnose_with_ai
from qa_copilot.prompt_builder import build_diagnosis_prompt
from qa_copilot.provider_health import check_provider_health
from qa_copilot.providers import supported_provider_specs

templates = Jinja2Templates(directory="app/templates")

PROVIDER_ISSUE_LABELS = {
    "api_key": "AI 服务未连接",
    "base_url": "AI 服务未连接",
    "model": "缺少模型配置",
    "unsupported_provider": "不支持的 AI 服务",
    "unsupported_api_style": "AI 服务配置需检查",
}

PROVIDER_ISSUE_HINTS = {
    "api_key": "如需现场生成诊断，请先连接 AI 服务。",
    "base_url": "如需使用兼容网关，请先完成服务连接配置。",
    "model": "为当前 AI 服务配置模型。",
    "unsupported_provider": "检查 AI 服务名称是否拼写正确。",
    "unsupported_api_style": "检查 AI 服务调用方式配置。",
}

DASHBOARD_VALUE_CARDS = [
    {
        "title": "端到端 QA 自动化",
        "body": (
            "FastAPI 被测系统配合 pytest API/service tests 与 Playwright E2E，"
            "覆盖从接口到浏览器的关键路径。"
        ),
    },
    {
        "title": "失败证据链",
        "body": (
            "测试失败会沉淀测试报告、结构化失败证据，以及可用时的浏览器截图或调试附件。"
        ),
    },
    {
        "title": "AI 辅助诊断",
        "body": "把失败上下文组织成 Failure Mode Matrix，输出证据、分类、候选根因和下一步建议。",
    },
    {
        "title": "AI 服务安全边界",
        "body": "AI 服务状态可观察，但不展示密钥或内部配置。",
    },
    {
        "title": "CI 作品集产物",
        "body": "真实 CI 报告包与安全演示报告包，让面试官不用复现失败，也能看到完整 QA 交付物。",
    },
]

DASHBOARD_PIPELINE_STEPS = [
    "pytest / Playwright",
    "结构化失败证据",
    "AI 诊断",
    "Failure Mode Matrix",
    "PR 摘要预览",
    "CI 报告包",
]

FAILURE_MODE_ROWS = [
    {
        "mode": "Product/API behavior",
        "example": "库存不足返回状态码不符合预期",
        "evidence": "API status mismatch",
        "next_action": "检查业务异常到 HTTP 409 的映射。",
    },
    {
        "mode": "API contract",
        "example": "请求/响应契约漂移",
        "evidence": "422 validation error",
        "next_action": "对齐 request body、schema 和测试契约。",
    },
    {
        "mode": "UI/E2E behavior",
        "example": "Playwright 等待按钮可见失败",
        "evidence": "locator visibility assertion",
        "next_action": "检查页面状态、按钮禁用逻辑和截图证据。",
    },
    {
        "mode": "Flaky/timing",
        "example": "搜索结果偶发失败",
        "evidence": "10 次运行中失败 3 次",
        "next_action": "稳定等待条件，排查 debounce / fetch race。",
    },
    {
        "mode": "Environment/setup",
        "example": "fixture 初始化数据库失败",
        "evidence": "no such table during setup",
        "next_action": "检查 fixture 顺序、迁移和测试隔离。",
    },
]

ARTIFACT_CARDS = [
    {
        "title": "CI 报告包",
        "kind": "真实 CI 产物",
        "body": (
            "CI 上传的测试报告、结构化失败证据、AI 诊断和 PR 摘要预览。"
        ),
    },
    {
        "title": "演示报告包",
        "kind": "手动生成的安全演示报告包",
        "body": "基于安全示例数据生成，适合稳定面试展示，不代表当前真实故障。",
    },
]


def _resolve_db_path(db_path: str | Path | None) -> str | Path:
    if db_path is not None:
        return db_path
    return os.getenv("AI_QA_DB_PATH", "reports/latest/dev.sqlite")


def _extract_bearer_token(authorization: str | None) -> str:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    return authorization.removeprefix("Bearer ").strip()


def _provider_health_view_model() -> dict[str, object]:
    health = check_provider_health()
    missing = [str(item) for item in health["missing"]]
    errors = [str(item) for item in health["errors"]]
    issue_codes = [*errors, *missing]
    issues = [
        {
            "label": PROVIDER_ISSUE_LABELS.get(code, code.replace("_", " ").title()),
            "hint": PROVIDER_ISSUE_HINTS.get(code, "检查 AI 服务环境变量配置。"),
        }
        for code in issue_codes
    ]
    return {
        "ok": health["ok"],
        "provider": health["provider"],
        "api_style": health["api_style"],
        "api_key_configured": health["api_key_configured"],
        "status_label": "已就绪" if health["ok"] else issues[0]["label"],
        "issues": issues,
    }


def _dashboard_context(db: sqlite3.Connection) -> dict[str, object]:
    sample_artifacts = load_failure_artifacts("reports/examples")
    provider_specs = supported_provider_specs()
    return {
        "provider_health": _provider_health_view_model(),
        "product_count": len(list_products(db)),
        "sample_artifact_count": len(sample_artifacts),
        "provider_count": len(provider_specs),
        "provider_names": list(provider_specs),
        "value_cards": DASHBOARD_VALUE_CARDS,
        "pipeline_steps": DASHBOARD_PIPELINE_STEPS,
        "failure_mode_rows": FAILURE_MODE_ROWS,
        "artifact_cards": ARTIFACT_CARDS,
    }


def create_app(db_path: str | Path | None = None) -> FastAPI:
    resolved_db_path = _resolve_db_path(db_path)

    @asynccontextmanager
    async def lifespan(api: FastAPI) -> AsyncIterator[None]:
        if resolved_db_path != ":memory:":
            Path(resolved_db_path).parent.mkdir(parents=True, exist_ok=True)
        connection = connect(resolved_db_path)
        initialize_database(connection)
        seed_database(connection)
        api.state.db = connection
        try:
            yield
        finally:
            connection.close()

    api = FastAPI(title="AI QA Copilot Demo Shop", lifespan=lifespan)
    api.mount("/static", StaticFiles(directory="app/static"), name="static")

    def get_db() -> sqlite3.Connection:
        return api.state.db

    def current_username(authorization: str | None = Header(default=None)) -> str:
        token = _extract_bearer_token(authorization)
        try:
            return username_from_token(token)
        except AuthenticationError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    def products_context(
        username: str,
        db: sqlite3.Connection,
        error: str = "",
    ) -> dict[str, object]:
        return {
            "username": username,
            "products": list_products(db),
            "error": error,
            "provider_health": _provider_health_view_model(),
        }

    DbConnection = Annotated[sqlite3.Connection, Depends(get_db)]
    CurrentUsername = Annotated[str, Depends(current_username)]

    @api.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @api.post("/api/login", response_model=LoginResponse)
    def login(payload: LoginRequest, db: DbConnection) -> LoginResponse:
        try:
            user = authenticate_user(db, payload.username, payload.password)
        except AuthenticationError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc
        return LoginResponse(access_token=token_for_username(user["username"]))

    @api.get("/api/products")
    def products(db: DbConnection) -> list[dict[str, object]]:
        return list_products(db)

    @api.get("/api/products/{product_id}")
    def product_detail(
        product_id: int,
        db: DbConnection,
    ) -> dict[str, object]:
        try:
            return get_product(db, product_id)
        except ProductNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @api.post("/api/orders", status_code=201)
    def order_create(
        payload: OrderRequest,
        username: CurrentUsername,
        db: DbConnection,
    ) -> dict[str, object]:
        try:
            return create_order(db, username, payload.product_id, payload.quantity)
        except ProductNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except InsufficientStockError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @api.post("/api/diagnosis", response_model=DiagnosisResponse)
    def diagnosis_create(payload: DiagnosisRequest) -> DiagnosisResponse:
        artifact = FailureArtifact(
            nodeid=payload.nodeid,
            failed_at=payload.failed_at,
            phase=payload.phase,
            duration_seconds=payload.duration_seconds,
            longrepr=payload.longrepr,
            keywords=payload.keywords,
        )
        prompt = build_diagnosis_prompt([artifact])
        report = diagnose_with_ai(prompt)
        return DiagnosisResponse(artifact_count=1, report_markdown=report)

    @api.get("/api/ai-providers")
    def ai_providers() -> dict[str, dict[str, dict[str, object]]]:
        return {"providers": supported_provider_specs()}

    @api.get("/api/provider-health", response_model=ProviderHealthResponse)
    def provider_health() -> ProviderHealthResponse:
        return ProviderHealthResponse(**check_provider_health())

    @api.get("/", response_class=HTMLResponse)
    def dashboard_page(request: Request, db: DbConnection) -> HTMLResponse:
        return templates.TemplateResponse(
            request,
            "dashboard.html",
            _dashboard_context(db),
        )

    @api.get("/login", response_class=HTMLResponse)
    def login_page(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "login.html", {"error": ""})

    @api.post("/login", response_model=None)
    async def web_login(
        request: Request,
        db: DbConnection,
    ) -> HTMLResponse | RedirectResponse:
        form = await request.form()
        username = str(form.get("username", ""))
        password = str(form.get("password", ""))
        try:
            authenticate_user(db, username, password)
        except AuthenticationError:
            return templates.TemplateResponse(
                request,
                "login.html",
                {"error": "用户名或密码错误"},
                status_code=401,
            )
        response = RedirectResponse("/products", status_code=303)
        response.set_cookie("qa_user", username, httponly=True)
        return response

    @api.get("/products", response_class=HTMLResponse, response_model=None)
    def products_page(
        request: Request,
        db: DbConnection,
    ) -> HTMLResponse | RedirectResponse:
        username = request.cookies.get("qa_user")
        if not username:
            return RedirectResponse("/login", status_code=303)
        return templates.TemplateResponse(
            request,
            "products.html",
            products_context(username, db),
        )

    @api.post("/orders", response_model=None)
    async def web_order(
        request: Request,
        db: DbConnection,
    ) -> HTMLResponse | RedirectResponse:
        username = request.cookies.get("qa_user")
        if not username:
            return RedirectResponse("/login", status_code=303)
        form = await request.form()
        product_id = int(str(form.get("product_id", "0")))
        quantity = int(str(form.get("quantity", "1")))
        try:
            order = create_order(db, username, product_id, quantity)
        except ProductNotFoundError:
            return templates.TemplateResponse(
                request,
                "products.html",
                products_context(username, db, "商品不存在。"),
                status_code=409,
            )
        except InsufficientStockError:
            return templates.TemplateResponse(
                request,
                "products.html",
                products_context(username, db, "库存不足，无法创建订单。"),
                status_code=409,
            )
        return templates.TemplateResponse(
            request,
            "order_success.html",
            {"username": username, "order": order},
        )

    return api


app = create_app()
