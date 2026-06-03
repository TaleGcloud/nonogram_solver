## Nonogram Solver

这是一个面向手机数织/Nonogram 的自动解题项目。

其中求解器的实现思路参考了 [Choimoe/NonogramSolver](https://github.com/Choimoe/NonogramSolver/blob/main/src/NonogramSolver.cpp)。

1. 从手机截图中识别棋盘区域。
2. 提取左侧和上方的提示数字。
3. 使用 Python 求解器计算答案。
4. 将求解结果转换为屏幕坐标并自动点击。

## 功能

- 识别棋盘大小和网格位置。
- 读取行提示和列提示。
- 生成并求解 nonogram 盘面。
- 根据解题结果自动点击需要填充的格子。

## 目录说明

- `main.py`：主入口，负责截图、识别、求解和点击。
- `nonogram_solver.py`：数织求解器，包含模式生成、约束传播和回溯搜索。
- `number.py`：识别提示数字。
- `contorl.py`：封装截图、点击、滑动等手机控制操作。

## 使用方式

直接运行主程序即可：

```bash
python main.py
```

运行后会：

- 通过手机截图生成 `screen.png`。
- 自动解析提示数字。
- 调用 `NonogramSolver` 计算解。
- 点击需要填充的位置。

如果你想单独测试求解器，也可以直接运行 `nonogram_solver.py` 里的示例数据。

## 题目数据约定

- 左边的提示数字对应 `rows`，也就是每一行的约束。
- 上面的提示数字对应 `cols`，也就是每一列的约束。
- 在 `number.py` 里，`row=True` 表示提示块是纵向排列的，`row=False` 表示横向排列的。

## 环境要求

- Python 3.14 或更高版本
- `opencv-python`
- 可选：Android 调试环境和可用的截图/点击控制实现

## 相关文件

- [main.py](main.py)
- [nonogram_solver.py](nonogram_solver.py)
- [number.py](number.py)
- [contorl.py](contorl.py)
