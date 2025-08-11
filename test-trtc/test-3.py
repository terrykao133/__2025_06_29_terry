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
        # PowerShell 指令：抓取硬碟型號與分割區對應
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

def main():
    disk_mapping = get_disk_mapping()
    net_old = psutil.net_io_counters()

    while True:
        os.system("cls")

        print("[硬碟與分割區對應]")
        for model, drives in disk_mapping.items():
            print(f"  {model}")
            for d in drives:
                try:
                    usage = psutil.disk_usage(d + "/")
                    print(f"    {d}")
                    print(f"      總容量   ：{format_size(usage.total)}")
                    print(f"      已使用   ：{format_size(usage.used)}")
                    print(f"      剩餘容量 ：{format_size(usage.free)}")
                    print(f"      使用率   ：{usage.percent:.1f}%")
                except Exception:
                    print(f"    {d}（無法讀取）")

        cpu_percent = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        print("\n[系統資源]")
        print(f"  CPU 使用率    ：{cpu_percent:.1f}%")
        print(f"  記憶體使用率  ：{mem.percent:.1f}% ({format_size(mem.used)} / {format_size(mem.total)})")

        net_new = psutil.net_io_counters()
        sent_speed = (net_new.bytes_sent - net_old.bytes_sent) / 1024
        recv_speed = (net_new.bytes_recv - net_old.bytes_recv) / 1024
        print("\n[網路即時速度]")
        print(f"  上傳：{sent_speed:.2f} KB/s")
        print(f"  下載：{recv_speed:.2f} KB/s")
        net_old = net_new

        print("\n(按 Ctrl+C 結束)")
        time.sleep(1)

if __name__ == "__main__":
    main()
