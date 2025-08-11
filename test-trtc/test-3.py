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
        disk_usage = psutil.disk_usage('/')
        stdscr.addstr(4, 0, f"硬碟總容量：{disk_usage.total / (1024**3):.2f} GB")
        stdscr.addstr(5, 0, f"已使用容量：{disk_usage.used / (1024**3):.2f} GB")
        stdscr.addstr(6, 0, f"剩餘容量　：{disk_usage.free / (1024**3):.2f} GB")
        stdscr.addstr(7, 0, f"使用率　　：{disk_usage.percent:.1f}%")

        # CPU / 記憶體
        cpu_percent = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        stdscr.addstr(9, 0, f"CPU 使用率：{cpu_percent:.1f}%")
        stdscr.addstr(10, 0, f"記憶體使用率：{mem.percent:.1f}% ({mem.used / (1024**3):.2f} / {mem.total / (1024**3):.2f} GB)")

        # 網路
        net = psutil.net_io_counters()
        stdscr.addstr(12, 0, f"網路傳送：{net.bytes_sent / (1024**2):.2f} MB")
        stdscr.addstr(13, 0, f"網路接收：{net.bytes_recv / (1024**2):.2f} MB")

        stdscr.addstr(15, 0, "按 Q 退出")
        stdscr.refresh()

        try:
            key = stdscr.getch()
            if key in (ord('q'), ord('Q')):
                break
        except:
            pass

        time.sleep(1)

if __name__ == "__main__":
    curses.wrapper(main)
