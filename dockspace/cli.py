# dockspace/cli.py
from __future__ import annotations

import argparse
from textwrap import indent

from . import disk_info
from .docker_info import get_docker_disk_summary, prune_docker_resources


def cmd_report(args: argparse.Namespace) -> None:
    print("=== WSL Disk Usage ===")
    for d in disk_info.get_wsl_disk_summary():
        print(f"- mount: {d.mount}")
        print(f"  total: {d.total_gb:.1f} GB")
        print(f"  used : {d.used_gb:.1f} GB ({d.percent_used:.1f}%)")
        print(f"  free : {d.free_gb:.1f} GB")
        print()

    print("=== Windows Temp Usage ===")
    try:
        temp = disk_info.get_windows_temp_usage()
        print(f"  path: {temp.path}")
        print(f"  size: {temp.total_gb:.2f} GB")
    except RuntimeError as e:
        print(f"  (error) {e}")
    print()

    print("=== Docker Disk Usage (docker system df) ===")
    try:
        docker_summary = get_docker_disk_summary()
        print(indent(docker_summary.raw_output.rstrip(), "  "))
    except RuntimeError as e:
        print(f"  (error) {e}")


def cmd_clean(args: argparse.Namespace) -> None:
    """사용하지 않는 Docker 리소스 정리 커맨드."""

    print("=== Docker Disk Usage (Before) ===")
    try:
        docker_summary = get_docker_disk_summary()
        print(indent(docker_summary.raw_output.rstrip(), "  "))
    except RuntimeError as e:
        print(f"  (error) {e}")
        return

    print()

    if not args.yes:
        print("[주의] 아래 Docker 리소스가 정리될 수 있습니다.")
        print(" - 기준: docker system prune", end="")
        if args.all:
            print(" -a", end="")
        if args.volumes:
            print(" --volumes", end="")
        print()
        answer = input("계속 진행할까요? [y/N]: ").strip().lower()
        if answer not in ("y", "yes"):
            print("취소되었습니다.")
            return

    ok, output = prune_docker_resources(
        all_images=args.all,
        volumes=args.volumes,
    )

    if not ok:
        print("❌ Docker clean 실행 중 오류가 발생했습니다:")
        print(indent(output.rstrip(), "  "))
        return

    print("✅ Docker clean 완료")
    if output.strip():
        print(indent(output.rstrip(), "  "))

    print()
    print("=== Docker Disk Usage (After) ===")
    try:
        docker_summary_after = get_docker_disk_summary()
        print(indent(docker_summary_after.raw_output.rstrip(), "  "))
    except RuntimeError as e:
        print(f"  (error) {e}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dockspace",
        description="WSL and Docker disk usage helper CLI",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # dockspace report
    report_parser = subparsers.add_parser(
        "report", help="Show WSL, Temp and Docker disk usage summary"
    )
    report_parser.set_defaults(func=cmd_report)

    # dockspace clean
    clean_parser = subparsers.add_parser(
        "clean",
        help="Prune unused Docker resources (wrapper around `docker system prune`)",
    )
    clean_parser.add_argument(
        "--all",
        action="store_true",
        help="Remove all unused images not just dangling ones (docker system prune -a)",
    )
    clean_parser.add_argument(
        "--volumes",
        action="store_true",
        help="Prune unused volumes as well (docker system prune --volumes)",
    )
    clean_parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Do not prompt for confirmation (non-interactive)",
    )
    clean_parser.set_defaults(func=cmd_clean)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
