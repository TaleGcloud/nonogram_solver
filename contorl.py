import subprocess

# 执行 ADB 命令（通用函数）
def adb(cmd):
    """执行 ADB 命令，返回结果"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        return result.stdout, result.stderr
    except Exception as e:
        return "", str(e)

def screenshot(save_path="screen.png"):
    adb(f"adb exec-out screencap -p > {save_path}")
    # print(f"✅ 截图完成：{save_path}")

def click(x, y):
    adb(f"adb shell input tap {x} {y}")
    # print(f"✅ 点击坐标：({x}, {y})")
    
def swipe(x1, y1, x2, y2, duration=200):
    adb(f"adb shell input swipe {x1} {y1} {x2} {y2} {duration}")
    print(f"✅ 滑动：({x1}, {y1}) -> ({x2}, {y2}), 持续 {duration}ms")

if __name__ == "__main__":
    screenshot()
    click(1060, 1000)
    swipe(650, 800, 650, 1700)