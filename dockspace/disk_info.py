# dockspace/disk_info.py
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Iterable


# ---------- 기본 WSL 디스크 요약 ----------

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


# ---------- Windows Temp usage ----------

@dataclass
class PathUsage:
    path: Path
    total_bytes: int

    @property
    def total_gb(self) -> float:
        return self.total_bytes / (1024 ** 3)


def _detect_windows_username() -> Optional[str]:
    """
    Try to detect the Windows username from WSL by calling cmd.exe.

    Returns None if detection fails.
    """
    try:
        completed = subprocess.run(
            ["cmd.exe", "/C", "echo", "%USERNAME%"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        # cmd.exe를 못 부르는 환경일 수도 있음
        return None

    if completed.returncode != 0:
        return None

    name = completed.stdout.strip()
    name = name.replace("\r", "").replace("\n", "")
    return name or None


def _fallback_windows_user(dir_iter: Iterable[os.DirEntry]) -> Optional[str]:
    """
    /mnt/c/Users 아래에서 적당한 사용자 디렉토리 하나를 고른다.
    Public, Default 계정 등은 제외.
    """
    candidates: list[str] = []
    for entry in dir_iter:
        if not entry.is_dir():
            continue
        if entry.name in ("Public", "Default", "Default User", "All Users"):
            continue
        if entry.name.startswith("Default"):
            continue
        candidates.append(entry.name)

    return candidates[0] if candidates else None


def get_windows_temp_path() -> Path:
    """
    추정되는 Windows Temp 경로를 반환한다.

    보통:
      C:\\Users\\<사용자>\\AppData\\Local\\Temp
    WSL에서는:
      /mnt/c/Users/<사용자>/AppData/Local/Temp
    """
    base = Path("/mnt/c/Users")
    if not base.exists():
        raise RuntimeError("'/mnt/c/Users' not found. Are you running under WSL with C: mounted?")

    username = _detect_windows_username()
    if not username:
        # cmd.exe로 못 알아냈으면 /mnt/c/Users 하위 디렉토리에서 하나 고르기
        with os.scandir(base) as it:
            username = _fallback_windows_user(it)

    if not username:
        raise RuntimeError("Failed to detect Windows user directory under /mnt/c/Users")

    temp_path = base / username / "AppData" / "Local" / "Temp"
    if not temp_path.exists():
        raise RuntimeError(f"Windows Temp path not found: {temp_path}")

    return temp_path


def get_directory_size_bytes(path: Path) -> int:
    """주어진 디렉토리의 전체 파일 크기 합계를 바이트 단위로 계산."""
    total = 0
    for root, dirs, files in os.walk(path):
        for name in files:
            p = Path(root) / name
            try:
                st = p.stat()
            except (FileNotFoundError, PermissionError):
                # 사라진 파일 / 권한 없는 파일은 건너뛰기
                continue
            total += st.st_size
    return total


def get_windows_temp_usage() -> PathUsage:
    """
    Windows Temp 디렉토리의 사용량을 계산한다.
    WSL 기준으로는 /mnt/c/Users/<사용자>/AppData/Local/Temp 경로를 사용.
    """
    try:
        # WSL 스타일(/mnt/c/Users/...) 우선 시도
        temp_path = get_windows_temp_path()
    except RuntimeError:
        # /mnt/c/Users가 없거나 사용자 디렉토리 추정 실패한 경우 → OS 기본 temp 사용
        temp_path = Path(tempfile.gettempdir())

    if not temp_path.exists():
        raise RuntimeError(f"Temp directory not found: {temp_path}")

    total_bytes = get_directory_size_bytes(temp_path)
    return PathUsage(path=temp_path, total_bytes=total_bytes)

__all__ = [
    "DiskUsage",
    "get_wsl_disk_summary",
    "PathUsage",
    "get_windows_temp_path",
    "get_directory_size_bytes",
    "get_windows_temp_usage",
]
