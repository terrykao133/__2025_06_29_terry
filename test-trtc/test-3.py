import psutil
import os
import time
import subprocess
import json

def get_disk_mapping():
    """
    使用 PowerShell 取得硬碟型號與分割區對應
    回傳 { '型號': ['C:', 'D:'] }
    """
    mapping = {}
    try:
        ps_cmd = r"""
        Get-PhysicalDisk | ForEach-Object {
            $model = $_.FriendlyName
            $devNum = (Get-Disk | Where-Object {$_.FriendlyName -eq $model}).Number
            $letters = (Get-Partition -DiskNumber $devNum | Get-Volume | Where-Object {$_.DriveLetter} | ForEach-Object { "$($_.DriveLetter):" })
            [PSCustomObject]@{ Model = $model; Letters = $letters }
        } | ConvertTo-Json
        """
        result = subprocess.check_output(["powershell", "-Command", ps_cmd], universal_newlines=True)
        disks = json.loads(result)
        for disk in disks:
            model = disk["Model"]
            letters = disk["Letters"]
            mapping[model] = letters if isinstance(letters, list) else [letters]
    except Exception as e:
        mapping[f"取得失敗: {e}"] = []
    return mapping

def format_size(bytes_size):
    return f"{bytes_size / (1024**3):.2f} GB"

def draw_box(title, lines):
    """
    繪製文字框
    title: 標題
    lines: 內容（list of str）
    """
    width = max(len(title), *(len(line) for line in lines)) + 4
    print("┌" + "─" * (width - 2) + "┐")
    print(f"│ {title.ljust(width-3)}│")
    print("├" + "─" * (width - 2) + "┤")
    for line in lines:
        print(f"│ {line.ljust(width-3)}│")
    print("└" + "─" * (width - 2) + "┘")

def main():
    disk_mapping = get_disk_mapping()
    net_old = psutil.net_io_counters()

    while True:
        os.system("cls")

        # 硬碟資訊
        disk_lines = []
        for model, drives in disk_mapping.items():
            disk_lines.append(model)
            for d in drives:
                try:
                    usage = psutil.disk_usage(d + "/")
                    disk_lines.append(f"  {d} | {usage.percent:.1f}% | {format_size(usage.used)} / {format_size(usage.total)}")
                except Exception:
                    disk_lines.append(f"  {d}（無法讀取）")
        draw_box("硬碟與分割區狀態", disk_lines)

        # 系統資源
        cpu_percent = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        sys_lines = [
            f"CPU 使用率   : {cpu_percent:.1f}%",
            f"記憶體使用率 : {mem.percent:.1f}% ({format_size(mem.used)} / {format_size(mem.total)})"
        ]
        draw_box("系統資源", sys_lines)

        # 網路速度
        net_new = psutil.net_io_counters()
        sent_speed = (net_new.bytes_sent - net_old.bytes_sent) / 1024  # KB/s
        recv_speed = (net_new.bytes_recv - net_old.bytes_recv) / 1024
        net_lines = [
            f"上傳: {sent_speed:.2f} KB/s",
            f"下載: {recv_speed:.2f} KB/s"
        ]
        draw_box("網路即時速度", net_lines)
        net_old = net_new

        print("\n(按 Ctrl+C 結束)")
        time.sleep(1)

if __name__ == "__main__":
    main()
