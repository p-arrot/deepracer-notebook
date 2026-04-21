"""
deepracer_notebook_core.py
===========================
将 bast_safe.py 和 visualize.py 中 notebook 所需的核心函数整合在一起，
使其不依赖上级目录的代码，可独立在 deepracer-notebook/ 下运行。

用法:
    from core import compute_racing_line, npy_to_csv
"""

import numpy as np
from shapely.geometry import Point, Polygon, LineString
import copy


# ─────────────────────────────────────────────────────────────────────────────
# 赛道数据加载
# ─────────────────────────────────────────────────────────────────────────────

def load_track_waypoints(track_path):
    """
    加载赛道 npy 文件，返回 center_line, inner_border, outer_border 三个 (N,2) 数组。

    支持的 npy 格式:
    - 数组形状 (N,6): [cx,cy, ix,iy, ox,oy] 交错排列
    - 字典/对象格式: 含 center_line/waypoints, inner_border/left_border,
                    outer_border/right_border 键
    """
    data = np.load(track_path, allow_pickle=True)

    if data.dtype == object or isinstance(data, dict):
        data = data.item()
        center_line = np.array(data.get('center_line') or data.get('waypoints'))
        inner_border = np.array(data.get('inner_border') or data.get('left_border'))
        outer_border = np.array(data.get('outer_border') or data.get('right_border'))
    else:
        if data.ndim == 2 and data.shape[1] == 6:
            center_line = data[:, 0:2]
            inner_border = data[:, 2:4]
            outer_border = data[:, 4:6]
        elif data.ndim == 2 and data.shape[1] == 4:
            inner_border = data[:, 0:2]
            outer_border = data[:, 2:4]
            center_line = (inner_border + outer_border) / 2
        elif data.ndim == 2 and data.shape[1] == 2:
            center_line = data
            raise ValueError("单有中心线时无法计算安全距离，请提供含边界的 npy 文件")
        else:
            raise ValueError(f"不支持的 npy 格式: shape={data.shape}")

    return center_line, inner_border, outer_border


# ─────────────────────────────────────────────────────────────────────────────
# 曲率计算
# ─────────────────────────────────────────────────────────────────────────────

def menger_curvature(pt1, pt2, pt3, atol=1e-3):
    """计算三点构成的 Menger 曲率 (1/r)。"""
    vec21 = np.array([pt1[0] - pt2[0], pt1[1] - pt2[1]])
    vec23 = np.array([pt3[0] - pt2[0], pt3[1] - pt2[1]])

    norm21 = np.linalg.norm(vec21)
    norm23 = np.linalg.norm(vec23)

    if norm21 < atol or norm23 < atol:
        return 0.0

    theta = np.arccos(np.clip(np.dot(vec21, vec23) / (norm21 * norm23), -1.0, 1.0))

    if np.isclose(theta - np.pi, 0.0, atol=atol):
        theta = 0.0

    dist13 = np.linalg.norm(vec21 - vec23)
    if dist13 < atol:
        return 0.0

    return 2 * np.sin(theta) / dist13


# ─────────────────────────────────────────────────────────────────────────────
# 赛车线优化（带安全距离）
# ─────────────────────────────────────────────────────────────────────────────

