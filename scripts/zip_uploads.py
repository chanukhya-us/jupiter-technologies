#!/usr/bin/env python3
from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPLOADS_DIR = ROOT / "uploads"
BACKUP_DIR = ROOT / "backups"


def main() -> int:
    if not UPLOADS_DIR.exists():
        print(f"Uploads directory not found at {UPLOADS_DIR}")
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_base = BACKUP_DIR / f"uploads_{timestamp}"
    archive_path = shutil.make_archive(str(archive_base), "zip", str(UPLOADS_DIR))
    print(f"Uploads backup created: {archive_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
