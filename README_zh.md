# DeepRacer 赛道线优化 — Notebook 工作流

用于 AWS DeepRacer 赛道优化的 Jupyter Notebook 工作流，包含安全距离约束和摩擦圆速度剖面计算。

[English](./README.md) | **中文**

---

## 项目简介

本项目提供完整的 5 步工作流，用于计算最优赛车线和速度剖面：

| 步骤 | 描述 | 输出 |
|------|------|------|
| 1 | 赛道 npy 文件导出为 CSV | `waypoints.csv` |
| 2 | 计算最优赛车线（带安全距离） | 赛车线坐标 |
| 3 | 速度剖面与到达时间 | 每点速度和到达时间 |
| 4 | 四维赛车线数据 | `[x, y, speed, time]` 用于可视化 |
| 5 | 奖励函数 | AWS DeepRacer 奖励函数代码 |

## 项目结构

```
deepracer-notebook/
├── DeepRacer_Workflow.ipynb   # 主 Notebook（5步工作流）
├── core.py                     # 核心函数：compute_racing_line(), npy_to_csv()
├── assets/
│   └── visualize.html          # 浏览器端赛道与赛车线可视化工具
├── requirements.txt            # Python 依赖
├── tests/
│   └── test_core.py            # 单元测试
├── README.md                   # 英文说明
├── README_zh.md                # 中文说明
└── map/
    └── reinvent_base.npy       # 默认赛道文件
```

## 快速开始

1. **安装依赖：**
   ```bash
   pip install -r requirements.txt
   ```

2. **启动 Notebook：**
   ```bash
   jupyter notebook DeepRacer_Workflow.ipynb
   ```

3. **按顺序运行所有单元格**

## 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `safety_distance` | 0.2 m | 赛道边界最小安全距离 |
| `line_iterations` | 2000 | 赛车线优化迭代次数 |
| `xi_iterations` | 4 | 每点二分查找深度 |
| `min_speed` / `max_speed` | 1.0 / 3.0 m/s | 速度上下限 |
| `look_ahead_points` | 1 | 前视点数（速度计算时向前看的弯道数） |

## 算法原理

**赛车线优化**使用梯度下降 + 二分搜索：
1. 从赛道中心线出发
2. 调整每点位置使曲率在相邻点间平滑过渡，同时保持与赛道边界的安全距离
3. 迭代 2000 次收敛

**速度剖面**采用摩擦圆模型：
- 横向加速度：a_lat = v² × κ ≤ μ × g
- 前向传播计算加速限制，后向传播计算制动限制

## visualize.html

在浏览器中打开 `assets/visualize.html` 可以：
- 导入 `waypoints.csv` 查看赛道边界
- 粘贴四维赛车线数据可视化速度分布（红色=低速，绿色=高速）

## 赛道数据格式

支持的 npy 文件结构：
- **字典/对象：** 包含 `center_line`/`waypoints`、`left_border`/`inner_border`、`right_border`/`outer_border` 键
- **数组 (N,6)：** 交错排列 `[cx,cy, ix,iy, ox,oy]`
- **数组 (N,4)：** `[inner_x, inner_y, outer_x, outer_y]`
- **数组 (N,2)：** 仅中心线（需配合其他数据才能优化）

---

## 相关资源

### 官方文档

- [AWS DeepRacer 官方文档](https://docs.aws.amazon.com/deepracer/)
- [AWS DeepRacer 控制台](https://console.aws.amazon.com/deepracer/)
- [AWS DeepRacer 定价](https://aws.amazon.com/deepracer/pricing/)
- [AWS DeepRacer 联赛](https://aws.amazon.com/deepracer/league/)

### 开源项目

- **[cdthompson/deepracer-k1999-race-lines](https://github.com/cdthompson/deepracer-k1999-race-lines)** — 使用连续曲率算法计算 DeepRacer 各赛道最优赛车线，基于 Rémi Coulom 博士论文方法，提供多个赛道的 npy 坐标文件和 Python 计算代码
- **[aws-samples/aws-deepracer-workshops](https://github.com/aws-samples/aws-deepracer-workshops)** — AWS 官方 DeepRacer 工作流与训练指南，包含 DPR-401 高级训练内容和日志分析工具
- **[owenps/Raceline_Optimization](https://github.com/owenps/Raceline_Optimization)** — 使用遗传算法优化 DeepRacer 赛车线

### 赛道资源

- **赛道 npy 文件**：`cdthompson/deepracer-k1999-race-lines` 仓库中包含多个官方赛道的预计算赛车线（Canada_Training、reinvent_base、reInvent2019 等）

---

## 许可

MIT
