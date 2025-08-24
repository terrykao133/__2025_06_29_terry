import logging

def setup_logger(logfile="system_monitor.log"):
    # 設定 logger
    logging.basicConfig(
        filename=logfile,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def main(interval=1.0):
    setup_logger()  # 初始化 logger

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

            # ===== 新增：寫入 log =====
            disk_logs = []
            for dev, info in disks_static.items():
                disk_logs.append(
                    f"{dev} {sizeof_fmt(info['used'])}/{sizeof_fmt(info['total'])} ({info['percent']:.1f}%)"
                )

            logging.info(
                f"CPU {cpu_pct:.1f}% | "
                f"Mem {sizeof_fmt(mem.used)}/{sizeof_fmt(mem.total)} ({mem.percent:.1f}%) | "
                f"Net ↑{sizeof_fmt(up_rate)}/s ↓{sizeof_fmt(down_rate)}/s | "
                f"Disks: {'; '.join(disk_logs)}"
            )

            # ===== Terminal UI 更新 =====
            layout = make_layout(cpu_pct, mem, {"up": up_rate, "down": down_rate}, disks_static)
            live.update(layout)

            time.sleep(interval)
