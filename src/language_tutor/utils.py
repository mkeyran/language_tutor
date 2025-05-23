"""Utility functions for the Language Tutor application."""

from __future__ import annotations

import re
import urllib.parse


def build_wiktionary_url(word: str, language: str = "en") -> str:
    """Return the mobile Wiktionary URL for ``word`` in the given ``language``.

    Parameters
    ----------
    word:
        Word to look up.
    language:
        Two-letter language code such as ``"en"`` or ``"pl"``.  Only the
        first part before ``'-'`` is used.
    """
    if not word:
        return ""
    lang = (language or "en").split("-")[0]
    quoted = urllib.parse.quote(word)
    return f"https://{lang}.m.wiktionary.org/wiki/{quoted}"


def strip_html_tags(text: str) -> str:
    """Remove HTML tags from *text*.

    Parameters
    ----------
    text:
        String possibly containing HTML tags.

    Returns
    -------
    str
        The text with any ``<tag>`` markup removed.
    """

    if not text:
        return ""

    return re.sub(r"<[^>]+>", "", text)
