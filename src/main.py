import sys
import pygame

from .state import State
from .generate import MazeGenerator
from .animations import Animation, Animator, AnimatingNode
from .maze import GOAL, START, Maze, WEIGHT

from .widgets import (
    Alignment,
    Label,
    Orientation,
    Popup,
    Table,
    TableCell
)

from .constants import (
    BLUE,
    CELL_SIZE,
    CLOCK,
    DARK,
    DARK_BLUE,
    FONT_14,
    FONT_18,
    GRAY,
    GREEN,
    GREEN_2,
    BLUE_2,
    MIN_SIZE,
    WHITE,
    WIDTH,
    HEIGHT,
    FPS,
    YELLOW
)

from .menu_config import (
    ALGORITHM_DEFINITIONS,
    ALGORITHMS_BY_LABEL,
    AlgorithmDefinition,
    SpeedSetting,
)
from .ui.layout import create_selection_summary, create_top_bar

# Initialize PyGame
pygame.init()

# Set up window
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HWACCEL)
pygame.display.set_caption("寻路算法可视化器")

# Top bar
top_controls = create_top_bar(WINDOW)
top = top_controls.area
title = top_controls.title

algorithm_bundle = top_controls.algorithm
speed_bundle = top_controls.speed
comparison_bundle = top_controls.comparison
generation_bundle = top_controls.generation

algorithm_menu = algorithm_bundle.menu
speed_menu = speed_bundle.menu
visualize_button = top_controls.visualize_button
comparison_menu = comparison_bundle.menu
generation_menu = generation_bundle.menu
pause_button = top_controls.pause_button
reset_button = top_controls.reset_button

selection_summary = create_selection_summary(WINDOW)
summary_area = selection_summary.area
status_area = pygame.Rect(32, summary_area.bottom + 6, WIDTH - 64, 30)

# Instantiate Maze and Animator
state = State()
maze = Maze(surface=WINDOW)
animator = Animator(surface=WINDOW, maze=maze)
maze_generator = MazeGenerator(animator=animator)
maze.animator = animator
maze.generator = maze_generator


def set_status(message: str) -> None:
    """Update the status banner displayed beneath the toolbar summary."""

    state.label = Label(
        message, "center", 0,
        background_color=pygame.Color(*WHITE),
        foreground_color=pygame.Color(*DARK),
        padding=5, font_size=15, outline=False,
        surface=WINDOW,
    )
    state.label.rect.center = status_area.center
    state.label.text_rect.topleft = (
        state.label.rect.x + state.label.padding,
        state.label.rect.y + state.label.padding,
    )


