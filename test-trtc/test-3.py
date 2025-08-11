import psutil
import time
import platform
import subprocess
import curses

def get_disk_info():
    system = platform.system()
    try:
        if system == "Windows":
            cmd = ['wmic', 'diskdrive', 'get', 'Model']
            result = subprocess.check_output(cmd, universal_newlines=True)
            lines = [line.strip() for line in result.split("\n") if line.strip() and "Model" not in line]
            return lines
        elif system == "Linux":
            cmd = ['lsblk', '-d', '-o', 'MODEL']
            result = subprocess.check_output(cmd, universal_newlines=True)
            lines = [line.strip() for line in result.split("\n") if line.strip() and "MODEL" not in line]
            return lines
        elif system == "Darwin":  # macOS
            cmd = ['system_profiler', 'SPStorageDataType']
            result = subprocess.check_output(cmd, universal_newlines=True)
            lines = [line.strip() for line in result.split("\n") if "Model:" in line]
            return [line.split(":")[1].strip() for line in lines]
    except Exception as e:
        return [f"取得失敗: {e}"]

def main(stdscr):
    curses.curs_set(0)  # 隱藏游標
    stdscr.nodelay(True)  # 不阻塞輸入
    disk_info = get_disk_info()
    disk_usage = psutil.disk_usage('/')

    while True:
        stdscr.clear()

        # 硬碟資訊
        stdscr.addstr(0, 0, "硬碟廠牌/型號：")
        for idx, model in enumerate(disk_info):
            stdscr.addstr(1 + idx, 2, model)

        # 硬碟容量
        disk_usage = psutil.disk_
