import psutil
import platform
import subprocess
import os
import time

def get_disk_info():
    system = platform.system()
    try:
        if system == "Windows":
            cmd = ['powershell', '-Command', 'Get-PhysicalDisk | Select-Object -ExpandProperty FriendlyName']
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

def main():
    disk_info = get_disk_info()
    prev_net = psutil.net_io_counters()

    while True:
        # 清除螢幕
        os.system('cls' if os.name == 'nt' else 'clear')

        # 硬碟資訊
        print("=== 硬碟廠牌/型號 ===")
        for model in disk_info:
            print(f"  {model}")

        # 硬碟使用狀況
        usage = psutil.disk_usage('/')
        print("\n=== 硬碟使用狀況 ===")
        print(f"  總容量　：{usage.total / (1024**3):.2f} GB")
        print(f"  已使用　：{usage.used / (1024**3):.2f} GB")
        print(f"  剩餘容量：{usage.free / (1024**3):.2f} GB")
        print(f"  使用率　：{usage.percent:.1f}%")

        # CPU 與記憶體
        cpu_percent = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        print("\n=== 系統資源 ===")
        print(f"  CPU 使用率：{cpu_percent:.1f}%")
        print(f"  記憶體使用率：{mem.percent:.1f}% ({mem.used / (1024**3):.2f} / {mem.total / (1024**3):.2f} GB)")

        # 網路流量（計算本秒收發）
        net = psutil.net_io_counters()
        sent_speed = (net.bytes_sent - prev_net.bytes_sent) / 1024  # KB/s
        recv_speed = (net.bytes_recv - prev_net.bytes_recv) / 1024
        prev_net = net
        print("\n=== 網路即時速率 ===")
        print(f"  傳送：{sent_speed:.2f} KB/s")
        print(f"  接收：{recv_speed:.2f} KB/s")

        print("\n(按 Ctrl+C 結束)")

        time.sleep(1)

if __name__ == "__main__":
    main()