def improve_race_line(old_line, inner_border, outer_border, safety_distance,
                      xi_iterations=4):
    """
    梯度下降单次扫描：调整赛道线上每个点的位置，使曲率在相邻点之间平滑过渡，
    同时确保点与赛道边界的距离不小于 safety_distance。
    """
    ls_inner = LineString(inner_border)
    ls_outer = LineString(outer_border)
    new_line = copy.deepcopy(old_line)
    npoints = len(new_line)

    for i in range(npoints):
        xi = new_line[i]
        prev = (i - 1 + npoints) % npoints
        nexxt = (i + 1) % npoints
        prevprev = (i - 2 + npoints) % npoints
        nexxtnexxt = (i + 2 + npoints) % npoints

        ci = menger_curvature(new_line[prev], xi, new_line[nexxt])
        c1 = menger_curvature(new_line[prevprev], new_line[prev], xi)
        c2 = menger_curvature(xi, new_line[nexxt], new_line[nexxtnexxt])
        target_ci = (c1 + c2) / 2

        xi_bound1 = copy.deepcopy(xi)
        xi_bound2 = ((new_line[nexxt][0] + new_line[prev][0]) / 2.0,
                     (new_line[nexxt][1] + new_line[prev][1]) / 2.0)
        p_xi = copy.deepcopy(xi)

        for _ in range(xi_iterations):
            p_ci = menger_curvature(new_line[prev], p_xi, new_line[nexxt])

            if np.isclose(p_ci, target_ci, atol=1e-4):
                break

            if p_ci < target_ci:
                xi_bound2 = copy.deepcopy(p_xi)
                new_p_xi = ((xi_bound1[0] + p_xi[0]) / 2.0,
                            (xi_bound1[1] + p_xi[1]) / 2.0)
            else:
                xi_bound1 = copy.deepcopy(p_xi)
                new_p_xi = ((xi_bound2[0] + p_xi[0]) / 2.0,
                            (xi_bound2[1] + p_xi[1]) / 2.0)

            p_point = Point(new_p_xi)
            dist_i = p_point.distance(ls_inner)
            dist_o = p_point.distance(ls_outer)
            if dist_i >= safety_distance and dist_o >= safety_distance:
                p_xi = new_p_xi
            else:
                if p_ci < target_ci:
                    xi_bound1 = copy.deepcopy(new_p_xi)
                else:
                    xi_bound2 = copy.deepcopy(new_p_xi)

        new_line[i] = p_xi

    return new_line


def optimize_race_line(race_line, inner_border, outer_border, safety_distance,
                       line_iterations=2000, xi_iterations=4, verbose=True):
    """多次扫描整个赛道，迭代优化赛车线。"""
    line = copy.deepcopy(race_line)
    for i in range(line_iterations):
        line = improve_race_line(line, inner_border, outer_border,
                                safety_distance, xi_iterations)
        if verbose and i % 200 == 0:
            print(f"  迭代 {i}/{line_iterations}")
    return line


def compute_racing_line(track_path, safety_distance=0.2,
                        line_iterations=2000, xi_iterations=4, verbose=True):
    """
    主入口函数：加载赛道并计算保留安全距离的最优赛车线。

    参数:
        track_path: 赛道 npy 文件路径
        safety_distance: 与赛道边界的最小安全距离（默认 0.2 米）
        line_iterations: 优化迭代次数（默认 2000）
        xi_iterations: 每点二分查找深度（默认 4）
        verbose: 是否打印进度

    返回:
        racing_line: (N,2) 赛车线坐标数组（闭合，首尾点相同）
        waypoints: dict，含 center_line, inner_border, outer_border
    """
    if verbose:
        print(f"加载赛道: {track_path}")
    center_line, inner_border, outer_border = load_track_waypoints(track_path)

    if verbose:
        print(f"赛道点数: {len(center_line)}, 安全距离: {safety_distance}")

    init_line = center_line[:-1] if np.allclose(center_line[0], center_line[-1]) else center_line

    if verbose:
        print("开始优化赛车线...")
    racing_line = optimize_race_line(
        init_line, inner_border, outer_border, safety_distance,
        line_iterations=line_iterations,
        xi_iterations=xi_iterations,
        verbose=verbose
    )

    loop_race_line = np.append(racing_line, [racing_line[0]], axis=0)

    if verbose:
        ls_orig = LineString(center_line)
        ls_new = LineString(loop_race_line)
        print(f"原中心线长度: {ls_orig.length:.2f}")
        print(f"优化后赛车线长度: {ls_new.length:.2f}")

    waypoints = {
        'center_line': center_line,
        'inner_border': inner_border,
        'outer_border': outer_border,
    }

    return loop_race_line, waypoints


# ─────────────────────────────────────────────────────────────────────────────
# npy → CSV 导出
# ─────────────────────────────────────────────────────────────────────────────

def npy_to_csv(npy_path, csv_path=None):
    """
    将赛道 npy 文件导出为 waypoints.csv。

    参数:
        npy_path: 赛道 npy 文件路径
        csv_path:  输出的 CSV 路径（默认为同目录下的 waypoints.csv）
    """
    if csv_path is None:
        import os
        csv_path = os.path.join(os.path.dirname(npy_path), 'waypoints.csv')

    waypoints = np.load(npy_path)
    np.savetxt(csv_path, waypoints, delimiter=',',
               header='center_x,center_y,inner_x,inner_y,outer_x,outer_y',
               comments='')
    print(f"✅ 已导出为 {csv_path}")
