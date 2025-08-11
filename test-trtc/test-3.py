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
