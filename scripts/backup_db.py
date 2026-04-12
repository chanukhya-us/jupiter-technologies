#!/usr/bin/env python3
from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "instance" / "app.db"
BACKUP_DIR = ROOT / "backups"


def main() -> int:
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = BACKUP_DIR / f"app_{timestamp}.db"
    shutil.copy2(DB_PATH, target)
    print(f"Database backup created: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
