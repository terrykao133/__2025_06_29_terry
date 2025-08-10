import psutil
import time
from datetime import datetime

def bytes_to_gb(bytes):
    return bytes / (1024 ** 3)

def monitor_system(interval=1):
    net_io_prev = psutil.net_io_counters()

    while True:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 取得當前時間字串

        disk_usage = psutil.disk_usage('/')
        used_gb = bytes_to_gb(disk_usage.used)
        free_gb = bytes_to_gb(disk_usage.free)

        cpu_percent = psutil.cpu_percent(interval=None)

        mem = psutil.virtual_memory()
        mem_total_gb = bytes_to_gb(mem.total)
        mem_used_gb = bytes_to_gb(mem.used)
        mem_free_gb = bytes_to_gb(mem.available)

        net_io = psutil.net_io_counters()
        bytes_sent_speed = (net_io.bytes_sent - net_io_prev.bytes_sent) / interval
        bytes_recv_speed = (net_io.bytes_recv - net_io_prev.bytes_recv) / interval
        net_io_prev = net_io

        print(f"[{now}]")
        print(f"硬碟已使用容量: {used_gb:.2f} GB, 剩餘容量: {free_gb:.2f} GB")
        print(f"CPU使用率: {cpu_percent:.2f} %")
        print(f"記憶體總容量: {mem_total_gb:.2f} GB, 使用中: {mem_used_gb:.2f} GB, 可用: {mem_free_gb:.2f} GB")
        print(f"網路傳送速率: {bytes_sent_speed / 1024:.2f} KB/s, 接收速率: {bytes_recv_speed / 1024:.2f} KB/s")
        print("-" * 40)

        time.sleep(interval)

if __name__ == "__main__":
    monitor_system(interval=1)
