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

## 环境配置（保姆级指南）

### 1. 安装 Python

**Windows 系统：**

1. 访问 Python 官网下载页面：https://www.python.org/downloads/
2. 点击 **Download Python 3.10.x** 或更高版本下载安装包
3. 运行安装程序，**重要**：勾选 "Add Python to PATH"（将 Python 添加到系统环境变量）
4. 点击 "Install Now" 完成安装

**macOS 系统：**

```bash
# 使用 Homebrew 安装
brew install python@3.10
```

**Linux 系统：**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### 2. 验证 Python 安装

打开终端（Windows 按 `Win + R`，输入 `cmd`；macOS 按 `Cmd + Space`，搜索 "Terminal"），输入：

```bash
python --version
# 或
python3 --version
```

应显示 Python 3.8.x 或更高版本，例如：`Python 3.10.9`

### 3. 配置环境变量（Windows 补充）

如果安装时未勾选 "Add Python to PATH"，手动配置：

1. 按 `Win + R`，输入 `sysdm.cpl`，回车
2. 点击 **高级** → **环境变量**
3. 在 **系统变量** 中找到 `Path`，双击编辑
4. 点击 **新建**，添加以下路径：
   - `C:\Users\你的用户名\AppData\Local\Programs\Python\Python310`
   - `C:\Users\你的用户名\AppData\Local\Programs\Python\Python310\Scripts`
5. 点击 **确定** 保存

### 4. 克隆或下载项目

```bash
# 如果使用 Git
git clone https://github.com/Tatakai/deepracer-notebook.git
cd deepracer-notebook

# 或者直接解压下载的 ZIP 文件到指定目录
```

### 5. 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 6. 安装依赖

```bash
pip install -r requirements.txt
```

### 7. 验证安装

```bash
python -c "import numpy, scipy, matplotlib, ipython; print('依赖安装成功！')"
```

如果显示 "依赖安装成功！" 则说明所有依赖已正确安装。

### 8. 运行项目

```bash
jupyter notebook DeepRacer_Workflow.ipynb
```

浏览器会自动打开 Jupyter Notebook 界面，按顺序运行所有单元格即可。

---

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
