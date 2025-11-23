# dockspace/docker_info.py
from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass
class DockerDiskSummary:
    raw_output: str


def get_docker_disk_summary() -> DockerDiskSummary:
    """
    Run `docker system df` and return the raw output.

    나중에 여기서 파싱해서 이미지/컨테이너별 용량을 숫자로 뽑도록 확장할 수 있음.
    """
    try:
        completed = subprocess.run(
            ["docker", "system", "df"],
            capture_output=True,
            text=True,
            check=True,
        )
        return DockerDiskSummary(raw_output=completed.stdout)
    except FileNotFoundError:
        raise RuntimeError("docker command not found. Is Docker installed and available?")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to run 'docker system df': {e.stderr}")
