"""
Language detection and text normalization package.
"""
from src.copilot.language.detector import detect_language
from src.copilot.language.normalizer import normalize_text

__all__ = ["detect_language", "normalize_text"]
