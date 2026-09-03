from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from qa_copilot.providers import DiagnosisProviderConfig
from qa_copilot.test_case_generator import (
    TestCaseGenerationResult,
    build_test_case_prompt,
    generate_test_cases,
    parse_test_cases_response,
)


@pytest.fixture
def mock_config() -> DiagnosisProviderConfig:
    return DiagnosisProviderConfig(
        api_key="mock-test-key-12345",
        provider="openai",
        model="gpt-4.1-mini",
        api_style="responses",
    )


@pytest.fixture
def sample_llm_json_response() -> str:
    test_cases_data = [
        {
            "test_case_id": "TC-001",
            "requirement_id": "REQ-SHOP-01",
            "scenario": "Verify valid product can be added to shopping cart",
            "preconditions": ["User is logged in", "Product is in stock"],
            "test_steps": [
                "Navigate to products page",
                "Select product 'Mechanical Keyboard'",
                "Click 'Add to Cart'",
            ],
            "expected_result": "Product is added to cart and stock count decreases by 1",
            "test_type": "Functional",
            "priority": "High",
        },
        {
            "test_case_id": "TC-002",
            "requirement_id": "REQ-SHOP-01",
            "scenario": "Attempt to add out-of-stock product to cart",
            "preconditions": ["User is logged in", "Product stock is 0"],
            "test_steps": [
                "Navigate to out-of-stock product page",
                "Click 'Add to Cart'",
            ],
            "expected_result": "Error alert displayed stating 'Product out of stock'",
            "test_type": "Negative",
            "priority": "High",
        },
        {
            "test_case_id": "TC-003",
            "requirement_id": "REQ-SHOP-01",
            "scenario": "Add maximum allowed quantity of product",
            "preconditions": ["User is logged in"],
            "test_steps": [
                "Enter quantity 9999",
                "Click 'Add to Cart'",
            ],
            "expected_result": "Quantity capped or validation error displayed",
            "test_type": "Boundary",
            "priority": "Medium",
        },
    ]
    return json.dumps(test_cases_data)


def test_build_test_case_prompt() -> None:
    prompt = build_test_case_prompt("User story: Add to cart", requirement_id="REQ-100")
    assert "REQ-100" in prompt
    assert "User story: Add to cart" in prompt
    assert "test_case_id" in prompt
    assert "preconditions" in prompt


def test_parse_test_cases_response_raw_json(sample_llm_json_response: str) -> None:
    test_cases = parse_test_cases_response(sample_llm_json_response, requirement_id="REQ-SHOP-01")
    assert len(test_cases) == 3
    assert test_cases[0].test_case_id == "TC-001"
    assert test_cases[0].test_type == "Functional"
    assert test_cases[0].priority == "High"
    assert test_cases[1].test_type == "Negative"
    assert test_cases[2].test_type == "Boundary"


def test_parse_test_cases_response_markdown_block(sample_llm_json_response: str) -> None:
    markdown_wrapped = f"```json\n{sample_llm_json_response}\n```"
    test_cases = parse_test_cases_response(markdown_wrapped, requirement_id="REQ-SHOP-01")
    assert len(test_cases) == 3
    assert test_cases[0].scenario == "Verify valid product can be added to shopping cart"


def test_parse_test_cases_response_invalid_json() -> None:
    test_cases = parse_test_cases_response(
        "This is not valid json text at all", requirement_id="REQ-01"
    )
    assert test_cases == []



def test_generate_test_cases_valid_input(
    mock_config: DiagnosisProviderConfig, sample_llm_json_response: str
) -> None:
    mock_provider = MagicMock()
    mock_provider.generate.return_value = sample_llm_json_response

    result: TestCaseGenerationResult = generate_test_cases(
        user_story="As a customer, I want to add items to cart.",
        requirement_id="REQ-SHOP-01",
        provider=mock_provider,
        config=mock_config,
    )

    assert result.ok is True
    assert result.requirement_id == "REQ-SHOP-01"
    assert len(result.test_cases) == 3
    assert result.error is None
    mock_provider.generate.assert_called_once()


def test_generate_test_cases_empty_input(mock_config: DiagnosisProviderConfig) -> None:
    mock_provider = MagicMock()

    with pytest.raises(ValueError, match="Requirement text cannot be empty or whitespace."):
        generate_test_cases(
            user_story="   ",
            requirement_id="REQ-001",
            provider=mock_provider,
            config=mock_config,
        )

    mock_provider.generate.assert_not_called()


def test_generate_test_cases_provider_unconfigured() -> None:
    empty_config = DiagnosisProviderConfig(
        api_key="",
        provider="openai",
        model="gpt-4.1-mini",
        api_style="responses",
    )

    result = generate_test_cases(
        user_story="Valid requirement text",
        requirement_id="REQ-001",
        config=empty_config,
    )

    assert result.ok is False
    assert result.test_cases == []
    assert "API key is not configured" in (result.error or "")


def test_generate_test_cases_provider_failure(mock_config: DiagnosisProviderConfig) -> None:
    mock_provider = MagicMock()
    mock_provider.generate.side_effect = RuntimeError("LLM Service Unavailable (503)")

    result = generate_test_cases(
        user_story="Valid requirement text",
        requirement_id="REQ-001",
        provider=mock_provider,
        config=mock_config,
    )

    assert result.ok is False
    assert result.test_cases == []
    assert "LLM Service Unavailable" in (result.error or "")
    mock_provider.generate.assert_called_once()
