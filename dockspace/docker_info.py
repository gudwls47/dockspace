# dockspace/docker_info.py
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Tuple


@dataclass
class DockerDiskSummary:
    raw_output: str


def _run_docker_command(cmd: list[str]) -> Tuple[bool, str]:
    """
    Docker 관련 명령어를 실행하고 (성공 여부, stdout+stderr)를 반환한다.
    clean 서브커맨드에서 재사용하기 위한 내부 유틸 함수.
    """
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return False, "docker command not found. Is Docker installed and available?"

    output = ""
    if completed.stdout:
        output += completed.stdout
    if completed.stderr:
        if output:
            output += "\n"
        output += completed.stderr

    return completed.returncode == 0, output


def get_docker_disk_summary() -> DockerDiskSummary:
    """
    Run `docker system df` and return the raw output.

    나중에 여기서 파싱해서 이미지/컨테이너별 용량을 숫자로 뽑도록 확장할 수 있음.
    """
    ok, output = _run_docker_command(["docker", "system", "df"])
    if not ok:
        raise RuntimeError(output or "Failed to run 'docker system df'")
    return DockerDiskSummary(raw_output=output)


def prune_docker_resources(
    *, all_images: bool = False, volumes: bool = False
) -> Tuple[bool, str]:
    """
    Run `docker system prune` to remove unused Docker resources.

    Parameters
    ----------
    all_images : bool
        True이면 `-a` 옵션을 추가하여 어떤 컨테이너에서도 사용하지 않는 이미지까지 모두 삭제.
    volumes : bool
        True이면 `--volumes` 옵션을 추가하여 사용하지 않는 볼륨도 함께 삭제.

    Returns
    -------
    (success, output) : Tuple[bool, str]
        success가 False이면 output에 에러 메시지/표준에러 내용이 포함됨.
    """
    cmd = ["docker", "system", "prune", "-f"]
    if all_images:
        cmd.append("-a")
    if volumes:
        cmd.append("--volumes")

    return _run_docker_command(cmd)
