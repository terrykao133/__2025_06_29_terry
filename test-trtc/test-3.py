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
        # 取得所有硬碟型號與DeviceID
        cmd = ['wmic', 'diskdrive', 'get', 'Model,DeviceID', '/format:csv']
        result = subprocess.check_output(cmd, universal_newlines=True)
        lines = [line for line in result.splitlines() if line and "Model" not in line and "Node" not in line]
        for line in lines:
            parts = line.split(',')
            if len(parts) < 3:
                continue
            device_id = parts[2].strip()
            model = parts[1].strip()
            # 取得分割區
            cmd2 = [
                'wmic', 'diskdrive', 'where', f"DeviceID='{device_id}'",
                'assoc', '/assocclass:Win32_DiskDriveToDiskPartition'
            ]
            result2 = subprocess.check_output(cmd2, universal_newlines=True)
            partitions = []
            for l in result2.splitlines():
                if "DeviceID=" in l:
                    partition_id = l.split('=')[1].strip().replace('"', '')
                    # 取得分割區對應的邏輯磁碟
                    cmd3 = [
                        'wmic', 'partition', 'where', f"DeviceID='{partition_id}'",
                        'assoc', '/assocclass:Win32_LogicalDiskToPartition'
                    ]
                    result3 = subprocess.check_output(cmd3, universal_newlines=True)
                    for ll in result3.splitlines():
                        if "DeviceID=" in ll:
                            drive_letter = ll.split('=')[1].strip().replace('"', '')
                            partitions.append(drive_letter)
            mapping[model] = partitions
    except Exception as e:
        print(f"取得硬碟資訊失敗: {e}")
    return mapping

if __name__ == "__main__":
    disk_info = get_disk_mapping()
    for model, partitions in disk_info.items():
        print(f"硬碟型號: {model}, 分割區: {', '.join(partitions)}")
