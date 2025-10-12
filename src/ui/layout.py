from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pygame

from ..constants import DARK_BLUE, GREEN, WHITE, WIDTH
from ..widgets import Button, Label, Menu
from ..menu_config import (
    ALGORITHM_DEFINITIONS,
    COMPARISON_OPTIONS,
    GENERATION_OPTIONS,
    SPEED_OPTIONS,
)

TOP_BAR_HEIGHT = 80
BUTTON_FONT_SIZE = 20
BUTTON_PADDING = 6
BUTTON_OUTLINE = False


@dataclass(slots=True)
class MenuBundle:
    """Encapsulates a menu button and its dropdown menu."""

    button: Button
    menu: Menu


@dataclass(slots=True)
class TopBarControls:
    """Collection of controls that compose the header of the visualiser."""

    area: pygame.Rect
    title: Label
    algorithm: MenuBundle
    speed: MenuBundle
    comparison: MenuBundle
    generation: MenuBundle
    visualize_button: Button
    clear_button: Button


def create_top_bar(surface: pygame.surface.Surface) -> TopBarControls:
    """Create and position all controls displayed in the top toolbar."""

    top_area = pygame.Rect(0, 0, WIDTH, TOP_BAR_HEIGHT)

    title_label = Label(
        "寻路算法可视化器", 20, 0,
        background_color=pygame.Color(*DARK_BLUE),
        foreground_color=pygame.Color(*WHITE),
        padding=BUTTON_PADDING, font_size=BUTTON_FONT_SIZE, bold=True,
        surface=surface,
    )
    title_label.rect.centery = top_area.centery

    algorithm_bundle = _create_menu_bundle(
        surface=surface,
        text="算法",
        x=title_label.width + 70,
        y=0,
        options=(definition.label for definition in ALGORITHM_DEFINITIONS),
    )
    algorithm_bundle.button.rect.centery = top_area.centery

    speed_bundle = _create_menu_bundle(
        surface=surface,
        text="速度",
        x=algorithm_bundle.button.rect.right + 40,
        y=0,
        options=(speed.value for speed in SPEED_OPTIONS),
    )
    speed_bundle.button.rect.centery = top_area.centery
    speed_bundle.button.rect.y -= 15

    visualize_button = Button(
        "开始可视化", "center", 0,
        background_color=pygame.Color(*GREEN),
        foreground_color=pygame.Color(*WHITE),
        padding=BUTTON_PADDING, font_size=BUTTON_FONT_SIZE, outline=BUTTON_OUTLINE,
        surface=surface,
    )
    visualize_button.rect.centery = top_area.centery

    comparison_button = Button(
        "全部运行    ", 0, 0,
        background_color=pygame.Color(*DARK_BLUE),
        foreground_color=pygame.Color(*WHITE),
        font_size=BUTTON_FONT_SIZE, outline=BUTTON_OUTLINE,
        surface=surface,
    )
    comparison_button.rect.centery = top_area.centery
    comparison_button.rect.left = visualize_button.rect.right + 50

    comparison_bundle = _create_menu_bundle(
        surface=surface,
        button=comparison_button,
        options=COMPARISON_OPTIONS,
    )

    generation_button = Button(
        "生成迷宫", 0, 0,
        background_color=pygame.Color(*DARK_BLUE),
        foreground_color=pygame.Color(*WHITE),
        font_size=BUTTON_FONT_SIZE, outline=BUTTON_OUTLINE,
        surface=surface,
    )
    generation_button.rect.centery = top_area.centery
    generation_button.rect.left = comparison_button.rect.right + 50

    generation_bundle = _create_menu_bundle(
        surface=surface,
        button=generation_button,
        options=GENERATION_OPTIONS,
    )

    clear_button = Button(
        "清除墙体", 0, 0,
        background_color=pygame.Color(*DARK_BLUE),
        foreground_color=pygame.Color(*WHITE),
        padding=BUTTON_PADDING, font_size=BUTTON_FONT_SIZE, outline=BUTTON_OUTLINE,
        surface=surface,
    )
    clear_button.rect.centery = top_area.centery
    clear_button.rect.right = WIDTH - 20

    return TopBarControls(
        area=top_area,
        title=title_label,
        algorithm=algorithm_bundle,
        speed=speed_bundle,
        comparison=comparison_bundle,
        generation=generation_bundle,
        visualize_button=visualize_button,
        clear_button=clear_button,
    )


def _create_menu_bundle(
    surface: pygame.surface.Surface,
    text: str | None = None,
    x: float = 0,
    y: float = 0,
    button: Button | None = None,
    options: Iterable[str] = (),
) -> MenuBundle:
    """Create a menu bundle with the provided button label and options."""

    menu_button = button or Button(
        surface=surface,
        text=text or "",
        x=x,
        y=y,
        background_color=pygame.Color(*DARK_BLUE),
        foreground_color=pygame.Color(*WHITE),
        font_size=BUTTON_FONT_SIZE,
        outline=BUTTON_OUTLINE,
    )

    option_buttons: list[Button] = [
        Button(
            surface=surface,
            text=label,
            x=0,
            y=0,
            background_color=pygame.Color(*DARK_BLUE),
            foreground_color=pygame.Color(*WHITE),
            font_size=BUTTON_FONT_SIZE,
            outline=BUTTON_OUTLINE,
        )
        for label in options
    ]

    return MenuBundle(
        button=menu_button,
        menu=Menu(surface=surface, button=menu_button, children=option_buttons),
    )
