import psutil
import os
import time
import subprocess
import json
import sys

def get_disk_mapping():
    """
    使用 PowerShell 取得硬碟型號與分割區對應
    回傳 { '型號': ['C:', 'D:'] }
    """
    mapping = {}
    try:
        ps_cmd = r"""
        Get-PhysicalDisk | ForEach-Object {
            $disk = Get-Disk -Number $_.DeviceId
            $letters = (Get-Partition -DiskNumber $disk.Number | Get-Volume | Where-Object {$_.DriveLetter} | ForEach-Object { "$($_.DriveLetter):" })
            [PSCustomObject]@{ Model = $_.FriendlyName; Letters = $letters }
        } | ConvertTo-Json
        """
        result = subprocess.check_output(["powershell.exe", "-Command", ps_cmd], universal_newlines=True)
        disks = json.loads(result)
        if isinstance(disks, dict):  # 單顆磁碟時 json 是 dict
            disks = [disks]
        for disk in disks:
            model = disk["Model"]
            letters = disk["Letters"]
            mapping[model] = letters if isinstance(letters, list) else [letters]
    except Exception as e:
        mapping[f"取得失敗: {e}"] = []
    return mapping

def format_size(bytes_size):
    """將容量自動轉換單位"""
    for unit in ['B','KB','MB','GB','TB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} PB"

def draw_box(title, lines):
    """繪製文字框"""
    width = max(len(title), *(len(line) for line in lines)) + 4
    box = []
    box.append("┌" + "─" * (width - 2) + "┐")
    box.append(f"│ {title.ljust(width-3)}│")
    box.append("├" + "─" * (width - 2) + "┤")
    for line in lines:
        box.append(f"│ {line.ljust(width-3)}│")
    box.append("└" + "─" * (width - 2) + "┘")
    return "\n".join(box)

def main():
    disk_mapping = get_disk_mapping()
    net_old = psutil.net_io_counters()
    disk_io_old = psutil.disk_io_counters()

    while True:
        # ANSI 控制碼，移到左上角並清除畫面
        sys.stdout.write("\033[H\033[J")
        sys.stdout.flush()

        # 硬碟資訊
        disk_lines = []
        for model, drives in disk_mapping.items():
            disk_lines.append(model)
            for d in drives:
                try:
                    usage = psutil.disk_usage(d + "\\")
                    disk_lines.append(f"  {d} | {usage.percent:.1f}% | {format_size(usage.used)} / {format_size(usage.total)}")
                except Exception:
                    disk_lines.append(f"  {d}（無法讀取）")
        print(draw_box("硬碟與分割區狀態", disk_lines))

        # 系統資源
        cpu_percent = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        sys_lines = [
            f"CPU 使用率   : {cpu_percent:.1f}%",
            f"記憶體使用率 : {mem.percent:.1f}% ({format_size(mem.used)} / {format_size(mem.total)})"
        ]
        print(draw_box("系統資源", sys_lines))

        # 網路速度
        net_new = psutil.net_io_counters()
        sent_speed = (net_new.bytes_sent - net_old.bytes_sent) / 1024  # KB/s
        recv_speed = (net_new.bytes_recv - net_old.bytes_recv) / 1024
        net_lines = [
            f"上傳: {sent_speed:.2f} KB/s",
            f"下載: {recv_speed:.2f} KB/s"
        ]
        print(draw_box("網路即時速度", net_lines))
        net_old = net_new

        # 磁碟 I/O 速度
        disk_io_new = psutil.disk_io_counters()
        read_speed = (disk_io_new.read_bytes - disk_io_old.read_bytes) / 1024 / 1024  # MB/s
        write_speed = (disk_io_new.write_bytes - disk_io_old.write_bytes) / 1024 / 1024
        io_lines = [
            f"讀取: {read_speed:.2f} MB/s",
            f"寫入: {write_speed:.2f} MB/s"
        ]
        print(draw_box("磁碟 I/O 即時速度", io_lines))
        disk_io_old = disk_io_new

        print("\n(按 Ctrl+C 結束)")
        time.sleep(1)

if __name__ == "__main__":
    main()
