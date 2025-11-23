# dockspace/disk_info.py
from __future__ import annotations

import shutil
from pathlib import Path
from dataclasses import dataclass


@dataclass
class DiskUsage:
    mount: str
    total_gb: float
    used_gb: float
    free_gb: float
    percent_used: float


def _disk_usage_for_path(path: str) -> DiskUsage:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"{path} does not exist")

    usage = shutil.disk_usage(path)
    total_gb = usage.total / (1024 ** 3)
    free_gb = usage.free / (1024 ** 3)
    used_gb = total_gb - free_gb
    percent_used = used_gb / total_gb * 100 if total_gb > 0 else 0.0

    return DiskUsage(
        mount=path,
        total_gb=total_gb,
        used_gb=used_gb,
        free_gb=free_gb,
        percent_used=percent_used,
    )


def get_wsl_disk_summary() -> list[DiskUsage]:
    """Check a few typical mount points in WSL."""
    mounts = ["/", "/mnt/c"]
    result: list[DiskUsage] = []
    for m in mounts:
        try:
            result.append(_disk_usage_for_path(m))
        except FileNotFoundError:
            # /mnt/c 같은게 없을 수도 있으니 그냥 스킵
            continue
    return result
