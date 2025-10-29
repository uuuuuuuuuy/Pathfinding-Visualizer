from abc import ABC, abstractmethod
from enum import Enum
import pygame

from .constants import (
    BLACK,
    DARK_BLUE,
    WHITE,
    WIDTH,
    HEIGHT,
    load_font,
)


class Widget(ABC):
    x: int
    y: int
    width: int
    height: int
    screen: pygame.surface.Surface
    rect: pygame.rect.Rect
    text: str

    @abstractmethod
    def draw(self) -> None:
        pass

    @abstractmethod
    def set_surface(self, surf: pygame.surface.Surface) -> None:
        pass


class Button(Widget):
    """Model a button (Can be used for creating labels)"""

    def __init__(
            self,
            text: str,
            x: float | str,
            y: float | str,
            padding: int = 5,
            font_size: int = 18,
            bold: bool = False,
            outline: bool = False,
            foreground_color: pygame.Color = pygame.Color(0, 0, 0),
            background_color: pygame.Color = pygame.Color(255, 255, 255),
            hover_background_color: pygame.Color | None = None,
            active_background_color: pygame.Color | None = None,
            surface: pygame.surface.Surface | None = None,
    ) -> None:
        if surface:
            self.screen = surface
        self.text = text
        self.padding = padding
        self.outline = outline
        self.foreground_color = foreground_color
        self.background_color = background_color
        self._base_background_color = background_color
        self.font_size = font_size
        self.bold = bold

        # Render text
        font = load_font(font_size, bold=bold)

        self.text_surf = font.render(
            self.text, True, foreground_color
        )

        # Get Rect object out of the text surface
        self.text_rect = self.text_surf.get_rect()

        # Translate params: x and y if they are strings
        self.width = self.text_rect.width + padding * 2
        self.height = self.text_rect.height + padding * 2

        if x == "center":
            x = (WIDTH - self.width) / 2

        if y == "center":
            y = (HEIGHT - self.height) / 2

        # Create the actual button
        self.rect = pygame.Rect(
            float(x),
            float(y),
            self.text_rect.width + padding * 2,
            self.text_rect.height + padding * 2
        )

        self.text_rect.topleft = self.rect.x + padding, self.rect.y + padding

        self._hover_background_color = hover_background_color or self._tint_color(
            self._base_background_color, 20
        )
        self._active_background_color = (
            active_background_color
            or self._tint_color(self._base_background_color, 35)
        )
        self._is_active = False
        self._pressed_last_frame = False

    def set_surface(self, surf: pygame.surface.Surface) -> None:
        self.screen = surf

    def draw(self):
        """Draw the button (or label)

        Args:
            surf (pygame.surface.Surface): Window surface

        Returns:
            bool: Whether this button was clicked
        """

        # Whether button is clicked or not
        action = False

        # Get mouse position
        pos = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(pos)
        pressed = hovered and pygame.mouse.get_pressed()[0]

        if pressed and not self._pressed_last_frame:
            action = True

        self._pressed_last_frame = pressed

        if self._is_active:
            background = self._active_background_color
        elif hovered:
            background = self._hover_background_color
        else:
            background = self._base_background_color

        # Draw button
        pygame.draw.rect(self.screen, background, self.rect)

        if self.outline:
            pygame.draw.rect(self.screen, BLACK,
                             self.rect, width=self.outline)

        text_x, text_y = self.rect.x + self.padding, self.rect.y + self.padding
        self.screen.blit(self.text_surf, (text_x, text_y))

        return action

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{tuple(vars(self).values())!r}"

    @staticmethod
    def _tint_color(color: pygame.Color, delta: int) -> pygame.Color:
        """Create a lighter colour variant used for hover/active states."""

        new_color = pygame.Color(color)
        new_color.r = min(new_color.r + delta, 255)
        new_color.g = min(new_color.g + delta, 255)
        new_color.b = min(new_color.b + delta, 255)
        return new_color

    def set_active(self, active: bool) -> None:
        """Highlight the button as active (e.g. when a menu is open)."""

        self._is_active = active

    def update_text(self, text: str) -> None:
        """Update the label rendered on the button while keeping its anchor."""

        if text == self.text:
            return

        self.text = text
        font = load_font(self.font_size, bold=self.bold)
        self.text_surf = font.render(self.text, True, self.foreground_color)
        self.text_rect = self.text_surf.get_rect()

        self.width = self.text_rect.width + self.padding * 2
        self.height = self.text_rect.height + self.padding * 2

        self.rect.width = self.width
        self.rect.height = self.height

        self.text_rect.topleft = self.rect.x + self.padding, self.rect.y + self.padding


