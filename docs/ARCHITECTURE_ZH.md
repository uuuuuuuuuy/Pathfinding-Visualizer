# 项目结构与函数说明

本文档对寻路算法可视化器的源代码进行系统梳理，便于快速了解架构、查阅函数职责，或在撰写论文与技术文档时引用。

## 目录概览
```
Pathfinding-Visualizer/
├── assets/                  # 字体与图片资源
├── screenshots/             # 示例截图
├── src/
│   ├── animations.py        # 动画节点与动画调度器
│   ├── constants.py         # 颜色、窗口尺寸等全局常量
│   ├── generate.py          # 迷宫生成算法集合
│   ├── main.py              # 程序入口与事件循环
│   ├── maze.py              # 迷宫状态、绘制与可视化逻辑
│   ├── menu_config.py       # 菜单配置与速度枚举
│   ├── state.py             # 全局运行状态单例
│   ├── ui/                  # 顶部控制栏构建
│   ├── widgets.py           # UI 基础控件
│   └── pathfinder/          # 寻路算法核心实现
└── run.pyw                  # 启动脚本（导入 src.main.main）
```

以下章节按照模块划分，逐一列出类与函数并说明其职责、核心逻辑及与其他组件的协作方式。

## 入口与状态管理

### `src/main.py`
- `main()`: 初始化标签与状态、进入 Pygame 事件循环，处理鼠标交互、菜单点击、拖拽节点等行为，并触发绘制与动画刷新。
- `instant_algorithm(maze, algorithm)`: 在不播放动画的情况下求解迷宫并立即将探索节点与最短路径渲染到网格上。
- `get_pressed()`: 监测数字键 2–9 是否被按下，用于决定绘制权重节点时的权值。
- `draw()`: 负责刷新窗口内容，包括背景、图例、菜单、迷宫格子以及按钮状态；同时根据选择的算法或速度更新标签。
- `run_single(idx)`: 对当前迷宫运行指定索引的单一算法，记录结果并在动画结束后展示统计信息。
- `run_all(algo_idx, maze_idx=-1)`: 顺序执行所有算法，支持跨多张迷宫图累计结果，并在全部完成后弹出对比表。
- `show_results(results)`: 构造表格弹窗，将算法名称、探索步数、路径长度、成本与耗时以排名形式展示。

### `src/state.py`
- `State.__new__(cls)`: 采用单例模式缓存唯一实例，集中保存界面标签、遮罩状态、结果缓存、当前算法等跨帧共享信息。

## 菜单与常量配置

### `src/menu_config.py`
- `AlgorithmDefinition`: 数据类，描述每个算法在界面中的标签与对应的 `Search` 枚举值。
- `SpeedSetting`: 枚举类，表示“快速/中速/慢速”三档动画速度。
- `ALGORITHM_DEFINITIONS`: 算法配置序列，供下拉菜单与运行逻辑共用。
- `ALGORITHMS_BY_LABEL`: 由算法标签映射到 `AlgorithmDefinition` 的字典，便于在 UI 选择后反查。
- `SPEED_OPTIONS`: 速度枚举的有序列表，驱动速度菜单。
- `COMPARISON_OPTIONS`: “当前迷宫 / 不同迷宫”两种对比运行模式。
- `GENERATION_OPTIONS`: 迷宫生成算法选项列表。

### `src/constants.py`
该文件无函数，集中定义颜色、窗口尺寸、迷宫大小、帧率、字体与素材路径，并在加载时根据 `--cell-size` 参数调整单元格尺寸。

## UI 布局与组件

### `src/ui/layout.py`
- `MenuBundle`: 数据类，打包顶栏按钮与其下拉菜单。
- `TopBarControls`: 数据类，存放顶栏区域矩形、标题标签、各菜单及按钮引用。
- `create_top_bar(surface)`: 构建顶栏背景与所有控件，设定排布位置后返回 `TopBarControls`。
- `_create_menu_bundle(surface, text=None, x=0, y=0, button=None, options=())`: 辅助函数，用于创建按钮及其对应的 `Menu` 下拉菜单。

