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

    # Pre-fetch disk info (we will
