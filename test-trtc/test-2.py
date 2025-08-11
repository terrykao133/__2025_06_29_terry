#!/usr/bin/env python3
"""
每秒更新的系統監控（Terminal UI）。
依賴: psutil, rich
pip install psutil rich
"""

import sys
import time
import re
import platform
import subprocess
from collections import defaultdict

import psutil
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text


def strip_partition_suffix(devname: str) -> str:
    # /dev/sda1 -> sda
    # /dev/nvme0n1p1 -> nvme0n1
    b = devname.strip().split('/')[-1]
    # for nvme like nvme0n1p1 remove trailing 'p' + digits
    m = re.match(r'(?P<base>.+?)(p?\d+)$', b)
    if m:
        return m.group('base')
    return b


def get_disk_brand_model_by_sys(device_basename: str):
    """Try Linux sysfs path for vendor/model"""
    base_paths = [
        f"/sys/block/{device_basename}/device",
        f"/sys/block/{device_basename}"
    ]
    vendor = model = None
    for p in base_paths:
        try:
            with open(f"{p}/vendor", "r") as f:
                vendor = f.read().strip()
        except Exception:
            vendor = vendor
        try:
            with open(f"{p}/model", "r") as f:
                model = f.read().strip()
        except Exception:
            model = model
    return vendor, model


def get_disk_info():
    """
    Return mapping: device_path -> {mountpoint, fs, total, used, free, percent, vendor, model}
    Attempt to retrieve vendor/model via sysfs, lsblk, or wmic (Windows).
    """
    disks = {}
    # gather partitions
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except PermissionError:
            continue
        dev = part.device  # e.g. /dev/sda1 or C:\
        disks[dev] = {
            "mountpoint": part.mountpoint,
            "fstype": part.fstype,
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": usage.percent,
            "vendor": None,
            "model": None
        }

    # Try platform-specific ways to get vendor/model
    sysname = platform.system().lower()
    if sysname == "linux":
        # map device base names to model/vendor via /sys or lsblk
        # Build set of base devices
        base_to_devs = defaultdict(list)
        for dev in list(disks.keys()):
            base = strip_partition_suffix(dev)
            base_to_devs[base].append(dev)
        # first try sysfs
        for base, devs in base_to_devs.items():
            vendor, model = get_disk_brand_model_by_sys(base)
            if vendor or model:
                for d in devs:
                    disks[d]["vendor"] = vendor or disks[d]["vendor"]
                    disks[d]["model"] = model or disks[d]["model"]
        # if still missing, fallback to lsblk
        try:
            ls = subprocess.run(["lsblk", "-dn", "-o", "NAME,MODEL,VENDOR,SERIAL"], capture_output=True, text=True, check=False)
            if ls.returncode == 0:
                for line in ls.stdout.splitlines():
                    parts = line.split(None, 3)
                    if not parts:
                        continue
                    name = parts[0]
                    model = parts[1] if len(parts) > 1 else None
                    vendor = parts[2] if len(parts) > 2 else None
                    # match to dev keys
                    for d in disks.keys():
                        base = strip_partition_suffix(d)
                        if base == name:
                            if vendor:
                                disks[d]["vendor"] = vendor
                            if model:
                                disks[d]["model"] = model
        except Exception:
            pass

    elif sysname.startswith("win"):
        # Use wmic to get disk model
        try:
            w = subprocess.run(["wmic", "diskdrive", "get", "DeviceID,Model,Manufacturer,SerialNumber", "/format:csv"],
                               capture_output=True, text=True, check=False)
            if w.returncode == 0:
                # parse csv-like output
                lines = [l for l in w.stdout.splitlines() if l.strip()]
                # skip header (Node,DeviceID,Model,...)
                for line in lines[1:]:
                    parts = line.split(',')
                    if len(parts) >= 3:
                        # DeviceID like \\.\PHYSICALDRIVE0
                        dev_id = parts[1]
                        model = parts[2] if len(parts) > 2 else None
                        manuf = parts[3] if len(parts) > 3 else None
                        # map to psutil partitions by checking mountpoint's device (on Windows psutil device might be like '\\\\.\\PHYSICALDRIVE0' or 'C:\\')
                        for d in disks.keys():
                            if dev_id and dev_id.lower() in d.lower():
                                disks[d]["vendor"] = manuf
                                disks[d]["model"] = model
        except Exception:
            pass
    else:
        # MacOS or others: try system_profiler or diskutil
        try:
            sp = subprocess.run(["system_profiler", "SPSerialATADataType"], capture_output=True, text=True, check=False)
            if sp.returncode == 0:
                out = sp.stdout
                # crude parsing omitted; leave as future improvement
        except Exception:
            pass

    return disks