### `src/widgets.py`
- `Widget.draw() / set_surface()`: 抽象方法，定义所有控件必须实现的绘制接口与表面绑定接口。
- `Button.__init__`: 根据文本、坐标、字体等参数生成按钮纹理与矩形。
- `Button.set_surface(surf)`: 更新按钮绘制使用的 Surface。
- `Button.draw()`: 绘制按钮背景、文本，并返回是否被点击。
- `Button.__repr__()`: 输出按钮核心属性的字符串表示。
- `Label.draw()`: 继承按钮逻辑，仅绘制文本不处理点击。
- `Menu.__init__`: 绑定下拉菜单的触发按钮，计算子项位置与整体弹出区域。
- `Menu.set_surface(surf)`: 同步菜单及子控件的绘制目标。
- `Menu.draw()`: 处理下拉面板显示、检测子项点击并返回交互结果。
- `Orientation` / `Alignment`: 枚举类型，分别描述弹窗布局方向与对齐方式。
- `TableCell.__init__`: 存放单元格嵌套的控件、背景色与对齐信息。
- `TableCell.draw(surf)`: 将单元格背景绘制到指定 Surface，并调用子控件绘制。
- `Table.__init__`: 构建表格网格，计算每列宽度、单元格位置，并在内部 Surface 上排列子控件。
- `Table.set_surface(surf)`: 指定表格最终绘制到的 Surface。
- `Table.draw()`: 将内部 Surface 渲染到目标 Surface。
- `Popup.__init__`: 创建弹窗容器，根据方向与对齐方式布置子控件，并生成关闭按钮。
- `Popup.set_surface(surf)`: 更新弹窗目标 Surface，同时同步关闭按钮。
- `Popup.update_center(center)`: 调整弹窗与关闭按钮的中心位置。
- `Popup.draw()`: 逐一绘制子控件，将弹窗贴到屏幕上，并返回关闭按钮是否被点击。

## 动画与迷宫逻辑

### `src/animations.py`
- `Animation`: 枚举，区分墙体、权重、路径三种动画类型。
- `AnimatingNode.__init__`: 记录动画矩形、目标值、颜色、持续时间与完成回调。
- `AnimatingNode.__repr__ / __str__`: 提供调试友好的文本描述。
- `Animator.__init__`: 绑定绘制 Surface 与迷宫引用，并初始化待播放的动画队列。
- `Animator.add_nodes_to_animate(nodes, delay=0, gap=10)`: 将一批动画节点入队，支持设置初始延迟与节点间隔。
- `Animator.animate_nodes()`: 更新动画进度、调用对应的私有动画函数，并在完成时写回迷宫状态及触发回调。
- `Animator._wall_animation(node)`: 对墙体动画应用 ease-out 曲线，绘制填充矩形。
- `Animator._weight_animation(node)`: 为权重节点绘制灰色方块与描边。
- `Animator._path_animation(node)`: 渲染路径动画，处理颜色渐变与圆角过渡。
- `Animator._ease_out_sine(time, starting_value, change_in_value, duration)`: 使用正弦缓动函数计算当前尺寸值。
- `Animator.__repr__()`: 输出动画器的主要状态字段。

### `src/maze.py`
- `MazeNode.__init__`: 扩展基础 `Node`，增加颜色属性以便绘制。
- `Maze.__init__`: 初始化迷宫网格、起止点坐标、屏幕坐标表与默认速度。
- `Maze._generate_coordinates()`: 计算每个单元格对应的屏幕像素坐标。
- `Maze.get_cell_value(pos)`: 返回指定格子的字符值。
- `Maze.get_node(pos)`: 返回迷宫节点对象。
- `Maze.set_cell(pos, value, forced=False)`: 根据值更新节点成本、颜色与特殊位置。
- `Maze.set_speed(speed)`: 保存当前动画速度枚举。
- `Maze.clear_board()`: 重置迷宫，清空墙体但保留起点与终点。
- `Maze.clear_visited()`: 清理可视化后留下的访问痕迹，将节点恢复为原始成本。
- `Maze.mouse_within_bounds(pos)`: 判断鼠标是否位于迷宫区域内。
- `Maze.get_cell_pos(pos)`: 将像素坐标转换为网格索引。
- `Maze.draw()`: 逐格绘制迷宫，优先显示动画中的节点。
- `Maze.generate_maze(algorithm, after_generation=None)`: 按指定算法生成迷宫，并在最后一个动画完成后触发回调。
- `Maze._draw_walls_around()`: 绘制围绕迷宫的边界墙体。
- `Maze.solve(search)`: 调用 `PathFinder` 求解当前迷宫。
- `Maze.visualize(solution, after_animation=None)`: 根据解路径添加探索节点与最短路径动画，并在结束时执行回调。
- `Maze._draw_rect(coords, color=BLUE, node=None)`: 在屏幕上绘制单个格子的最终颜色或动画帧。

