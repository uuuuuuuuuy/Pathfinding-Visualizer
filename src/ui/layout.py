from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pygame

from ..constants import DARK, DARK_BLUE, GREEN, WHITE, WIDTH
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
SUMMARY_HEIGHT = 56
SUMMARY_PADDING = 10
SUMMARY_GAP = 20


@dataclass(slots=True)
class MenuBundle:
    """Encapsulates a menu button and its dropdown menu."""

    button: Button
    menu: Menu
    label: str
    current_value: str | None = None

    def set_selection(self, value: str | None) -> None:
        """Remember the current selection while keeping the caption static."""

        if value == self.current_value:
            return

        self.current_value = value
        self.button.update_text(f"{self.label} ▼")
        self.menu.set_current_selection(value)
        self.menu.mark_dirty()


@dataclass(slots=True)
class SummaryField:
    """Represents one value in the selection summary row."""

    key: str
    heading: str
    placeholder: str
    label: Label

    def set_value(self, value: str | None) -> None:
        display = value if value else self.placeholder
        self.label.update_text(f"{self.heading}：{display}")


@dataclass(slots=True)
class SelectionSummary:
    """Container that lays out the current selections beneath the toolbar."""

    area: pygame.Rect
    fields: dict[str, SummaryField]
    order: tuple[str, ...]

    def layout(self) -> None:
        x_cursor = self.area.left + 24
        baseline = self.area.centery

        for key in self.order:
            field = self.fields[key]
            label = field.label
            label.rect.left = x_cursor
            label.rect.centery = baseline
            label.text_rect.topleft = (
                label.rect.x + label.padding,
                label.rect.y + label.padding,
            )
            x_cursor = label.rect.right + SUMMARY_GAP

    def set_value(self, key: str, value: str | None) -> None:
        if key not in self.fields:
            return

        self.fields[key].set_value(value)

    def values(self) -> tuple[SummaryField, ...]:
        return tuple(self.fields[key] for key in self.order)


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
    pause_button: Button
    reset_button: Button

    def layout(self) -> None:
        """Reflow toolbar controls based on their current text widths."""

        y_center = self.area.centery
        margin_left = 24
        gap_after_title = 32
        gap_between_menus = 18
        gap_after_speed = 24
        gap_after_visualize = 20
        gap_after_pause = 18
        gap_after_reset = 28

        def place(widget: Button, gap: int) -> None:
            nonlocal x_cursor
            widget.rect.left = x_cursor
            widget.rect.centery = y_center
            if hasattr(widget, "text_rect"):
                widget.text_rect.topleft = (
                    widget.rect.x + widget.padding,
                    widget.rect.y + widget.padding,
                )
            x_cursor = widget.rect.right + gap

        x_cursor = margin_left

        place(self.title, gap_after_title)

        place(self.algorithm.button, gap_between_menus)
        self.algorithm.menu.mark_dirty()

        place(self.speed.button, gap_after_speed)
        self.speed.menu.mark_dirty()

        place(self.visualize_button, gap_after_visualize)

        place(self.pause_button, gap_after_pause)

        place(self.reset_button, gap_after_reset)

        place(self.comparison.button, gap_between_menus)
        self.comparison.menu.mark_dirty()

        place(self.generation.button, gap_between_menus)
        self.generation.menu.mark_dirty()

        if hasattr(self.reset_button, "text_rect"):
            self.reset_button.text_rect.topleft = (
                self.reset_button.rect.x + self.reset_button.padding,
                self.reset_button.rect.y + self.reset_button.padding,
            )


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
    x_cursor = algorithm_bundle.button.rect.right + 18

    speed_bundle = _create_menu_bundle(
        surface=surface,
        label="速度",
        x=x_cursor,
        y=y_center,
        options=[speed.value for speed in SPEED_OPTIONS],
    )
    x_cursor = speed_bundle.button.rect.right + 24

    visualize_button = Button(
        "开始可视化", 0, 0,
        background_color=pygame.Color(*GREEN),
        foreground_color=pygame.Color(*WHITE),
        padding=BUTTON_PADDING, font_size=BUTTON_FONT_SIZE, outline=BUTTON_OUTLINE,
        surface=surface,
    )
    x_cursor = visualize_button.rect.right + 28

    pause_button = Button(
        "暂停动画", 0, 0,
        background_color=pygame.Color(*DARK_BLUE),
        foreground_color=pygame.Color(*WHITE),
        padding=BUTTON_PADDING, font_size=BUTTON_FONT_SIZE, outline=BUTTON_OUTLINE,
        surface=surface,
    )
    x_cursor = pause_button.rect.right + 18

    reset_button = Button(
        "重新开始", 0, 0,
        background_color=pygame.Color(*DARK_BLUE),
        foreground_color=pygame.Color(*WHITE),
        padding=BUTTON_PADDING, font_size=BUTTON_FONT_SIZE, outline=BUTTON_OUTLINE,
        surface=surface,
    )
    x_cursor = reset_button.rect.right + 24

    comparison_button = Button(
        "比较模式", 0, 0,
        background_color=pygame.Color(*DARK_BLUE),
        foreground_color=pygame.Color(*WHITE),
        font_size=BUTTON_FONT_SIZE, outline=BUTTON_OUTLINE,
        surface=surface,
    )
    comparison_bundle = _create_menu_bundle(
        surface=surface,
        label="比较模式",
        button=comparison_button,
        options=list(COMPARISON_OPTIONS),
    )
    x_cursor = comparison_bundle.button.rect.right + 18

    generation_button = Button(
        "迷宫生成", 0, 0,
        background_color=pygame.Color(*DARK_BLUE),
        foreground_color=pygame.Color(*WHITE),
        font_size=BUTTON_FONT_SIZE, outline=BUTTON_OUTLINE,
        surface=surface,
    )
    generation_bundle = _create_menu_bundle(
        surface=surface,
        label="迷宫生成",
        button=generation_button,
        options=list(GENERATION_OPTIONS),
    )
    controls = TopBarControls(
        area=top_area,
        title=title_label,
        algorithm=algorithm_bundle,
        speed=speed_bundle,
        comparison=comparison_bundle,
        generation=generation_bundle,
        visualize_button=visualize_button,
        pause_button=pause_button,
        reset_button=reset_button,
    )

    controls.layout()

    return controls


def create_selection_summary(surface: pygame.surface.Surface) -> SelectionSummary:
    """Create the summary row that mirrors current dropdown selections."""

    summary_area = pygame.Rect(0, TOP_BAR_HEIGHT, WIDTH, SUMMARY_HEIGHT)

    field_specs = (
        ("algorithm", "当前算法", "未选择"),
        ("speed", "当前速度", "快速"),
        ("comparison", "比较模式", "关闭"),
        ("generation", "迷宫生成", "未开始"),
    )

    fields: dict[str, SummaryField] = {}
    for key, heading, placeholder in field_specs:
        label = Label(
            f"{heading}：{placeholder}",
            0,
            0,
            padding=SUMMARY_PADDING,
            font_size=18,
            background_color=pygame.Color(*WHITE),
            foreground_color=pygame.Color(*DARK),
            surface=surface,
        )
        fields[key] = SummaryField(
            key=key,
            heading=heading,
            placeholder=placeholder,
            label=label,
        )

    summary = SelectionSummary(
        area=summary_area,
        fields=fields,
        order=tuple(key for key, *_ in field_specs),
    )
    summary.layout()
    return summary


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
