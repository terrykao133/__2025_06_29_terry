import psutil
import sys
import time

def format_size(bytes_size):
    """將容量自動轉換單位"""
    for unit in ['B','KB','MB','GB','TB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} PB"

def print_section(title, lines):
    """簡單輸出區塊（沒有框線）"""
    print(f"【{title}】")
    for line in lines:
        print(line)
    print()

def main():
    net_old = psutil.net_io_counters()
    disk_io_old = psutil.disk_io_counters()

    while True:
        # ANSI 控制碼，移到左上角並清除畫面
        sys.stdout.write("\033[H\033[J")
        sys.stdout.flush()

        # 硬碟資訊（只靠 psutil）
        disk_lines = []
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disk_lines.append(
                    f"{part.device} ({part.mountpoint}) | {usage.percent:.1f}% | {format_size(usage.used)} / {format_size(usage.total)}"
                )
            except PermissionError:
                disk_lines.append(f"{part.device} ({part.mountpoint}) | 無法讀取")
        print_section("硬碟與分割區狀態", disk_lines)

        # 系統資源
        cpu_percent = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        sys_lines = [
            f"CPU 使用率   : {cpu_percent:.1f}%",
            f"記憶體使用率 : {mem.percent:.1f}% ({format_size(mem.used)} / {format_size(mem.total)})"
        ]
        print_section("系統資源", sys_lines)

        # 網路速度
        net_new = psutil.net_io_counters()
        sent_speed = (net_new.bytes_sent - net_old.bytes_sent) / 1024  # KB/s
        recv_speed = (net_new.bytes_recv - net_old.bytes_recv) / 1024
        net_lines = [
            f"上傳: {sent_speed:.2f} KB/s",
            f"下載: {recv_speed:.2f} KB/s"
        ]
        print_section("網路即時速度", net_lines)
        net_old = net_new

        # 磁碟 I/O 速度
        disk_io_new = psutil.disk_io_counters()
        read_speed = (disk_io_new.read_bytes - disk_io_old.read_bytes) / 1024 / 1024  # MB/s
        write_speed = (disk_io_new.write_bytes - disk_io_old.write_bytes) / 1024 / 1024
        io_lines = [
            f"讀取: {read_speed:.2f} MB/s",
            f"寫入: {write_speed:.2f} MB/s"
        ]
        print_section("磁碟 I/O 即時速度", io_lines)
        disk_io_old = disk_io_new

        print("(按 Ctrl+C 結束)")
        time.sleep(1)

if __name__ == "__main__":
    main()
