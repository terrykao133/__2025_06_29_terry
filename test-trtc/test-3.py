import psutil
import os
import time
import subprocess

def get_disk_mapping():
    """
    取得 Windows 實體硬碟型號 與 對應分割區
    回傳格式：
    {
        "WDC WD10EZEX-08WN4A0": ["C:/", "D:/"],
        "SAMSUNG SSD 860 EVO": ["E:/"]
    }
    """
    mapping = {}
    try:
        # 查詢硬碟型號與對應裝置ID
        cmd = ['wmic', 'diskdrive', 'get', 'Model,DeviceID']
        result = subprocess.check_output(cmd, universal_newlines=True)
        lines = [line.strip() for line in result.split("\n") if line.strip() and "Model" not in line]

        for line in lines:
            parts = line.split()
            if not parts:
                continue
            # 最後一個欄位是 DeviceID，其餘是 Model 名稱
            device_id = parts[-1]
            model = " ".join(parts[:-1])

            # 查詢這顆硬碟的 partitions
            cmd2 = ['wmic', 'diskdrive', 'where', f"DeviceID='{device_id}'", 'assoc', '/assocclass:Win32_DiskDriveToDiskPartition']
            result2 = subprocess.check_output(cmd2, universal_newlines=True
