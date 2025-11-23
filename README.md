# dockspace

> WSL 환경에서 **디스크 사용량**과 **Docker가 차지하는 용량**을 한 번에 확인할 수 있는 작은 CLI 도구입니다.

Windows + WSL + Docker Desktop 조합에서 개발하다 보면,  
어느 순간 C 드라이브와 WSL 디스크가 꽉 차서 당황하는 일이 자주 생깁니다.

`dockspace`는 다음 정보를 한 번에 보여주는 **로컬 전용** CLI입니다.

- WSL 루트(`/`) 및 Windows 디스크(`/mnt/c`) 사용량 요약  
- `docker system df` 결과를 보기 좋게 출력  
- “어디가 얼마나 차지하고 있는지”를 빠르게 파악할 수 있는 리포트  

아직은 **정리/삭제(clean)** 기능 없이, **리포트(report)** 기능만 제공합니다.  
향후 이미지/컨테이너별 상세 분석 및 정리 기능까지 확장하는 것을 목표로 합니다.

---

## Features

- ✅ WSL 내 주요 마운트 포인트의 디스크 사용량 요약  
  - 기본: `/`, `/mnt/c`  
- ✅ Docker 디스크 사용량 요약  
  - `docker system df` 실행 결과를 보기 좋게 출력  
- ✅ 간단한 서브커맨드 기반 CLI 인터페이스  
  - `dockspace report` 한 번으로 전체 요약  

---

## Requirements

- Python 3.10+  
- WSL (Ubuntu 등)  
- Docker CLI가 설치되어 있고 `docker system df` 명령이 동작할 것  
  (Docker가 없으면 해당 부분은 에러 메시지로 안내됩니다)

---

## Installation (개발용)

현재는 개발용으로 `editable` 설치를 기준으로 합니다.

```bash
git clone https://github.com/gudwls47/dockspace.git
cd dockspace

# 가상환경(optional) 생성
python -m venv .venv
source .venv/bin/activate  # Windows WSL 기준, PowerShell이면 .\.venv\Scripts\activate

# 패키지 설치 (editable)
pip install -e .
```

---

## Usage

WSL 및 Docker 디스크 사용량을 한 번에 보고 싶다면:

```bash
dockspace report
```
### 예상 출력 예시
```
=== WSL Disk Usage ===
- mount: /
  total: 100.0 GB
  used : 60.5 GB (60.5%)
  free : 39.5 GB

- mount: /mnt/c
  total: 475.0 GB
  used : 430.2 GB (90.6%)
  free : 44.8 GB

=== Docker Disk Usage (docker system df) ===
  TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
  Images          15        5         30.45GB   20.12GB (66%)
  Containers      8         3         2.34GB    1.10GB (47%)
  Local Volumes   5         5         4.56GB    0B (0%)
  Build Cache                        10.23GB    8.00GB (78%)
```
실제 값은 환경에 따라 달라집니다.

---

## Project Structure
```
dockspace/
  ├─ dockspace/
  │   ├─ __init__.py
  │   ├─ cli.py          # CLI 엔트리포인트 (argparse 기반)
  │   ├─ disk_info.py    # WSL 디스크 사용량 관련 로직
  │   └─ docker_info.py  # Docker 디스크 사용량 관련 로직
  ├─ pyproject.toml      # 패키지 설정 및 entry point 정의
  ├─ README.md
  └─ .gitignore
```

---

## Roadmap / TODO
- [ ] docker system df --format 옵션을 사용한 JSON 파싱 지원

- [ ] 이미지/컨테이너별 사용량 숫자 파싱 후 “삭제 시 확보 가능한 용량” 추정치 계산

- [ ] dockspace clean --dry-run
    - 실제 삭제 없이, 어떤 리소스를 지우면 얼마나 확보되는지 시뮬레이션

- [ ] Windows 환경에서 WSL 디스크(VHDX) 크기까지 포함한 요약 (연구 예정)
