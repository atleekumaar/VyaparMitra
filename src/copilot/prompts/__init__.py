"""
Prompts package for VyaparMitra Copilot.
"""

from typing import Union

from src.copilot.prompts.english_prompt import format_english_prompt
from src.copilot.prompts.hindi_prompt import format_hindi_prompt
from src.copilot.prompts.hinglish_prompt import format_hinglish_prompt
from src.copilot.prompts.system_prompt import get_system_prompt
from src.copilot.schemas import BusinessContext, Language


def format_prompt(query: str, context: BusinessContext, language: Union[Language, str]) -> str:
    """Dispatches prompt construction based on target language."""
    lang_str = language.value if isinstance(language, Language) else str(language).lower()

    if lang_str == Language.HINDI.value:
        return format_hindi_prompt(query, context)
    elif lang_str == Language.ENGLISH.value:
        return format_english_prompt(query, context)
    else:
        return format_hinglish_prompt(query, context)


__all__ = [
    "get_system_prompt",
    "format_prompt",
    "format_hindi_prompt",
    "format_hinglish_prompt",
    "format_english_prompt",
]