def sizeof_fmt(n, suffix="B"):
    # human readable
    for unit in ["", "K", "M", "G", "T", "P"]:
        if abs(n) < 1024.0:
            return f"{n:3.1f}{unit}{suffix}"
        n /= 1024.0
    return f"{n:.1f}Y{suffix}"


def make_layout(cpu_pct, mem, net_rate, disks_info):
    layout = Layout()
    # top: system (CPU / MEM / NET)
    top_table = Table.grid(expand=True)
    top_table.add_column(ratio=1)
    top_table.add_column(ratio=1)
    top_table.add_column(ratio=1)

    cpu_text = Text(f"CPU: {cpu_pct:.1f}%")
    mem_text = Text(f"Mem: {sizeof_fmt(mem.used)} / {sizeof_fmt(mem.total)} ({mem.percent:.1f}%)")
    net_text = Text(f"Net ↑ {sizeof_fmt(net_rate['up'])}/s  ↓ {sizeof_fmt(net_rate['down'])}/s")

    top_table.add_row(Panel(cpu_text, title="CPU", padding=(1, 2)),
                      Panel(mem_text, title="Memory", padding=(1, 2)),
                      Panel(net_text, title="Network", padding=(1, 2)))

    # disks table
    dtable = Table(title="Disks", expand=True)
    dtable.add_column("Device", no_wrap=True)
    dtable.add_column("Mount")
    dtable.add_column("FS")
    dtable.add_column("Total", justify="right")
    dtable.add_column("Used", justify="right")
    dtable.add_column("Free", justify="right")
    dtable.add_column("%", justify="right")
    dtable.add_column("Vendor / Model", overflow="fold")

    # sort by mountpoint for stable order
    for dev in sorted(disks_info.keys(), key=lambda d: disks_info[d]["mountpoint"]):
        info = disks_info[dev]
        vendor_model = " / ".join(x for x in (info.get("vendor") or "N/A", info.get("model") or "N/A"))
        dtable.add_row(dev, info["mountpoint"], info["fstype"],
                       sizeof_fmt(info["total"]),
                       sizeof_fmt(info["used"]),
                       sizeof_fmt(info["free"]),
                       f"{info['percent']:.1f}%",
                       vendor_model)

    layout.split_column(
        Layout(Panel(top_table), name="top", size=8),
        Layout(Panel(dtable), name="disks")
    )
    return layout


def main(interval=1.0):
    last_net = psutil.net_io_counters(pernic=False)
    last_bytes_sent = last_net.bytes_sent
    last_bytes_recv = last_net.bytes_recv

    # Pre-fetch disk info (we will refresh sizes each tick)
    disks_static = get_disk_info()

    with Live(refresh_per_second=4, screen=False) as live:
        while True:
            # CPU and memory
            cpu_pct = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()

            # network: compute bytes/sec
            net = psutil.net_io_counters(pernic=False)
            now_sent = net.bytes_sent
            now_recv = net.bytes_recv
            up_rate = max(0, now_sent - last_bytes_sent) / interval
            down_rate = max(0, now_recv - last_bytes_recv) / interval
            last_bytes_sent = now_sent
            last_bytes_recv = now_recv

            # refresh disk sizes & usage (do not re-query vendor/model every tick)
            for dev in list(disks_static.keys()):
                mp = disks_static[dev]["mountpoint"]
                try:
                    usage = psutil.disk_usage(mp)
                    disks_static[dev].update({
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent
                    })
                except Exception:
                    pass

            layout = make_layout(cpu_pct, mem, {"up": up_rate, "down": down_rate}, disks_static)
            live.update(layout)
            # sleep for interval seconds but cpu_percent with percpu already non-blocking
            time.sleep(interval)


if __name__ == "__main__":
    try:
        main(interval=1.0)
    except KeyboardInterrupt:
        print("Exit.")
        sys.exit(0)
