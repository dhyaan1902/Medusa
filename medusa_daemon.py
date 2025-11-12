# medusa_daemon.py
import os
import time
from medusa_core import load_config, run_downloads, LAST_RUN_FILE

def hours_since_last_run():
    try:
        if not os.path.exists(LAST_RUN_FILE):
            return float('inf')
        return (time.time() - os.path.getmtime(LAST_RUN_FILE)) / 3600.0
    except Exception:
        return float('inf')

def main():
    cfg = load_config()
    if not cfg.get("auto_refresh", False):
        print("Auto refresh disabled in config. Exiting.")
        return
    interval = float(cfg.get("refresh_hours", 24.0))
    if hours_since_last_run() < max(0.1, interval):
        print("Not time yet. Exiting.")
        return
    print("Running Medusa daemon downloads...")
    paths = run_downloads(cfg)
    print(f"Downloaded {len(paths)} images")

if __name__ == "__main__":
    main()
