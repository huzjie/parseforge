# 性能剖析

## 复杂度

- 版面检测：O(n_regions · n_types)，n_types=6 常数。
- 表格识别：O(n_rows · n_cols)。
- 图表序列：O(n_series · n_points)。
- 视觉塔：O(depth · n_patches^2 · dim)（自注意力平方项）。

## 零依赖的取舍

纯 Python 张量在 dim≤64、n_patches≤64 时秒级跑完（doctor/bench 都在 1~2 秒内）。
真实生产换 PyTorch/JAX 后端即可，算法结构不变——这正是「参考实现」的意义：把
**机制**讲清楚，性能留给加速库。
