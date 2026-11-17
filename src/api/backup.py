"""
Database Backup & Disaster Recovery Automation for VyaparMitra.
Provides consistent online SQLite snapshots and automated retention pruning.
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from src.api.config import get_api_config

logger = logging.getLogger("vyaparmitra.api.backup")


def create_database_backup(
    db_path: Optional[Path | str] = None,
    backup_dir: Optional[Path | str] = None,
    retain_count: int = 10,
) -> Dict[str, Any]:
    """
    Takes an atomic online snapshot of the SQLite database using sqlite3.backup API.
    Safely prunes old snapshots keeping the latest `retain_count` backups.
    """
    config = get_api_config()
    source_path = Path(db_path or config.db_path).resolve()

    if not source_path.exists():
        raise FileNotFoundError(f"Source database file not found at {source_path}")

    dest_dir = Path(backup_dir or (config.data_dir / "backups")).resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_filename = f"vyaparmitra_backup_{timestamp}.db"
    dest_path = dest_dir / backup_filename

    # Perform atomic online SQLite backup
    src_conn = sqlite3.connect(str(source_path), timeout=30.0)
    dst_conn = sqlite3.connect(str(dest_path), timeout=30.0)
    try:
        with dst_conn:
            src_conn.backup(dst_conn, pages=100)
    finally:
        dst_conn.close()
        src_conn.close()

    size_bytes = dest_path.stat().st_size
    logger.info("Successfully created database backup: %s (%d bytes)", dest_path.name, size_bytes)

    # Prune older backups beyond retain_count
    all_backups = sorted(
        dest_dir.glob("vyaparmitra_backup_*.db"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    pruned_count = 0
    if len(all_backups) > retain_count:
        for old_backup in all_backups[retain_count:]:
            try:
                old_backup.unlink()
                pruned_count += 1
            except Exception as e:
                logger.warning("Could not prune old backup %s: %s", old_backup, e)

    return {
        "success": True,
        "backup_file": str(dest_path),
        "filename": backup_filename,
        "size_bytes": size_bytes,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "retained_backups": len(all_backups) - pruned_count,
        "pruned_backups": pruned_count,
    }


if __name__ == "__main__":
    import json
    result = create_database_backup()
    print(json.dumps(result, indent=2))
