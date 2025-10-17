"""Utility helpers for font resolution.

This module centralizes the logic that picks the best matching font file
available in ``assets/fonts`` so the rest of the codebase can render Chinese
text when a compatible font is present.  We prioritise CJK-ready fonts and
fall back to the original Montserrat assets when no other option exists.
"""

from __future__ import annotations

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
    ("assets/fonts/Montserrat-Regular.ttf", "assets/fonts/Montserrat-Bold.ttf"),
)


def _existing_font_pair(candidates: Iterable[Tuple[str, str]]) -> tuple[str, str]:
    """Return the first candidate pair where both files exist."""

    for regular_path, bold_path in candidates:
        if Path(regular_path).is_file() and Path(bold_path).is_file():
            return regular_path, bold_path
    raise FileNotFoundError(
        "No valid font pair found. Please place a Chinese font (e.g. Noto Sans "
        "SC) under assets/fonts with both regular and bold weights."
    )


def resolve_font(bold: bool = False) -> str:
    """Return the font path that matches the requested weight.

    The function inspects :data:`FONT_CANDIDATES` and returns the first font path
    whose regular and bold files are both present on disk.  If no Chinese font is
    available, Montserrat is used as a graceful fallback.
    """

    regular_path, bold_path = _existing_font_pair(FONT_CANDIDATES)
    return bold_path if bold else regular_path


def load_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Build a ``pygame.font.Font`` object using the resolved font path."""

    font_path = resolve_font(bold=bold)
    return pygame.font.Font(font_path, size)

