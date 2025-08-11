def main():
    disk_mapping = get_disk_mapping()
    net_old = psutil.net_io_counters()

    # Print once outside the loop to create placeholders and fix line counts if needed
    while True:
        # Move the cursor to the top-left corner (0,0) - works in Windows 10+ with VT mode enabled, or in modern terminals
        print("\033[H", end="")

        # The rest is unchanged
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

        cpu_percent = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        sys_lines = [
            f"CPU 使用率   : {cpu_percent:.1f}%",
            f"記憶體使用率 : {mem.percent:.1f}% ({format_size(mem.used)} / {format_size(mem.total)})"
        ]
        draw_box("系統資源", sys_lines)

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
