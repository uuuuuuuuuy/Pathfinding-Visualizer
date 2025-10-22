import re
import sys
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Tuple

import pygame

try:
    from .fonts import load_font as _load_font_impl
except ImportError:
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
        normalized = _STYLE_SUFFIX.sub("", stem)
        return normalized.lower()

    def _style_tag(stem: str) -> str:
        lower = stem.lower()
        if re.search(r"(bold|black|heavy|extrabold|demibold|semibold|w[7-9][0-9])", lower):
            return "bold"
        return "regular"

    def _discover_font_pairs(font_dir: Path) -> list[tuple[str, str]]:
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

        candidate_pairs: list[tuple[str, str]] = [
            (str(regular), str(bold)) for regular, bold in candidates
        ]

        candidate_pairs.append(
            ("assets/fonts/Montserrat-Regular.ttf", "assets/fonts/Montserrat-Bold.ttf")
        )

        return candidate_pairs

    def _candidate_pairs() -> Iterable[tuple[str, str]]:
        static_candidates: tuple[tuple[str, str], ...] = (
            ("assets/fonts/NotoSansSC-Regular.otf", "assets/fonts/NotoSansSC-Bold.otf"),
            ("assets/fonts/NotoSansSC-Regular.ttf", "assets/fonts/NotoSansSC-Bold.ttf"),
            ("assets/fonts/SourceHanSansSC-Regular.otf", "assets/fonts/SourceHanSansSC-Bold.otf"),
            ("assets/fonts/SourceHanSans-Regular.otf", "assets/fonts/SourceHanSans-Bold.otf"),
            ("assets/fonts/MiSans-Regular.ttf", "assets/fonts/MiSans-Bold.ttf"),
        )

        discovered = _discover_font_pairs(Path("assets/fonts"))
        seen: set[tuple[str, str]] = set()

        for pair in (*static_candidates, *discovered):
            if pair in seen:
                continue
            seen.add(pair)
            yield pair

    def _existing_font_pair(
        candidates: Iterable[Tuple[str, str]]
    ) -> tuple[str, str]:
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
        return _existing_font_pair(_candidate_pairs())

    def load_font(size: int, bold: bool = False) -> pygame.font.Font:
        regular_path, bold_path = _resolved_pair()
        font_path = bold_path if bold else regular_path
        return pygame.font.Font(font_path, size)

else:

    def load_font(size: int, bold: bool = False) -> pygame.font.Font:
        return _load_font_impl(size, bold)

pygame.font.init()
pygame.display.init()

# Colors
BLACK = (0, 0, 0)
DARK = (11, 53, 71)
GREEN = (26, 188, 157)
GREEN_2 = (104, 224, 185)
BLUE = (100, 206, 228)
WHITE = (255, 255, 255)
YELLOW = (255, 254, 106)
GRAY = (166, 222, 255)
DARK_BLUE = (52, 73, 94)
BLUE_2 = (81, 145, 228)
DARK_BLUE_2 = (44, 67, 208)
PURPLE = (17, 104, 217)
ORANGE = (243, 156, 18)
RED = (231, 76, 60)

# Window Dimensions
WINDOW_INFO = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = WINDOW_INFO.current_w, WINDOW_INFO.current_h
WIDTH = 1280 if SCREEN_WIDTH >= 1280 else SCREEN_WIDTH - 150
HEIGHT = 900 if SCREEN_HEIGHT >= 900 else SCREEN_HEIGHT - 150
HEADER_HEIGHT = 200

# Maze
CELL_SIZE = 26
if len(sys.argv) > 1:
    arg = sys.argv[1]

    try:
        assert arg.startswith("--cell-size:") == True

        size = arg.split(":")[1]
        size = int(size)

        if size < 10:
            size = 10
        elif size > 90:
            size = 90

        CELL_SIZE = size
    except:
        print("\nInvalid command line arguments")
        print("USAGE: python3 run.pyw [ --cell-size:<int> ]")
        exit(1)

REMAINDER_W = WIDTH % CELL_SIZE
if REMAINDER_W == 0:
    REMAINDER_W = CELL_SIZE

REMAINDER_H = (HEIGHT - HEADER_HEIGHT) % CELL_SIZE
if REMAINDER_H == 0:
    REMAINDER_H = CELL_SIZE

MAZE_WIDTH = WIDTH - REMAINDER_W
MAZE_HEIGHT = HEIGHT - HEADER_HEIGHT - REMAINDER_H

# Framerate
FPS = 60
CLOCK = pygame.time.Clock()

# Images and fonts
WEIGHT = pygame.image.load("assets/images/weight.png")
START = pygame.image.load("assets/images/triangle.png")
GOAL = pygame.image.load("assets/images/circle.png")
FONT_14 = load_font(14)
FONT_18 = load_font(18)

# Animations
MIN_SIZE = 0.3 * CELL_SIZE
MAX_SIZE = 1.2 * CELL_SIZE
