"""
VyaparMitra AI Business Copilot — Core Facade.
Provides the primary interface for natural language merchant queries in Hindi, Hinglish, and English,
strictly grounded in validated business data from Phases 1-4.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from src.copilot.config import CopilotConfig, load_copilot_config
from src.copilot.conversation.state import ConversationState
from src.copilot.intent.router import QueryRouter
from src.copilot.language.detector import LanguageDetector
from src.copilot.llm import LLMProvider, get_llm_provider
from src.copilot.prompts import format_prompt, get_system_prompt
from src.copilot.retrieval.business_query import BusinessQueryEngine
from src.copilot.retrieval.context_builder import ContextBuilder
from src.copilot.retrieval.knowledge_retriever import KnowledgeRetriever
from src.copilot.schemas import (
    BusinessContext,
    CopilotResponse,
    Intent,
    Language,
    QueryPlan,
    ValidationResult,
)
from src.copilot.validation.response_validator import ResponseValidator


class VyaparMitraCopilot:
    """
    Main conversational interface for the VyaparMitra business copilot.
    """

    def __init__(
        self,
        config: Optional[CopilotConfig] = None,
        session_id: Optional[str] = None,
        merchant_id: Optional[str] = None,
    ):
        self.config: CopilotConfig = config or load_copilot_config()
        self.language_detector = LanguageDetector()
        self.query_router = QueryRouter()
        self.query_engine = BusinessQueryEngine(data_dir=self.config.data_dir)
        self.knowledge_retriever = KnowledgeRetriever(knowledge_dir=self.config.knowledge_path)
        self.context_builder = ContextBuilder(
            query_engine=self.query_engine,
            knowledge_retriever=self.knowledge_retriever,
        )
        self.llm_provider: LLMProvider = get_llm_provider(self.config)
        self.validator = ResponseValidator(enforce_strict=self.config.validation_enforce_grounding)
        self.state = ConversationState(
            session_id=session_id,
            merchant_id=merchant_id or self.config.default_merchant_id,
        )

    def ask(
        self,
        query: str,
        merchant_id: Optional[str] = None,
        language_override: Optional[Union[Language, str]] = None,
    ) -> CopilotResponse:
        """
        Executes a single conversational query turn:
        1. Language detection / override
        2. Intent routing & entity extraction with state memory
        3. Context retrieval across Phases 1-4 & Knowledge Base
        4. Grounded LLM generation
        5. Response validation & anti-hallucination check
        6. State update and structured response packaging
        """
        clean_query = query.strip()
        m_id = merchant_id or self.state.merchant_id

        # 1. Determine language
        if language_override:
            target_lang = (
                language_override
                if isinstance(language_override, Language)
                else Language(language_override.lower())
            )
        else:
            target_lang = self.language_detector.detect(clean_query)

        # 2. Intent and Entity routing with State
        query_plan: QueryPlan = self.query_router.route(
            query=clean_query,
            merchant_id=m_id,
            language=target_lang,
            state=self.state,
        )

        # 3. Retrieve Business Context
        context: BusinessContext = self.context_builder.build_context(
            query_plan=query_plan,
            query=clean_query,
            merchant_id=m_id,
        )

        # 4. Prompt Construction & Generation
        prompt = format_prompt(clean_query, context, target_lang)
        system_prompt = get_system_prompt()

        raw_answer = self.llm_provider.generate(
            prompt=prompt,
            context=context,
            system_prompt=system_prompt,
        )

        # 5. Validation & Anti-Hallucination Guard
        final_answer, validation_res = self.validator.validate_and_sanitize(
            answer=raw_answer,
            context=context,
        )

        # 6. Record turn in state
        self.state.record_turn(
            query=clean_query,
            answer=final_answer,
            intent=query_plan.intent,
            entities=query_plan.entities,
            language=target_lang,
        )

        # 7. Package CopilotResponse
        now_str = datetime.now(timezone.utc).isoformat()
        return CopilotResponse(
            answer=final_answer,
            intent=query_plan.intent.value,
            language=target_lang.value,
            sources=context.source_references,
            evidence=context.evidence,
            recommendations=context.recommendations,
            confidence=0.95 if validation_res.valid else 0.70,
            validation=validation_res,
            generated_at=now_str,
        )

    def generate_daily_brief(
        self,
        merchant_id: Optional[str] = None,
        language: Optional[Union[Language, str]] = None,
    ) -> CopilotResponse:
        """
        Generates a consolidated merchant morning briefing covering sales, 7-day forecast,
        and high-priority daily actions.
        """
        lang = language or self.state.last_language or Language.HINGLISH
        brief_query = (
            "Mujhe aaj ka poora business summary aur daily action plan batao"
            if lang == Language.HINGLISH
            else ("मुझे आज की व्यापार सारांश और दैनिक कार्य योजना बताएं" if lang == Language.HINDI else "Give me today's business summary and daily action plan")
        )
        return self.ask(query=brief_query, merchant_id=merchant_id, language_override=lang)

    def explain_recommendation(
        self,
        recommendation_id: str,
        merchant_id: Optional[str] = None,
        language: Optional[Union[Language, str]] = None,
    ) -> CopilotResponse:
        """
        Explains the specific analytical and predictive evidence behind a recommendation.
        """
        lang = language or self.state.last_language or Language.HINGLISH
        query = (
            f"Is recommendation {recommendation_id} ka kaaran kya hai?"
            if lang == Language.HINGLISH
            else (f"इस सुझाव {recommendation_id} का क्या कारण है?" if lang == Language.HINDI else f"What is the evidence behind recommendation {recommendation_id}?")
        )
        return self.ask(query=query, merchant_id=merchant_id, language_override=lang)