class Label(Button):
    def draw(self) -> None:
        """Draw label

        Args:
            surf (pygame.surface.Surface): Destination surface
        """
        # Draw label rectangle
        pygame.draw.rect(self.screen, self.background_color, self.rect)

        # Draw outline
        if self.outline:
            pygame.draw.rect(self.screen, BLACK,
                             self.rect, width=self.outline)

        # Render text
        text_x, text_y = self.rect.x + self.padding, self.rect.y + self.padding
        self.screen.blit(self.text_surf, (text_x, text_y))


class Menu(Widget):
    def __init__(
        self,
        surface: pygame.surface.Surface,
        button: Button,
        children: list[Widget]
    ) -> None:
        self.screen = surface
        self.button = button
        self.children = children
        self.clicked = False
        self.selected: Widget | None = None
        self.current_selection: Widget | None = None
        self.just_closed = False
        self._mouse_was_down = False
        self._layout_dirty = True
        self.popup_rect = pygame.Rect(0, 0, 0, 0)

        self._layout_children()


    def set_surface(self, surf: pygame.surface.Surface) -> None:
        self.screen = surf
        self.button.set_surface(surf)
        for child in self.children:
            child.set_surface(surf)

    def draw(self) -> bool:
        """Draw the menu

        Args:
            surf (pygame.surface.Surface): Window surface

        Returns:
            bool: Whether any button in this menu is clicked
        """

        if self._layout_dirty:
            self._layout_children()

        clicked = self.button.draw()
        self.selected = None
        self.just_closed = False

        if clicked:
            self.clicked = not self.clicked
            self.button.set_active(self.clicked)
            if not self.clicked:
                self.just_closed = True
                self._mouse_was_down = pygame.mouse.get_pressed()[0]
                return False

        if not self.clicked:
            self._mouse_was_down = pygame.mouse.get_pressed()[0]
            return False

        # Whether button is clicked or not
        action = False

        pos = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed()[0]

        if mouse_down and not self._mouse_was_down:
            inside_button = self.button.rect.collidepoint(pos)
            inside_popup = self.popup_rect.collidepoint(pos)
            if not inside_button and not inside_popup:
                self.clicked = False
                self.button.set_active(False)
                self.just_closed = True
                self._mouse_was_down = mouse_down
                return False

        pygame.draw.rect(
            self.screen,
            DARK_BLUE,
            self.popup_rect,
            border_radius=10
        )

        # Handle selection
        for child in self.children:
            if isinstance(child, Button):
                child.set_active(child is self.current_selection)
            if child.draw():
                self.selected = child
                self.current_selection = child
                self.clicked = False
                self.button.set_active(False)
                self.just_closed = True
                action = True
                break

        self._mouse_was_down = mouse_down

        return action

    def mark_dirty(self) -> None:
        """Schedule a layout refresh before the next draw call."""

        self._layout_dirty = True

    def set_current_selection(self, label: str | None) -> None:
        """Highlight the menu option matching ``label`` when reopened."""

        self.current_selection = None
        if label is None:
            return

        for child in self.children:
            if getattr(child, "text", None) == label:
                self.current_selection = child
                break

    def _layout_children(self) -> None:
        """Recalculate dropdown geometry based on the button and options."""

        if not self.children:
            self.popup_rect = pygame.Rect(
                self.button.rect.x,
                self.button.rect.bottom,
                self.button.rect.width,
                0,
            )
            self._layout_dirty = False
            return

        inner_margin = 8
        vertical_margin = 6

        max_child_width = max(child.rect.width for child in self.children)
        popup_width = max(self.button.rect.width, max_child_width + inner_margin * 2)
        popup_x = self.button.rect.x
        popup_y = self.button.rect.bottom + vertical_margin

        current_top = popup_y + inner_margin
        for child in self.children:
            child.rect.x = popup_x + inner_margin
            child.rect.width = popup_width - inner_margin * 2
            if hasattr(child, "width"):
                child.width = child.rect.width
            child.rect.top = current_top
            if hasattr(child, "text_rect"):
                child.text_rect.topleft = (
                    child.rect.x + child.padding,
                    child.rect.y + child.padding,
                )
            current_top = child.rect.bottom

        popup_height = current_top - popup_y + inner_margin
        self.popup_rect = pygame.Rect(
            popup_x,
            popup_y,
            popup_width,
            popup_height,
        )

        self._layout_dirty = False


