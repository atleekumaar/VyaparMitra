"""
Command-Line Interface (CLI) for VyaparMitra Hindi AI Business Copilot.

Usage:
  python -m src.copilot
  python -m src.copilot --query "Kal kitni bikri hui thi?"
  python -m src.copilot --daily-brief
  python -m src.copilot --query "Agle 7 dino mein sales ka kya anumaan hai?" --language hinglish
"""

from __future__ import annotations

import argparse
import io
import json
import sys

# Configure UTF-8 stdout and stderr for Windows terminal encoding support
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

from src.copilot.config import load_copilot_config
from src.copilot.copilot import VyaparMitraCopilot
from src.copilot.schemas import Language



def print_banner():
    banner = """
===================================================================
   VYAPARMITRA AI BUSINESS COPILOT (व्यापारमित्र बिज़नेस साथी)
   Multilingual Intelligence for Small Merchants (Hindi / Hinglish / English)
===================================================================
Type your question below (or 'exit' / 'quit' to quit).
Examples:
  - Kal kitni bikri hui thi?
  - Agle hafte sales kitni hogi?
  - Kaunsa samaan khatam hone wala hai?
  - Aaj mujhe dukaan mein kya karna chahiye?
-------------------------------------------------------------------
"""
    print(banner)


def format_response_cli(resp) -> str:
    lines = [
        f"\n[VyaparMitra]:\n{resp.answer}",
        f"\n-- Grounding & Sources ({len(resp.sources)} sources) --",
    ]
    for s in resp.sources[:3]:
        lines.append(f"  * {s.source} -> {s.artifact} ({s.description or ''})")

    if resp.recommendations:
        lines.append(f"-- Recommendations Linked: {len(resp.recommendations)} --")
        for r in resp.recommendations[:2]:
            lines.append(f"  * [{r.get('type', 'ACTION')}] {r.get('sku', '')}: {r.get('action', '')}")

    lines.append(f"-- Validation: {'PASSED' if resp.validation.valid else 'FLAGGED'} (Confidence: {resp.confidence:.0%}) --\n")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="VyaparMitra Multilingual Business Copilot CLI")
    parser.add_argument("--query", "-q", type=str, help="Single query to ask the copilot")
    parser.add_argument("--daily-brief", "-b", action="store_true", help="Generate daily merchant brief")
    parser.add_argument("--language", "-l", choices=["hindi", "hinglish", "english"], default=None, help="Language override")
    parser.add_argument("--merchant-id", "-m", type=str, default=None, help="Target merchant ID")
    parser.add_argument("--json", action="store_true", help="Output response in JSON format")

    args = parser.parse_args()
    config = load_copilot_config()
    copilot = VyaparMitraCopilot(config=config, merchant_id=args.merchant_id)

    lang_enum = Language(args.language.lower()) if args.language else None

    # 1. Daily Brief Mode
    if args.daily_brief:
        resp = copilot.generate_daily_brief(merchant_id=args.merchant_id, language=lang_enum)
        if args.json:
            print(json.dumps(resp.model_dump(), indent=2, ensure_ascii=False))
        else:
            print(format_response_cli(resp))
        return

    # 2. Single Query Mode
    if args.query:
        resp = copilot.ask(query=args.query, merchant_id=args.merchant_id, language_override=lang_enum)
        if args.json:
            print(json.dumps(resp.model_dump(), indent=2, ensure_ascii=False))
        else:
            print(format_response_cli(resp))
        return

    # 3. Interactive REPL Mode
    print_banner()
    while True:
        try:
            user_input = input("Merchant > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q", "bye"):
                print("Dhanyawaad! VyaparMitra closing. Shubh Vyapar!")
                break

            resp = copilot.ask(query=user_input, merchant_id=args.merchant_id, language_override=lang_enum)
            if args.json:
                print(json.dumps(resp.model_dump(), indent=2, ensure_ascii=False))
            else:
                print(format_response_cli(resp))

        except (KeyboardInterrupt, EOFError):
            print("\nSession ended. Shubh Vyapar!")
            break


if __name__ == "__main__":
    main()