def main() -> None:
    """Start here"""
    set_status("状态：请选择算法并点击“开始可视化”")

    speed_bundle.set_selection(SpeedSetting.FAST.value)
    maze.set_speed(SpeedSetting.FAST)
    selection_summary.set_value("speed", SpeedSetting.FAST.value)
    selection_summary.set_value("comparison", "关闭")
    selection_summary.set_value("generation", "未开始")

    # Game loop
    mouse_is_down = False
    state.done_visualising = False
    state.need_update = True

    draw_weighted_nodes = False

    dragging = False
    cell_under_mouse = (-1, -1)
    cell_value = ""

    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if state.overlay:
                    break

                state.need_update = True
                pos = pygame.mouse.get_pos()

                if not maze.mouse_within_bounds(pos):
                    break

                mouse_is_down = True

                row, col = maze.get_cell_pos(pos)
                if (value := maze.get_cell_value((row, col))) in ("A", "B"):
                    dragging = True
                    cell_under_mouse = (row, col)
                    cell_value = value

            if event.type == pygame.MOUSEBUTTONUP:
                mouse_is_down = False
                animator.animating = False
                draw_weighted_nodes = False

                if dragging:
                    dragging = False

                    pos = pygame.mouse.get_pos()
                    if not maze.mouse_within_bounds(pos):
                        break

                    row, col = maze.get_cell_pos(pos)
                    if maze.get_cell_value((row, col)) in ("A", "B") or state.done_visualising:
                        break

                    maze.set_cell((row, col), cell_value)
                    maze.set_cell(cell_under_mouse, "1")

                cell_under_mouse = (-1, -1)

        if state.need_update:
            draw()

        # Get pressed keys for weighted nodes
        draw_weighted_nodes, key = get_pressed()

        # Draw walls | weighted nodes
        # This should not run when animating solution
        if mouse_is_down and not dragging:
            pos = pygame.mouse.get_pos()

            if maze.mouse_within_bounds(pos):
                row, col = maze.get_cell_pos(pos)

                if cell_under_mouse != (row, col):
                    if maze.get_cell_value((row, col)) in ("1", "V", "*"):
                        rect = pygame.Rect(0, 0, MIN_SIZE, MIN_SIZE)
                        x, y = maze.coords[row][col]

                        if draw_weighted_nodes and key:

                            animator.add_nodes_to_animate([
                                AnimatingNode(
                                    rect=rect,
                                    center=(x + CELL_SIZE // 2,
                                            y + CELL_SIZE // 2),
                                    ticks=pygame.time.get_ticks(),
                                    value=str(key % 50 + 2),
                                    animation=Animation.WEIGHT_ANIMATION,
                                    color=WHITE,
                                    duration=50,
                                )
                            ])

                        else:
                            animator.add_nodes_to_animate([
                                AnimatingNode(
                                    rect=rect,
                                    center=(x + CELL_SIZE // 2,
                                            y + CELL_SIZE // 2),
                                    ticks=pygame.time.get_ticks(),
                                    value="#",
                                    color=DARK
                                )
                            ])

                    elif maze.get_cell_value((row, col)) not in ("A", "B"):
                        maze.set_cell((row, col), "1")

                    cell_under_mouse = (row, col)

        # Animate nodes
        if animator.nodes_to_animate and state.need_update:
            animator.animating = True
            animator.animate_nodes()
        else:
            animator.animating = False

        # Handle moving start and target nodes
        if dragging and not state.done_visualising and not animator.animating:
            x, y = pygame.mouse.get_pos()
            if cell_value == "A":
                WINDOW.blit(START, (x - 10, y - 10))
            else:
                WINDOW.blit(GOAL, (x - 10, y - 10))

        # Instantly find path if dragging post visualisation
        if dragging and state.done_visualising and not animator.animating:
            x, y = pygame.mouse.get_pos()

            if maze.mouse_within_bounds((x, y)):
                row, col = maze.get_cell_pos((x, y))
                x, y = maze.coords[row][col]

                if cell_under_mouse != (row, col):
                    maze.set_cell((row, col), cell_value)
                    maze.set_cell(cell_under_mouse, "1")

                    if state.current_algorithm:
                        instant_algorithm(maze, state.current_algorithm)
                    cell_under_mouse = (row, col)

        # Update
        pygame.display.update()
        CLOCK.tick(FPS)


def instant_algorithm(maze: Maze, algorithm: AlgorithmDefinition) -> None:
    """Find path without animation

    Args:
        maze (Maze): Maze
        algorithm (AlgorithmDefinition): Algorithm to solve with
    """
    maze.clear_visited()

    solution = maze.solve(algorithm.search)

    path = solution.path
    explored = solution.explored

    # Mark explored nodes as blue
    for i, j in explored:
        if (i, j) in (maze.start, maze.goal):
            continue

        maze.set_cell((i, j), "V")

    # Mark optimal path nodes as yellow
    for i, j in path:
        if (i, j) in (maze.start, maze.goal):
            continue

        maze.set_cell((i, j), "*")


def get_pressed() -> tuple[bool, int | None]:
    """Return pressed key if number

    Returns:
        tuple[bool, int | None]: Whether a num key was pressed,
                                 the key if found
    """
    keys = [pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
            pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]

    pressed = pygame.key.get_pressed()
    for key in keys:
        if pressed[key]:
            return True, key

    return False, None


def draw() -> None:
    """Draw things (except Visualise button)
    """
    top_controls.layout()

    # Fill white, draw top background and title text
    WINDOW.fill(WHITE)
    pygame.draw.rect(WINDOW, DARK_BLUE, top)
    title.draw()

    pygame.draw.rect(WINDOW, BLUE_2, summary_area)
    selection_summary.layout()
    for field in selection_summary.values():
        field.label.draw()

    pygame.draw.rect(WINDOW, WHITE, status_area)
    state.label.rect.center = status_area.center
    state.label.text_rect.topleft = (
        state.label.rect.x + state.label.padding,
        state.label.rect.y + state.label.padding,
    )
    state.label.draw()

    legend_sections = [
        (
            "节点类型",
            [
                ("迷宫节点", WHITE, None),
                ("障碍物节点", DARK, None),
                ("权重节点", WHITE, WEIGHT),
            ],
        ),
        (
            "搜索状态",
            [
                ("起点节点", WHITE, START),
                ("目标节点", WHITE, GOAL),
                ("访问过的节点", BLUE, None),
                ("最短路径节点", YELLOW, None),
            ],
        ),
    ]

    legend_left = 32
    legend_right = WIDTH - 32
    legend_top = status_area.bottom + 10
    icon_size = 20
    row_gap = 10
    item_gap = 18
    heading_gap = 10
    group_gap = 24

    legend_x = legend_left
    legend_y = legend_top
    max_row_height = icon_size

    for heading, items in legend_sections:
        heading_text = f"{heading}："
        heading_surf = FONT_14.render(heading_text, True, DARK_BLUE)
        heading_rect = heading_surf.get_rect()
        heading_rect.centery = legend_y + icon_size // 2
        heading_rect.left = legend_x

        if heading_rect.right > legend_right:
            legend_x = legend_left
            legend_y += max_row_height + row_gap
            max_row_height = icon_size
            heading_rect.left = legend_x
            heading_rect.centery = legend_y + icon_size // 2

        WINDOW.blit(heading_surf, heading_rect)
        legend_x = heading_rect.right + heading_gap

        for label, color, icon in items:
            if legend_x + icon_size > legend_right:
                legend_x = legend_left
                legend_y += max_row_height + row_gap
                max_row_height = icon_size

            icon_rect = pygame.Rect(legend_x, legend_y, icon_size, icon_size)
            pygame.draw.rect(WINDOW, color, icon_rect)
            pygame.draw.rect(WINDOW, GRAY, icon_rect, width=1)

            if icon:
                asset_rect = icon.get_rect(center=icon_rect.center)
                WINDOW.blit(icon, asset_rect)

            text_surf = FONT_14.render(label, True, DARK)
            text_rect = text_surf.get_rect()
            text_rect.midleft = (icon_rect.right + 6, icon_rect.centery)
            WINDOW.blit(text_surf, text_rect)

            item_height = max(icon_rect.height, text_rect.height)
            max_row_height = max(max_row_height, item_height)
            legend_x = text_rect.right + item_gap

        legend_x += group_gap

    legend_y += max_row_height + row_gap

    weight_hint = FONT_14.render(
        "提示：按数字键 2-9 并拖拽鼠标可放置不同权重节点", True, DARK
    )
    hint_rect = weight_hint.get_rect()
    hint_rect.topleft = (legend_left, legend_y)
    WINDOW.blit(weight_hint, hint_rect)

    maze.draw()

    # Handle buttons
    if (algorithm_menu.draw() or algorithm_menu.clicked) \
            and not maze.animator.animating:
        state.overlay = True
        if algorithm_menu.selected:
            state.current_algorithm = ALGORITHMS_BY_LABEL[
                algorithm_menu.selected.text
            ]
            algorithm_bundle.set_selection(algorithm_menu.selected.text)
            selection_summary.set_value("algorithm", algorithm_menu.selected.text)
            set_status("状态：算法已选择，点击“开始可视化”开始演示")

            if state.done_visualising:
                instant_algorithm(maze, state.current_algorithm)

            state.overlay = False

    if algorithm_menu.just_closed and state.overlay and not (
        animator.animating or state.results_popup
    ):
        state.overlay = False

    if (speed_menu.draw() or speed_menu.clicked) \
            and not maze.animator.animating:
        state.overlay = True

        if speed_menu.selected:
            maze.set_speed(SpeedSetting(speed_menu.selected.text))
            speed_bundle.set_selection(speed_menu.selected.text)
            selection_summary.set_value("speed", speed_menu.selected.text)
            state.overlay = False

    if speed_menu.just_closed and state.overlay and not (
        animator.animating or state.results_popup
    ):
        state.overlay = False

    if visualize_button.draw() \
        and state.current_algorithm \
            and not maze.animator.animating:
        state.overlay = True

        idx = ALGORITHM_DEFINITIONS.index(state.current_algorithm)
        run_single(idx)

    pause_clicked = pause_button.draw()
    if pause_clicked:
        if animator.paused:
            animator.resume()
            pause_button.update_text("暂停动画")
            pause_button.set_active(False)
        elif animator.nodes_to_animate:
            animator.pause()
            pause_button.update_text("继续动画")
            pause_button.set_active(True)
        else:
            pause_button.update_text("暂停动画")
            pause_button.set_active(False)

    if not animator.nodes_to_animate and not animator.animating and not animator.paused:
        pause_button.update_text("暂停动画")
        pause_button.set_active(False)

    if reset_button.draw():
        reset_simulation()

    if (comparison_menu.draw() or comparison_menu.clicked) \
            and not animator.animating:
        state.overlay = True

        if comparison_menu.selected \
                and comparison_menu.selected.text == "当前迷宫":
            comparison_bundle.set_selection(comparison_menu.selected.text)
            selection_summary.set_value("comparison", comparison_menu.selected.text)
            state.results = {}
            run_all(0)
        elif comparison_menu.selected \
                and comparison_menu.selected.text == "不同迷宫":
            state.run_all_mazes = True
            state.results = {}
            comparison_bundle.set_selection(comparison_menu.selected.text)
            selection_summary.set_value("comparison", comparison_menu.selected.text)
            run_all(0)

    if comparison_menu.just_closed and state.overlay and not (
        animator.animating or state.results_popup
    ):
        state.overlay = False

    if (generation_menu.draw() or generation_menu.clicked) \
            and not animator.animating:
        state.overlay = True

        if generation_menu.selected:
            maze.clear_board()
            text = state.label.text
            selected_generation = generation_menu.selected.text
            generation_bundle.set_selection(selected_generation)
            selection_summary.set_value(
                "generation", f"{selected_generation}（进行中）"
            )

            def callback():
                state.overlay = False
                set_status(text)
                selection_summary.set_value("generation", selected_generation)

            maze.generate_maze(
                algorithm=selected_generation,
                after_generation=callback
            )

            algorithm = selected_generation

            if algorithm == "基本权重迷宫":
                new_text = "正在生成基本权重迷宫"
            elif algorithm == "基本随机迷宫":
                new_text = "正在随机生成迷宫"
            else:
                new_text = f"正在使用 {algorithm} 生成迷宫"

            set_status(new_text)

    if state.results_popup:
        state.overlay = True
        if state.results_popup.draw():
            state.results_popup = None
            state.overlay = False

    if not (
        algorithm_menu.clicked
        or speed_menu.clicked
        or comparison_menu.clicked
        or generation_menu.clicked
        or state.results_popup
        or animator.animating
        or animator.nodes_to_animate
    ) and state.overlay:
        state.overlay = False


def reset_simulation() -> None:
    """Stop ongoing animations and restore the default maze configuration."""

    animator.stop()
    maze.clear_board()
    maze.set_speed(SpeedSetting.FAST)

    state.done_visualising = False
    state.need_update = True
    state.overlay = False
    state.results = {}
    state.run_all_mazes = False
    state.results_popup = None
    state.current_algorithm = None

    set_status("状态：请选择算法并点击“开始可视化”")

    algorithm_bundle.set_selection(None)
    speed_bundle.set_selection(SpeedSetting.FAST.value)
    comparison_bundle.set_selection(None)
    generation_bundle.set_selection(None)

    selection_summary.set_value("algorithm", None)
    selection_summary.set_value("speed", SpeedSetting.FAST.value)
    selection_summary.set_value("comparison", "关闭")
    selection_summary.set_value("generation", "未开始")

    pause_button.update_text("暂停动画")
    pause_button.set_active(False)


def run_single(idx: int) -> None:
    """Run a single algorithm on one maze."""

    maze.clear_visited()
    definition = ALGORITHM_DEFINITIONS[idx]
    state.current_algorithm = definition
    solution = maze.solve(definition.search)

    def callback() -> None:
        state.done_visualising = True
        set_status(
            f"{definition.label} 共探索 {solution.explored_length} 步，耗时 {solution.time:.2f} 毫秒"
        )
        state.overlay = False

    maze.visualize(solution=solution, after_animation=callback)

    set_status(f"正在运行 {definition.label}")


def run_all(algo_idx: int, maze_idx: int = -1) -> None:
    """Run all algorithms on the current maze or across multiple mazes."""

    maze.clear_visited()
    definition = ALGORITHM_DEFINITIONS[algo_idx]
    state.current_algorithm = definition

    def callback():
        if algo_idx + 1 < len(ALGORITHM_DEFINITIONS):
            run_all(algo_idx + 1, maze_idx)
        elif state.run_all_mazes and maze_idx + 1 < len(generation_menu.children):
            maze.clear_board()

            def after_generation():
                run_all(0, maze_idx + 1)

            maze.generate_maze(
                algorithm=generation_menu.children[maze_idx + 1].text,
                after_generation=after_generation
            )

            algorithm = generation_menu.children[maze_idx + 1].text

            if algorithm == "基本权重迷宫":
                new_text = "正在生成基本权重迷宫"
            elif algorithm == "基本随机迷宫":
                new_text = "正在随机生成迷宫"
            else:
                new_text = f"正在使用 {algorithm} 生成迷宫"

            set_status(new_text)
        else:
            set_status("比较完成，查看结果表获取详细数据")

            results = list(state.results.items())

            if state.run_all_mazes:
                for result in results:
                    result[1]["path_length"] //= maze_idx + 2
                    result[1]["path_cost"] //= maze_idx + 2
                    result[1]["explored_length"] //= maze_idx + 2
                    result[1]["time"] /= maze_idx + 2

            results.sort(key=lambda item: item[1]["time"])

            show_results(results)
            state.run_all_mazes = False
            state.overlay = False

    solution = maze.solve(definition.search)

    if definition.label not in state.results:
        state.results[definition.label] = vars(solution)
    else:
        state.results[definition.label]["explored_length"] += solution.explored_length
        state.results[definition.label]["path_length"] += solution.path_length
        state.results[definition.label]["path_cost"] += solution.path_cost
        state.results[definition.label]["time"] += solution.time

    maze.visualize(solution=solution, after_animation=callback)

    set_status(f"正在运行 {definition.label}")


def show_results(results: list[tuple[str, dict[str, float]]]) -> None:
    """Display results

    Args:
        results (list[tuple[str, dict[str, float]]]): Result data
    """
    children: list[list[TableCell]] = []
    children.append([
        TableCell(
            child=Label(
                    "算法", 0, 0,
                    background_color=pygame.Color(*DARK_BLUE),
                    foreground_color=pygame.Color(*WHITE),
                    padding=6, font_size=20, outline=False,
                    surface=WINDOW,
                    ),
            color=DARK_BLUE,
        ),
        TableCell(
            child=Label(
                "探索步数", 0, 0,
                background_color=pygame.Color(*DARK_BLUE),
                foreground_color=pygame.Color(*WHITE),
                padding=6, font_size=20, outline=False,
                surface=WINDOW,
            ),
            color=DARK_BLUE,
        ),
        TableCell(
            child=Label(
                "路径长度", 0, 0,
                background_color=pygame.Color(*DARK_BLUE),
                foreground_color=pygame.Color(*WHITE),
                padding=6, font_size=20, outline=False,
                surface=WINDOW,
            ),
            color=DARK_BLUE,
        ),
        TableCell(
            child=Label(
                "路径成本", 0, 0,
                background_color=pygame.Color(*DARK_BLUE),
                foreground_color=pygame.Color(*WHITE),
                padding=6, font_size=20, outline=False,
                surface=WINDOW,
            ),
            color=DARK_BLUE,
        ),
        TableCell(
            child=Label(
                "耗时", 0, 0,
                background_color=pygame.Color(*DARK_BLUE),
                foreground_color=pygame.Color(*WHITE),
                padding=6, font_size=20, outline=False,
                surface=WINDOW,
            ),
            color=DARK_BLUE,
        ),
    ])

    colors = [GREEN_2, GREEN_2, YELLOW, YELLOW]
    colors.extend([GRAY] * (len(results) - 4))

    for i, result in enumerate(results):
        children.append([
            TableCell(
                child=Label(
                        f"{i + 1}. {result[0]}", 0, 0,
                        background_color=pygame.Color(*colors[i]),
                        foreground_color=pygame.Color(*DARK),
                        padding=6, font_size=20, outline=False,
                        surface=WINDOW,
                        ),
                color=colors[i],
                align=Alignment.LEFT
            ),
            TableCell(
                child=Label(
                    f"{result[1]['explored_length']}", 0, 0,
                    background_color=pygame.Color(*colors[i]),
                    foreground_color=pygame.Color(*DARK),
                    padding=6, font_size=20, outline=False,
                    surface=WINDOW,
                ),
                color=colors[i],
                align=Alignment.RIGHT
            ),
            TableCell(
                child=Label(
                    f"{result[1]['path_length']}", 0, 0,
                    background_color=pygame.Color(*colors[i]),
                    foreground_color=pygame.Color(*DARK),
                    padding=6, font_size=20, outline=False,
                    surface=WINDOW,
                ),
                color=colors[i],
                align=Alignment.RIGHT
            ),
            TableCell(
                child=Label(
                    f"{result[1]['path_cost']}", 0, 0,
                    background_color=pygame.Color(*colors[i]),
                    foreground_color=pygame.Color(*DARK),
                    padding=6, font_size=20, outline=False,
                    surface=WINDOW,
                ),
                color=colors[i],
                align=Alignment.RIGHT
            ),
            TableCell(
                child=Label(
                    f"{result[1]['time']:.2f} 毫秒", 0, 0,
                    background_color=pygame.Color(*colors[i]),
                    foreground_color=pygame.Color(*DARK),
                    padding=6, font_size=20, outline=False,
                    surface=WINDOW,
                ),
                color=colors[i],
                align=Alignment.RIGHT
            ),
        ])

    popup = Popup(
        WINDOW,
        0,
        0,
        padding=20,
        color=DARK,
        orientation=Orientation.VERTICAL,
        x_align=Alignment.CENTER,
        y_align=Alignment.CENTER,
        children=[
            Label(
                "比较结果", 0, 0,
                background_color=pygame.Color(*DARK),
                foreground_color=pygame.Color(*WHITE),
                padding=10, font_size=20, outline=False,
                surface=WINDOW,
            ),
            Table(
                x=0,
                y=0,
                rows=6,
                columns=5,
                padding=20,
                color=DARK,
                children=children,
            )
        ],
    )

    popup.update_center(WINDOW.get_rect().center)
    popup.set_surface(WINDOW)
    state.results_popup = popup