class Orientation(Enum):
    HORIZONTAL = "X"
    VERTICAL = "Y"


class Alignment(Enum):
    CENTER = "C"
    LEFT = "L"
    RIGHT = "R"
    TOP = "T"
    BOTTOM = "B"
    NONE = "N"


class TableCell:
    def __init__(
        self,
        child: Widget,
        color: tuple[int, int, int] = WHITE,
        align: Alignment = Alignment.NONE
    ) -> None:
        self.child = child
        self.color = color
        self.alignment = align
        self.rect = pygame.Rect(child.rect)

    def draw(self, surf: pygame.surface.Surface) -> None:
        pygame.draw.rect(surf, self.color, self.rect)
        self.child.draw()


class Table(Widget):
    def __init__(
        self,
        x: int,
        y: int,
        rows: int,
        columns: int,
        children: list[list[TableCell]],
        color: tuple[int, int, int] = WHITE,
        padding: int = 0,
        surface: pygame.surface.Surface | None = None,
    ) -> None:
        self.x, self.y = 0, 0
        self.padding = padding

        if surface:
            self.screen = surface
            self.x = x
            self.y = y

        self.rows = rows
        self.columns = columns
        self.children = children

        max_col_widths = [max(child.rect.width for child in col)
                          for col in zip(*self.children)]

        idx = 0
        for col in zip(*self.children):
            for child in col:
                child.rect.width = max_col_widths[idx]

            idx += 1

        self.width = self.padding * 2
        self.height = self.padding * 2
        self.width += sum(max_col_widths)

        for row in self.children:
            self.height += max([child.rect.height for child in row])

        y = self.padding
        for row in range(self.rows):
            x = self.padding
            for col in range(self.columns):
                child = children[row][col]
                child.rect.x = x
                child.rect.y = y

                match child.alignment:
                    case Alignment.CENTER:
                        child.child.rect.center = child.rect.center
                    case Alignment.RIGHT:
                        child.child.rect.center = child.rect.center
                        child.child.rect.right = child.rect.right
                    case _:
                        child.child.rect.center = child.rect.center
                        child.child.rect.left = child.rect.left

                x += children[row][col].rect.width

            y += max(children[row][i].rect.height for i in range(self.columns))

        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill(color)
        self.rect = pygame.Rect(x, y, self.width, self.height)

        for row in self.children:
            for child in row:
                child.child.set_surface(self.surface)

    def set_surface(self, surf: pygame.surface.Surface) -> None:
        self.screen = surf

    def draw(self):
        for row in self.children:
            for child in row:
                child.draw(self.surface)
        self.screen.blit(self.surface, self.rect)


