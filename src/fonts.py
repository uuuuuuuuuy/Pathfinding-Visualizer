"""Utility helpers for font resolution.

This module centralizes the logic that picks the best matching font file
available in ``assets/fonts`` so the rest of the codebase can render Chinese
text when a compatible font is present.  We prioritise CJK-ready fonts and
fall back to the original Montserrat assets when no other option exists.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Iterable, Tuple

import pygame

# Candidate font pairs ordered from most to least preferred.
# Each tuple stores (regular_path, bold_path).
FONT_CANDIDATES: tuple[tuple[str, str], ...] = (
    ("assets/fonts/NotoSansSC-Regular.otf", "assets/fonts/NotoSansSC-Bold.otf"),
    ("assets/fonts/NotoSansSC-Regular.ttf", "assets/fonts/NotoSansSC-Bold.ttf"),
    ("assets/fonts/SourceHanSansSC-Regular.otf", "assets/fonts/SourceHanSansSC-Bold.otf"),
    ("assets/fonts/SourceHanSans-Regular.otf", "assets/fonts/SourceHanSans-Bold.otf"),
    ("assets/fonts/MiSans-Regular.ttf", "assets/fonts/MiSans-Bold.ttf"),
    # Allow plain "regular" weights without a bold companion.
    ("assets/fonts/NotoSansSC-Regular.otf", "assets/fonts/NotoSansSC-Regular.otf"),
    ("assets/fonts/NotoSansSC-Regular.ttf", "assets/fonts/NotoSansSC-Regular.ttf"),
    ("assets/fonts/SourceHanSansSC-Regular.otf", "assets/fonts/SourceHanSansSC-Regular.otf"),
    ("assets/fonts/SourceHanSans-Regular.otf", "assets/fonts/SourceHanSans-Regular.otf"),
    ("assets/fonts/MiSans-Regular.ttf", "assets/fonts/MiSans-Regular.ttf"),
    ("assets/fonts/Montserrat-Regular.ttf", "assets/fonts/Montserrat-Bold.ttf"),
)


def _existing_font_pair(candidates: Iterable[Tuple[str, str]]) -> tuple[str, str]:
    """Return the first candidate pair whose files are present on disk.

    The search order prefers real bold weights, but gracefully degrades to a
    regular-only file so that users can drop a single Chinese font file in the
    directory without having to provide multiple variants.
    """

    fallback_regular: str | None = None

    for regular_path, bold_path in candidates:
        regular_exists = Path(regular_path).is_file()
        bold_exists = Path(bold_path).is_file()

        if regular_exists and bold_exists:
            return regular_path, bold_path

        if regular_exists and fallback_regular is None:
            fallback_regular = regular_path

    if fallback_regular is not None:
        return fallback_regular, fallback_regular

    raise FileNotFoundError(
        "No valid font found. Please place a Chinese font (e.g. Noto Sans SC) "
        "under assets/fonts; a single regular weight file is sufficient."
    )


@lru_cache(maxsize=2)
def _resolved_pair() -> tuple[str, str]:
    """Cache the resolved font lookup to avoid repeated filesystem scans."""

    return _existing_font_pair(FONT_CANDIDATES)


def resolve_font(bold: bool = False) -> str:
    """Return the font path that matches the requested weight.

    The function inspects :data:`FONT_CANDIDATES` and returns the first font path
    whose regular and bold files are both present on disk.  If no Chinese font is
    available, Montserrat is used as a graceful fallback.
    """

    regular_path, bold_path = _resolved_pair()
    return bold_path if bold else regular_path


def load_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Build a ``pygame.font.Font`` object using the resolved font path."""

    font_path = resolve_font(bold=bold)
    return pygame.font.Font(font_path, size)

