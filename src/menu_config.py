from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from .pathfinder.models.search_types import Search


@dataclass(frozen=True)
class AlgorithmDefinition:
    """Represents a path-finding algorithm option exposed to the UI."""

    label: str
    search: Search


class SpeedSetting(str, Enum):
    """Possible animation speeds for the maze visualiser."""

    FAST = "快速"
    MEDIUM = "中速"
    SLOW = "慢速"


ALGORITHM_DEFINITIONS: Sequence[AlgorithmDefinition] = (
    AlgorithmDefinition("A* 搜索", Search.ASTAR_SEARCH),
    AlgorithmDefinition("迪杰斯特拉搜索", Search.DIJKSTRAS_SEARCH),
    AlgorithmDefinition("贪心最佳优先搜索", Search.GREEDY_BEST_FIRST_SEARCH),
    AlgorithmDefinition("广度优先搜索", Search.BREADTH_FIRST_SEARCH),
    AlgorithmDefinition("深度优先搜索", Search.DEPTH_FIRST_SEARCH),
)

ALGORITHMS_BY_LABEL = {definition.label: definition for definition in ALGORITHM_DEFINITIONS}

SPEED_OPTIONS: Sequence[SpeedSetting] = (
    SpeedSetting.FAST,
    SpeedSetting.MEDIUM,
    SpeedSetting.SLOW,
)

COMPARISON_OPTIONS: Sequence[str] = ("当前迷宫", "不同迷宫")

GENERATION_OPTIONS: Sequence[str] = (
    "递归划分",
    "普里姆算法",
    "随机深度优先",
    "基本随机迷宫",
    "基本权重迷宫",
)
