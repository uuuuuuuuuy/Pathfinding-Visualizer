"""Utility helpers for font resolution.

This module centralizes the logic that picks the best matching font file
available in ``assets/fonts`` so the rest of the codebase can render Chinese
text when a compatible font is present.  We prioritise CJK-ready fonts and
fall back to the original Montserrat assets when no other option exists.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Tuple

import pygame

# Candidate font pairs ordered from most to least preferred.
# Each tuple stores (regular_path, bold_path).
#
# We keep a curated shortlist for the most common Chinese font families, but the
# resolver also scans ``assets/fonts`` to pick up any other ``.ttf`` or ``.otf``
# that the user might have dropped into the directory.  This means users no
# longer have to rename their font files to match one of the hard-coded names.
STATIC_FONT_CANDIDATES: tuple[tuple[str, str], ...] = (
    ("assets/fonts/NotoSansSC-Regular.otf", "assets/fonts/NotoSansSC-Bold.otf"),
    ("assets/fonts/NotoSansSC-Regular.ttf", "assets/fonts/NotoSansSC-Bold.ttf"),
    ("assets/fonts/SourceHanSansSC-Regular.otf", "assets/fonts/SourceHanSansSC-Bold.otf"),
    ("assets/fonts/SourceHanSans-Regular.otf", "assets/fonts/SourceHanSans-Bold.otf"),
    ("assets/fonts/MiSans-Regular.ttf", "assets/fonts/MiSans-Bold.ttf"),
)

CJK_KEYWORDS: tuple[str, ...] = (
    "sc",
    "cn",
    "zh",
    "han",
    "hei",
    "yahei",
    "fang",
    "song",
    "kai",
    "noto",
    "sourcehan",
    "simsun",
    "simhei",
    "pingfang",
    "wenquanyi",
    "微软雅黑",
    "黑体",
    "仿宋",
    "楷体",
)

_STYLE_SUFFIX = re.compile(
    r"[-_ ]?(regular|bold|medium|semibold|demibold|black|heavy|light|thin|"
    r"extrabold|extrablack|book|normal|std|w[0-9]{2})$",
    re.IGNORECASE,
)

def _normalize_family(stem: str) -> str:
    """Return a simplified family name for grouping font variants."""

    normalized = _STYLE_SUFFIX.sub("", stem)
    return normalized.lower()


def _style_tag(stem: str) -> str:
    """Rudimentarily categorise a font file as ``regular`` or ``bold``."""

    lower = stem.lower()
    if re.search(r"(bold|black|heavy|extrabold|demibold|semibold|w[7-9][0-9])", lower):
        return "bold"
    return "regular"


def _discover_font_pairs(font_dir: Path) -> list[tuple[str, str]]:
    """Scan the font directory for available files and create candidate pairs."""

    if not font_dir.is_dir():
        return []

    font_files = [
        path for path in font_dir.iterdir()
        if path.suffix.lower() in {".ttf", ".otf"} and path.is_file()
    ]

    if not font_files:
        return []

    grouped: dict[str, dict[str, list[Path]]] = {}

    for font_path in font_files:
        family = _normalize_family(font_path.stem)
        styles = grouped.setdefault(family, {"regular": [], "bold": []})
        styles[_style_tag(font_path.stem)].append(font_path)

    candidates: list[tuple[Path, Path]] = []

    for styles in grouped.values():
        regular_candidates = styles["regular"] or styles["bold"]
        if not regular_candidates:
            continue

        regular_path = sorted(regular_candidates)[0]
        bold_path = sorted(styles["bold"])[0] if styles["bold"] else regular_path
        candidates.append((regular_path, bold_path))

    def score(pair: tuple[Path, Path]) -> tuple[int, str]:
        regular_path, _ = pair
        name = regular_path.stem.lower()

        if "montserrat" in name:
            return 2, name

        if any(keyword in name for keyword in CJK_KEYWORDS):
            return 0, name

        return 1, name

    candidates.sort(key=score)

    return [(str(regular), str(bold)) for regular, bold in candidates]


def _candidate_pairs() -> Iterable[tuple[str, str]]:
    """Yield curated and discovered font pairs without duplicates."""

    fonts_dir = Path("assets/fonts")
    discovered = _discover_font_pairs(fonts_dir)

    # Always include Montserrat as the ultimate fallback.
    discovered.append(("assets/fonts/Montserrat-Regular.ttf", "assets/fonts/Montserrat-Bold.ttf"))

    seen: set[tuple[str, str]] = set()

    for pair in (*STATIC_FONT_CANDIDATES, *discovered):
        if pair in seen:
            continue
        seen.add(pair)
        yield pair


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

    return _existing_font_pair(_candidate_pairs())


def resolve_font(bold: bool = False) -> str:
    """Return the font path that matches the requested weight.

    The resolver tries dynamically discovered font pairs first and falls back to
    the original Montserrat assets when no Chinese-capable font is available.
    """

    regular_path, bold_path = _resolved_pair()
    return bold_path if bold else regular_path


def load_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Build a ``pygame.font.Font`` object using the resolved font path."""

    font_path = resolve_font(bold=bold)
    return pygame.font.Font(font_path, size)

