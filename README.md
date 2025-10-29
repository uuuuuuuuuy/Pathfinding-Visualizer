# 寻路算法可视化器

该项目基于 Python 与 Pygame 构建，是一个交互式的寻路与迷宫生成算法可视化工具。通过动画展示搜索过程、路径选择及性能指标，帮助你直观比较不同算法在不同地图上的表现，非常适合教学演示、论文撰写或课程项目展示。

## 功能亮点
- **多算法支持**：内置 A\*、迪杰斯特拉、贪心最佳优先、广度优先、深度优先等搜索算法，并可一键对比运行结果。
- **迷宫生成**：提供递归划分、随机深度优先、随机普里姆、基础随机、基础权重等迷宫生成策略。
- **动画演示**：分步展示节点探索、最短路径回溯与权重节点的创建过程，可调节动画播放速度。
- **交互式网格**：支持拖拽起点/终点、绘制墙体、添加权重节点以及清空画布。
- **结果统计**：自动统计探索步数、路径长度、路径花费与耗时，并以弹窗表格显示。

## 环境要求
- Python 3.10 及以上版本
- Pygame 及其他依赖（`pip install -r requirements.txt`）

## 安装与运行
1. 克隆项目：
   ```bash
   git clone https://github.com/<your-account>/Pathfinding-Visualizer.git
   cd Pathfinding-Visualizer
   ```
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 启动程序：
   - macOS / Linux：`python3 run.pyw`
   - Windows：`python run.pyw`

### 可选命令行参数
- `--cell-size:<int>`：调整单元格边长（像素），范围推荐 10–90，例如：
  ```bash
  python run.pyw --cell-size:32
  ```

## 使用指南
- **顶部控制栏**：选择算法、设置动画速度、启动可视化、批量运行对比或生成新迷宫。
- **绘制操作**：按住鼠标左键即可绘制墙体；同时按数字键（2–9）并拖动可创建权重节点；拖动起点/终点图标可快速变更位置。
- **结果查看**：完成可视化后将显示探索统计信息；若选择“全部运行”，会弹出详细对比表格。

## 相关资源
- 预览视频：[项目演示](https://user-images.githubusercontent.com/67793598/218127466-38274684-5eb6-44e9-b842-29720a26dd54.mp4)
- 示例截图位于 `screenshots/` 目录，可直接插入论文或报告。

## 文档与架构
详细的模块划分、类与函数说明请参阅 [docs/ARCHITECTURE_ZH.md](docs/ARCHITECTURE_ZH.md)。

## 许可协议
本项目采用 [MIT License](LICENSE)。欢迎在保留原作者署名的前提下修改与分发。
