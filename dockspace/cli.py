# dockspace/cli.py
from __future__ import annotations

import argparse
from textwrap import indent

from .disk_info import get_wsl_disk_summary
from .docker_info import get_docker_disk_summary


def cmd_report(args: argparse.Namespace) -> None:
    print("=== WSL Disk Usage ===")
    for d in get_wsl_disk_summary():
        print(f"- mount: {d.mount}")
        print(f"  total: {d.total_gb:.1f} GB")
        print(f"  used : {d.used_gb:.1f} GB ({d.percent_used:.1f}%)")
        print(f"  free : {d.free_gb:.1f} GB")
        print()

    print("=== Docker Disk Usage (docker system df) ===")
    try:
        docker_summary = get_docker_disk_summary()
        print(indent(docker_summary.raw_output.rstrip(), "  "))
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
        "report", help="Show WSL and Docker disk usage summary"
    )
    report_parser.set_defaults(func=cmd_report)

    # 나중에 dockspace clean 같은 서브커맨드 추가 가능
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
