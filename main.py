import cv2

from number import parse_one_hint_block
from nonogram_solver import NonogramSolver, _format_grid
from contorl import screenshot, click, swipe

def deal(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, bound = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)
    _, text = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
    
    cv2.imwrite("debug_bound.png", bound)
    cv2.imwrite("debug_text.png", text)

    contours, _ = cv2.findContours(
        bound,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    bounds = []
    grid_id = 0
    best_area = 0

    for i, c in enumerate(contours):
        x, y, w, h = cv2.boundingRect(c)
        bounds.append((x, y, w, h))

        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 3)
        cv2.putText(img, f"{i}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        area = w * h

        if area > best_area:
            best_area = area
            grid_id = i

    return bounds, grid_id, text
        
def coord(solution, bound):
    # 取出棋盘在屏幕上的 左上角x、左上角y、总宽度、总高度
    board_x, board_y, board_w, board_h = bound
    
    # 获取网格的 行数、列数
    rows = len(solution)
    cols = len(solution[0]) if rows > 0 else 0
    
    # 计算每个格子的宽高
    cell_w = board_w / cols
    cell_h = board_h / rows
    
    coords = []
    for r, row in enumerate(solution):
        for c, cell in enumerate(row):
            if cell == 2:
                # 计算格子在屏幕上的中心点
                x = board_x + c * cell_w + cell_w / 2
                y = board_y + r * cell_h + cell_h / 2
                coords.append((int(x), 400 + int(y)))  # 转整数，给adb用
    
    return coords

def extract_text():
    img = cv2.imread("data/all.png")[400:1800]
    bounds, grid_id, text = deal(img)
    nums = [(2, 1), (3, 1), (5, 0), (3, 0), (0, 0), (8, 0), (7, 0), (5, 1), (1, 0), (19, 0)]
    for i, num in enumerate(nums):
        x, y, w, h = bounds[num[0]]
        block = text[y:y+h, x:x+w]
        res = parse_one_hint_block(block, row=num[0]>grid_id, index=num[1], debug=i)
        print(res)

if __name__ == "__main__":
    # extract_text()

    screenshot()   # 截图

    img = cv2.imread("screen.png")[400:1800]
    
    bounds, grid_id, text = deal(img)
    x, y, w, h = bounds[grid_id]
    print(grid_id)
    print(x, y, w, h)
    
    alphas = {5: 16, 10: 15, 15: 10, 20: 7}

    rows = []
    print(" ==> row:")
    for i in range(grid_id):
        x, y, w, h = bounds[i]
        block = text[y:y+h, x:x+w]
        res = parse_one_hint_block(block, row=True, alpha=alphas[grid_id])
        rows.append(res)
    rows.reverse()
    print(rows)
    
    cols = []
    print(" ==> col:")
    for i in range(grid_id):
        x, y, w, h = bounds[grid_id + 1 + i]
        block = text[y:y+h, x:x+w]
        res = parse_one_hint_block(block, row=False, alpha=alphas[grid_id])
        cols.append(res)
    cols.reverse()
    print(cols)
    
    solver = NonogramSolver(rows, cols)
    solutions = solver.solve()

    print(f"solutions: {len(solutions)}")
    for index, solution in enumerate(solutions, start=1):
        print(f"solution {index}")
        print(_format_grid(solution))
    
    coords = coord(solutions[0], bounds[grid_id])

    for x, y in coords:
        click(x, y)