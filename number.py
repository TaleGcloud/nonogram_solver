import cv2
import numpy as np

def parse_one_hint_block(block, row=False, index=-1, debug=-1, alpha=10):
    contours, _ = cv2.findContours(
        block,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )
    
    if row:
        contours, _ = sort_contours_left_to_right(contours)
    else:
        contours, _ = sort_contours_top_to_bottom(contours)
    
    numbers = []
    prev_box = None

    for i, c in enumerate(contours):
        x, y, w, h = cv2.boundingRect(c)
        digit_block = block[y:y+h, x:x+w]
        if w != h:
            # 以高度为正方形边长
            size = h
            # 创建黑色正方形底板
            square_img = np.zeros((size, size), dtype=np.uint8)
            # 计算居中偏移（只左右补）
            offset_x = (size - w) // 2
            # 贴到中间
            square_img[:, offset_x:offset_x + w] = digit_block
            digit_block = square_img
        
        digit_block = cv2.resize(digit_block, (50, 50), interpolation=cv2.INTER_LINEAR)

        if index == -1:
            cur_num = recognize_digit(digit_block, debug=debug)

            merge = False
            curr_box = (x, y, w, h)
            
            if prev_box is not None:
                px, py, pw, ph = prev_box
                cx, cy, cw, ch = curr_box

                if row:
                    gap = cx - (px + pw)
                    # if 0 <= gap < cw * (0.8 if cur_num == 1 or prev_num == 1 else alpha):
                    if 0 <= gap < alpha:
                        merge = True
                else:
                    curr_top = cy
                    curr_bottom = cy + ch
                    prev_top = py
                    prev_bottom = py + ph
                    overlap = min(curr_bottom, prev_bottom) - max(curr_top, prev_top)
                    if overlap > 0:
                        merge = True

            if merge:
                numbers[-1] = numbers[-1] * 10 + cur_num
            else:
                numbers.append(cur_num)
            prev_box = curr_box
        if index == i and debug != -1:
            cv2.imwrite(f"debug_digit_{debug}.png", digit_block)

    return numbers

def sort_contours_left_to_right(contours):
    boxes = [cv2.boundingRect(c) for c in contours]  # x, y, w, h

    sorted_pairs = sorted(
        zip(contours, boxes),
        key=lambda b: b[1][0]  # x
    )

    sorted_contours = [c for c, _ in sorted_pairs]
    sorted_boxes = [b for _, b in sorted_pairs]

    return sorted_contours, sorted_boxes

def sort_contours_top_to_bottom(contours):
    boxes = [cv2.boundingRect(c) for c in contours]  # x, y, w, h
    pairs = list(zip(contours, boxes))

    # 先按顶部 y 坐标粗略排序
    pairs.sort(key=lambda p: p[1][1])

    # 分组：重叠在同一行的放一起
    rows = []
    current_row = []
    last_bottom = -1

    for cnt, box in pairs:
        x, y, w, h = box
        top = y
        bottom = y + h

        if not current_row:
            current_row.append((cnt, box))
            last_bottom = bottom
        else:
            # 如果当前顶部 < 上一行底部 → 说明重叠，属于同一行
            if top < last_bottom - 5:  # -5 容错
                current_row.append((cnt, box))
                last_bottom = max(last_bottom, bottom)
            else:
                # 新行
                rows.append(current_row)
                current_row = [(cnt, box)]
                last_bottom = bottom

    if current_row:
        rows.append(current_row)

    # 每一行内部按 x 从左到右排序
    sorted_pairs = []
    for row in rows:
        row_sorted = sorted(row, key=lambda p: p[1][0])  # 按x排序
        sorted_pairs.extend(row_sorted)

    sorted_contours = [c for c, _ in sorted_pairs]
    sorted_boxes = [b for _, b in sorted_pairs]

    return sorted_contours, sorted_boxes

def recognize_digit_onnx(img):
    model = cv2.dnn.readNetFromONNX("mnist-12.onnx")
    # 自动缩放到 28x28（模型要求）
    # img = img.astype("float32") / 255.0

    # 丢进模型识别
    blob = cv2.dnn.blobFromImage(img)
    model.setInput(blob)
    pred = model.forward()

    return np.argmax(pred)  # 直接输出 0-9

def recognize_digit(img, debug=-1):
    best_score = float("inf")
    best_digit = 0

    # 遍历 0-9 模板
    for digit, template in enumerate(templates):
        # 计算像素差异（最简单、最稳定）
        diff = cv2.absdiff(img, template)
        score = np.sum(diff)
        
        if debug != -1:
            print(f"Digit {digit}: score = {score}")
            cv2.imwrite(f"debug_diff_{digit}.png", diff)

        # 分数越小，越像
        if score < best_score:
            best_score = score
            best_digit = digit

    return best_digit

templates = [cv2.imread(f"templates/{i}.png", cv2.IMREAD_GRAYSCALE) for i in range(10)]

if __name__ == "__main__":
    block = cv2.imread("debug_text_bound.png")
    gray = cv2.cvtColor(block, cv2.COLOR_BGR2GRAY)
    
    contours, _ = cv2.findContours(
        gray,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )
    
    for i, c in enumerate(contours):
        x, y, w, h = cv2.boundingRect(c)
        digit_block = gray[y:y+h, x:x+w]
        res = recognize_digit(digit_block)
        print(f"Digit {i}: {res}")