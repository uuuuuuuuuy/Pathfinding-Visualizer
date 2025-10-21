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
    label: str
    current_value: str | None = None

    def set_selection(self, value: str | None) -> None:
        """Update the menu caption to reflect the selected value."""

        if value == self.current_value:
            return

        self.current_value = value
        if value:
            caption = f"{self.label}：{value} ▼"
        else:
            caption = f"{self.label} ▼"

        self.button.update_text(caption)
        self.menu.set_current_selection(value)
        self.menu.mark_dirty()


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

    y_center = top_area.centery
    x_cursor = title_label.rect.right + 32

    algorithm_bundle = _create_menu_bundle(
        surface=surface,
        label="算法",
        x=x_cursor,
        y=y_center,
        options=[definition.label for definition in ALGORITHM_DEFINITIONS],
    )
    algorithm_bundle.button.rect.left = x_cursor
    algorithm_bundle.button.rect.centery = y_center
    algorithm_bundle.menu.mark_dirty()

    x_cursor = algorithm_bundle.button.rect.right + 18

    speed_bundle = _create_menu_bundle(
        surface=surface,
        label="速度",
        x=x_cursor,
        y=y_center,
        options=[speed.value for speed in SPEED_OPTIONS],
    )
    speed_bundle.button.rect.left = x_cursor
    speed_bundle.button.rect.centery = y_center
    speed_bundle.menu.mark_dirty()

    x_cursor = speed_bundle.button.rect.right + 24

    visualize_button = Button(
        "开始可视化", 0, 0,
        background_color=pygame.Color(*GREEN),
        foreground_color=pygame.Color(*WHITE),
        padding=BUTTON_PADDING, font_size=BUTTON_FONT_SIZE, outline=BUTTON_OUTLINE,
        surface=surface,
    )
    visualize_button.rect.centery = y_center
    visualize_button.rect.left = x_cursor

    x_cursor = visualize_button.rect.right + 28

    comparison_button = Button(
        "比较模式", 0, 0,
        background_color=pygame.Color(*DARK_BLUE),
        foreground_color=pygame.Color(*WHITE),
        font_size=BUTTON_FONT_SIZE, outline=BUTTON_OUTLINE,
        surface=surface,
    )
    comparison_button.rect.centery = y_center
    comparison_button.rect.left = x_cursor

    comparison_bundle = _create_menu_bundle(
        surface=surface,
        label="比较模式",
        button=comparison_button,
        options=list(COMPARISON_OPTIONS),
    )
    comparison_bundle.menu.mark_dirty()

    x_cursor = comparison_bundle.button.rect.right + 18

    generation_button = Button(
        "迷宫生成", 0, 0,
        background_color=pygame.Color(*DARK_BLUE),
        foreground_color=pygame.Color(*WHITE),
        font_size=BUTTON_FONT_SIZE, outline=BUTTON_OUTLINE,
        surface=surface,
    )
    generation_button.rect.centery = y_center
    generation_button.rect.left = x_cursor

    generation_bundle = _create_menu_bundle(
        surface=surface,
        label="迷宫生成",
        button=generation_button,
        options=list(GENERATION_OPTIONS),
    )
    generation_bundle.menu.mark_dirty()

    x_cursor = generation_bundle.button.rect.right + 18

    clear_button = Button(
        "清除墙体", 0, 0,
        background_color=pygame.Color(*DARK_BLUE),
        foreground_color=pygame.Color(*WHITE),
        padding=BUTTON_PADDING, font_size=BUTTON_FONT_SIZE, outline=BUTTON_OUTLINE,
        surface=surface,
    )
    clear_button.rect.centery = y_center
    clear_button.rect.right = WIDTH - 24

    # Adjust spacing if the clear button overlaps the toolbar actions.
    overlap = generation_bundle.button.rect.right + 18 - clear_button.rect.left
    if overlap > 0:
        shift = overlap + 12
        clear_button.rect.left += shift

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
    label: str | None = None,
    x: float = 0,
    y: float = 0,
    button: Button | None = None,
    options: Iterable[str] = (),
) -> MenuBundle:
    """Create a menu bundle with the provided button label and options."""

    base_label = label or (button.text.strip() if button else "")
    caption = f"{base_label} ▼"

    menu_button = button or Button(
        surface=surface,
        text=caption,
        x=x,
        y=y,
        background_color=pygame.Color(*DARK_BLUE),
        foreground_color=pygame.Color(*WHITE),
        font_size=BUTTON_FONT_SIZE,
        outline=BUTTON_OUTLINE,
    )

    if button is not None:
        menu_button.update_text(caption)
        menu_button.rect.x = float(x)
        menu_button.rect.y = float(y)

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

    bundle = MenuBundle(
        button=menu_button,
        menu=Menu(surface=surface, button=menu_button, children=option_buttons),
        label=base_label,
    )
    bundle.set_selection(None)
    return bundle
