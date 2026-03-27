"""Shared language injection utility for all LLM clients in MiroFish."""
import os


def inject_language_header(messages: list, lang: str = None) -> list:
    """Prepend output-language instruction to the system message.

    No-ops when lang is 'Chinese' (preserves original OASIS behaviour).
    Applied in all LLM clients before every API call.

    Args:
        messages: List of chat message dicts with 'role' and 'content'.
        lang: Output language override. Defaults to OUTPUT_LANGUAGE env var.

    Returns:
        Messages list with language header prepended to the system message.
    """
    lang = lang or os.environ.get("OUTPUT_LANGUAGE", "English")
    if not lang or lang.strip().lower() == "chinese":
        return messages
    header = (
        f"IMPORTANT: You must respond entirely in {lang}. "
        f"All text, field values, summaries, and analysis must be written in {lang}. "
        f"Do not use Chinese or any other language.\n\n"
    )
    return [
        {**msg, "content": header + msg["content"]}
        if msg.get("role") == "system"
        else msg
        for msg in messages
    ]
