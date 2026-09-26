"""
Grounding verification and claim extraction for VyaparMitra Copilot.
Extracts numbers, currency tokens, and entity identifiers from generated responses
and verifies them against BusinessContext.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Set, Tuple

from src.copilot.schemas import BusinessContext


class GroundingChecker:
    """
    Checks if numbers, monetary figures, and entity IDs mentioned in an LLM answer
    are grounded in the provided BusinessContext.
    """

    @staticmethod
    def extract_numbers(text: str) -> List[float]:
        """
        Extracts numeric values (integers and floats) from text,
        ignoring standard serial list numbers like '1.', '2.', etc.
        """
        # Remove list markers like '1.', '2. '
        cleaned = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
        # Find currency amounts, commas, decimals
        raw_matches = re.findall(r"₹?\s*([0-9]+(?:,[0-9]+)*(?:\.[0-9]+)?)", cleaned)
        numbers = []
        for m in raw_matches:
            val_str = m.replace(",", "").strip()
            if not val_str:
                continue
            try:
                numbers.append(float(val_str))
            except ValueError:
                continue
        return numbers

    @staticmethod
    def extract_entities(text: str) -> Set[str]:
        prd_matches = set(re.findall(r"\b(?:PRD[_-][A-Za-z0-9_]+|SKU[_-][A-Za-z0-9_]+)\b", text, re.IGNORECASE))

        cust_matches = set(re.findall(r"\bCUST[_-][A-Za-z0-9]+\b|\bC[0-9]{3,}\b", text, re.IGNORECASE))
        return {e.upper() for e in (prd_matches | cust_matches)}

    @classmethod
    def get_context_numbers(cls, context: BusinessContext) -> Set[float]:
        """Collects all numeric values present in context metrics, facts, and recommendations."""
        nums = set()

        def _collect(val: Any) -> None:
            if isinstance(val, (int, float)):
                nums.add(round(float(val), 2))
                nums.add(float(int(val)))
            elif isinstance(val, dict):
                for v in val.values():
                    _collect(v)
            elif isinstance(val, (list, tuple)):
                for item in val:
                    _collect(item)
            elif isinstance(val, str):
                for n in cls.extract_numbers(val):
                    nums.add(round(n, 2))
                    nums.add(float(int(n)))

        _collect(context.metrics)
        _collect(context.recommendations)
        _collect(context.evidence)
        for f in context.facts:
            _collect(f.value)

        return nums

    @classmethod
    def get_context_entities(cls, context: BusinessContext) -> Set[str]:
        """Collects all entity identifiers present in context."""
        entities = set()

        def _collect(val: Any) -> None:
            if isinstance(val, str):
                for e in cls.extract_entities(val):
                    entities.add(e)
            elif isinstance(val, dict):
                for k, v in val.items():
                    if "id" in k.lower() or "sku" in k.lower() or "customer" in k.lower() or "product" in k.lower():
                        if isinstance(v, str):
                            entities.add(v.strip().upper())
                    _collect(v)
            elif isinstance(val, (list, tuple)):
                for item in val:
                    _collect(item)

        _collect(context.metrics)
        _collect(context.recommendations)
        _collect(context.evidence)
        for f in context.facts:
            _collect(f.key)
            _collect(f.value)

        return entities

    @classmethod
    def verify(
        cls,
        answer: str,
        context: BusinessContext,
        tolerance: float = 0.05,
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Verifies answer against context.
        Returns:
            (is_grounded, numeric_mismatches, entity_mismatches)
        """
        answer_nums = cls.extract_numbers(answer)
        ctx_nums = cls.get_context_numbers(context)

        # Filter out common small integers like 1, 2, 3, 7 (days in week), 30 (days in month)
        benign_numbers = {0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 10.0, 14.0, 30.0, 60.0, 90.0, 100.0}

        numeric_mismatches = []
        for an in answer_nums:
            if an in benign_numbers:
                continue
            # Check if an is within tolerance of any context number
            matched = False
            for cn in ctx_nums:
                if abs(an - cn) <= max(1.0, abs(cn) * tolerance):
                    matched = True
                    break
            if not matched:
                numeric_mismatches.append(f"Number {an} in answer not grounded in context metrics.")

        answer_entities = cls.extract_entities(answer)
        ctx_entities = cls.get_context_entities(context)

        entity_mismatches = []
        for ae in answer_entities:
            # Check if entity is present in context entities
            if not any(ae == ce or ce in ae or ae in ce for ce in ctx_entities):
                entity_mismatches.append(f"Entity '{ae}' in answer not found in context.")

        is_grounded = len(numeric_mismatches) == 0 and len(entity_mismatches) == 0
        return is_grounded, numeric_mismatches, entity_mismatches