### `src/generate.py`
- `MazeGenerator.__init__(animator)`: 保存动画器引用并获取迷宫实例。
- `MazeGenerator._is_valid_cell(pos)`: 判断网格坐标是否在迷宫范围内。
- `MazeGenerator._get_two_step_neighbors(maze, cell, value="")`: 获取距离两个单元格的邻居，可过滤为墙或空地。
- `MazeGenerator.randomised_prims_algorithm()`: 使用随机化普里姆算法生成迷宫，同时构造对应的墙体动画节点。
- `MazeGenerator.randomised_dfs()`: 应用随机化深度优先生成迷宫并记录动画节点。
- `MazeGenerator.basic_weight_maze()`: 随机布置高成本权重节点，生成相应动画。
- `MazeGenerator.basic_random_maze()`: 随机布置墙体节点。
- `MazeGenerator.recursive_division(x1, x2, y1, y2)`: 递归划分子区域并绘制墙体分隔线。
- `MazeGenerator._draw_line(x1, x2, y1, y2, horizontal=False)`: 在指定范围内绘制一条墙线并返回其位置，供递归划分算法使用。

## 寻路内核

### `src/pathfinder/main.py`
- `SEARCH`: 字典，将 `Search` 枚举映射到对应算法的 `search` 静态方法。
- `PathFinder.find_path(grid, search)`: 记录执行时间、调用算法求解并将耗时写回 `Solution`。

### `src/pathfinder/models`
- `Node.__init__(value, state, cost, parent=None, action=None)`: 定义网格节点的状态、成本与父子关系。
- `Node.__lt__(other)`: 在优先队列中比较节点优先级，若估价无穷则按坐标排序。
- `Node.__repr__()`: 生成节点的调试字符串。
- `Grid.__init__(grid, start, end)`: 接收迷宫节点矩阵并缓存起止坐标、尺寸信息。
- `Grid.get_node(pos)`: 按坐标获取节点对象。
- `Grid.get_cost(pos)`: 返回节点的成本值。
- `Grid.get_neighbours(pos)`: 计算可行的四向相邻动作与坐标映射。
- `Grid.__repr__()`: 返回网格摘要。
- `Frontier.__init__()`: 初始化基础边界结构的节点列表。
- `Frontier.add(node)`: 向边界加入一个节点。
- `Frontier.contains_state(state)`: 判断某状态是否已经在边界中。
- `Frontier.is_empty()`: 判空。
- `Frontier.__repr__()` / `__str__()`: 提供边界状态文本描述。
- `StackFrontier.remove()`: 以 LIFO 方式弹出节点，不存在时抛出异常。
- `QueueFrontier.remove()`: 以 FIFO 方式弹出节点，不存在时抛出异常。
- `PriorityQueueFrontier.__init__()`: 创建最小堆存储 `(priority, node)` 元组。
- `PriorityQueueFrontier.add(node, priority=0)`: 按优先级入堆。
- `PriorityQueueFrontier.get(state)`: 在堆内查找指定状态的节点。
- `PriorityQueueFrontier.pop()`: 弹出优先级最小的节点。
- `Solution.__init__(path, explored, time=0, path_cost=0)`: 保存路径、探索列表、耗时与成本并计算长度。
- `Solution.__repr__()`: 返回包含起止节点的解摘要。
- `NoSolution.__repr__()`: 自定义无解情况下的摘要字符串。
- `Search`: 枚举，定义 5 类搜索策略。

### `src/pathfinder/search`
所有搜索类都采用静态方法 `search(grid)` 返回 `Solution`。
- `AStarSearch.search(grid)`: 使用启发式估价与优先队列实现 A\* 搜索。
- `AStarSearch.heuristic(state, goal)`: 采用曼哈顿距离作为启发函数。
- `BreadthFirstSearch.search(grid)`: 使用队列按层扩展节点，适用于无权图最短路径。
- `DepthFirstSearch.search(grid)`: 使用栈深度优先遍历，适合展示回溯行为。
- `DijkstrasSearch.search(grid)`: 以节点累积成本为优先级，适合加权图最短路径。
- `GreedyBestFirstSearch.search(grid)`: 根据启发函数选择最接近目标的节点，牺牲最优性换取速度。
- `GreedyBestFirstSearch.heuristic(state, goal)`: 同样基于曼哈顿距离计算估价。

## 论文撰写建议
- **流程描述**：可引用 `main.py` 的事件循环与 `Maze.visualize()` 的动画流程来说明系统运行步骤。
- **算法比较**：`run_all()` 与 `show_results()` 提供了跨算法统计数据的生成方式，适合描述实验对比设计。
- **界面交互**：`widgets.py` 中的控件定义能够支撑 UI 设计章节的说明，尤其是弹窗、表格等复合控件的实现细节。

如需进一步扩展，可在对应模块补充函数注释或单元测试以满足论文附录或代码清单需求。