class Popup(Widget):
    def __init__(
        self,
        surface: pygame.surface.Surface,
        x: int,
        y: int,
        children: list[Widget],
        padding: int,
        color: tuple[int, int, int] = WHITE,
        width: int | None = None,
        height: int | None = None,
        orientation: Orientation = Orientation.HORIZONTAL,
        x_align: Alignment = Alignment.NONE,
        y_align: Alignment = Alignment.NONE,
    ) -> None:
        self.screen = surface
        self.children = children
        self.x = x
        self.y = y
        self.width = width if width else 0
        self.height = height if height else 0

        if orientation == Orientation.HORIZONTAL:
            content_width = sum(child.rect.width for child in children)
            content_height = max(child.rect.height for child in children)
        else:
            content_width = max(child.rect.width for child in children)
            content_height = sum(child.rect.height for child in children)

        if self.width == 0:
            self.width = content_width

        if self.height == 0:
            self.height = content_height

        if padding:
            self.width += padding * 2
            self.height += padding * 2

        self.padding = padding
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill(color)
        self.rect = pygame.Rect(x - padding, y - padding,
                                self.width, self.height)

        for child in children:
            child.set_surface(self.surface)

        if orientation == Orientation.HORIZONTAL:
            match x_align:
                case Alignment.CENTER:
                    children[0].rect.left = (
                        self.width - content_width) // 2
                case Alignment.RIGHT:
                    children[0].rect.left = (
                        self.width - self.padding - content_width)
                case _:
                    children[0].rect.left = self.padding

            match y_align:
                case Alignment.CENTER:
                    children[0].rect.centery = (self.height) // 2
                case Alignment.BOTTOM:
                    children[0].rect.top = (
                        self.height - self.padding - content_height
                    )
                case _:
                    children[0].rect.top = self.padding

            for i in range(1, len(children)):
                child = children[i]
                prev = children[i - 1]
                child.rect.x = prev.rect.right
                child.rect.y = self.padding

                if y_align == Alignment.CENTER:
                    child.rect.centery = prev.rect.centery
                elif y_align != Alignment.NONE:
                    child.rect.top = prev.rect.top
        else:
            match x_align:
                case Alignment.CENTER:
                    children[0].rect.centerx = self.width // 2
                case Alignment.RIGHT:
                    children[0].rect.left = (
                        self.width - self.padding - content_width)
                case _:
                    children[0].rect.left = self.padding

            match y_align:
                case Alignment.CENTER:
                    children[0].rect.top = (
                        self.height - content_height) // 2
                case Alignment.BOTTOM:
                    children[0].rect.top = (
                        self.height - self.padding - content_height
                    )
                case _:
                    children[0].rect.top = self.padding

            for i in range(1, len(children)):
                child = children[i]
                prev = children[i - 1]
                child.rect.y = prev.rect.bottom
                child.rect.x = self.padding

                if x_align == Alignment.CENTER:
                    child.rect.centerx = prev.rect.centerx
                elif x_align != Alignment.NONE:
                    child.rect.left = prev.rect.left

        self.close_btn = Button(
            surface=self.surface,
            text="   X   ",
            x=0,
            y=0,
            background_color=pygame.Color(*DARK_BLUE),
            foreground_color=pygame.Color(*WHITE),
            font_size=20, outline=False
        )
        self.close_btn.rect.right = self.rect.right
        self.close_btn.rect.top = self.rect.top

    def set_surface(self, surf: pygame.surface.Surface) -> None:
        self.screen = surf
        self.close_btn.set_surface(surf)

    def update_center(self, center: tuple[int, int]):
        self.rect.center = center
        self.close_btn.rect.right = self.rect.right
        self.close_btn.rect.top = self.rect.top

    def draw(self) -> bool:
        for child in self.children:
            child.draw()

        self.screen.blit(self.surface, self.rect)
        return self.close_btn.draw()
