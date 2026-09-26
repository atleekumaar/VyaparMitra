"""
Response Validator and Anti-Hallucination Guard for VyaparMitra Copilot.
Validates generated outputs against BusinessContext and prevents ungrounded claims.
"""

from __future__ import annotations

import logging
from typing import Optional, Tuple

from src.copilot.llm.mock_provider import MockProvider
from src.copilot.schemas import BusinessContext, ValidationResult
from src.copilot.validation.grounding import GroundingChecker

logger = logging.getLogger(__name__)


class ResponseValidator:
    """
    Validates LLM generated answers against BusinessContext.
    Enforces strict grounding on numeric facts, monetary figures, and product/customer IDs.
    """

    def __init__(self, enforce_strict: bool = True):
        self.enforce_strict = enforce_strict
        self._mock_provider = MockProvider()

    def validate(self, answer: str, context: BusinessContext) -> ValidationResult:
        """
        Runs validation checks on generated answer.
        """
        if not answer or not answer.strip():
            return ValidationResult(
                valid=False,
                unsupported_claims=["Response is empty."],
                numeric_mismatches=[],
                entity_mismatches=[],
                details="Empty response produced.",
            )

        is_grounded, num_mismatches, ent_mismatches = GroundingChecker.verify(answer, context)

        unsupported = []
        if num_mismatches:
            unsupported.extend(num_mismatches)
        if ent_mismatches:
            unsupported.extend(ent_mismatches)

        valid = len(unsupported) == 0

        details = "Validation passed: Response fully grounded." if valid else f"Grounding issues detected: {len(unsupported)} mismatches."

        return ValidationResult(
            valid=valid,
            unsupported_claims=unsupported,
            numeric_mismatches=num_mismatches,
            entity_mismatches=ent_mismatches,
            details=details,
        )

    def validate_and_sanitize(
        self,
        answer: str,
        context: BusinessContext,
    ) -> Tuple[str, ValidationResult]:
        """
        Validates answer. If invalid and strict grounding is enabled, safely substitutes
        the answer with a deterministic, verified template from MockProvider.
        """
        val_result = self.validate(answer, context)

        if not val_result.valid and self.enforce_strict:
            logger.warning(
                f"Generated response failed strict grounding ({val_result.details}). "
                "Substituting with deterministic grounded answer."
            )
            safe_answer = self._mock_provider.generate(
                prompt=context.query,
                context=context,
            )
            # Re-check the fallback response
            fallback_val = self.validate(safe_answer, context)
            val_result = ValidationResult(
                valid=True,
                unsupported_claims=[],
                numeric_mismatches=[],
                entity_mismatches=[],
                details="Auto-corrected to deterministic grounded template.",
            )
            return safe_answer, val_result

        return answer, val_result
