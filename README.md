# dockspace : WSL·Docker 디스크 정리 도와주는 CLI

> WSL / Windows 환경에서 **디스크 사용량**과 **Docker가 차지하는 용량**,  
> 그리고 **Windows Temp 폴더 용량**까지 한 번에 확인하고,  
> 필요하면 `docker system prune` 기반으로 정리까지 할 수 있는 작은 CLI 도구입니다.

Windows + WSL + Docker Desktop 조합에서 개발하다 보면,  
어느 순간 C 드라이브와 WSL 디스크가 꽉 차서 당황하는 일이 자주 생깁니다.

`dockspace`는 다음 정보를 한 번에 보여주는 **로컬 전용** CLI입니다.

- WSL 루트(`/`) 및 Windows 디스크(`/mnt/c`) 사용량 요약  
- Windows Temp 디렉토리 사용량 (`C:\Users\<you>\AppData\Local\Temp` 등)  
- `docker system df` 결과를 보기 좋게 출력  
- 필요 시 `docker system prune` 래핑으로 Docker 리소스 정리

---

## Features

- ✅ WSL / Windows 디스크 사용량 요약  
  - 기본: `/`, `/mnt/c` (WSL)  
  - 순수 Windows에서 실행해도 `/` 기준으로 요약 출력
- ✅ Windows Temp 사용량 확인  
  - WSL: `/mnt/c/Users/<사용자>/AppData/Local/Temp` 기준  
  - Windows: `tempfile.gettempdir()` (보통 `C:\Users\<사용자>\AppData\Local\Temp`)
- ✅ Docker 디스크 사용량 요약  
  - `docker system df` 실행 결과를 보기 좋게 출력  
- ✅ 간단한 서브커맨드 기반 CLI 인터페이스  
  - `dockspace report` 한 번으로 전체 요약  
  - `dockspace clean` 으로 안전한 기본 Docker 정리 실행  
    - 내부적으로 `docker system prune` 래핑

---

## Requirements

- Python 3.10+  
- (권장) WSL (Ubuntu 등) + Docker Desktop  
- Docker CLI가 설치되어 있고 `docker system df`, `docker system prune` 명령이 동작할 것  
  - Docker가 없으면 해당 부분은 에러 메시지로 안내됩니다

---

## Installation (개발용)

로컬에서 editable 설치를 기준으로 합니다.

```bash
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

=== Windows Temp Usage ===
  path: C:\Users\<you>\AppData\Local\Temp
  size: 19.73 GB

=== Docker Disk Usage (docker system df) ===
  TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
  Images          15        5         30.45GB   20.12GB (66%)
  Containers      8         3         2.34GB    1.10GB (47%)
  Local Volumes   5         5         4.56GB    0B (0%)
  Build Cache                        10.23GB    8.00GB (78%)
```
실제 값은 환경에 따라 달라집니다.

---

## 사용하지 않는 Docker 리소스 정리
`docker system prune`을 직접 치기 전에, `dockspace`를 통해 정리 전/후 사용량을 같이 보고 싶다면:
```bash
dockspace clean
```

기본 동작:
- 정리 전 `docker system df` 출력
- 사용자 확인 프롬프트
- 내부적으로 `docker system prune -f` 실행
- 정리 후 다시 `docker system df` 출력

조금 더 강한 정리가 필요하다면:
```bash
# 어떤 컨테이너에서도 사용하지 않는 이미지까지 삭제
dockspace clean --all

# 사용하지 않는 볼륨까지 삭제
dockspace clean --volumes

# 둘 다 + 확인 프롬프트 없이 바로 실행
dockspace clean --all --volumes -y
```

내부적으로는 다음과 같이 매핑:
- `dockspace clean` → `docker system prune -f`
- `dockspace clean --all` → `docker system prune -f -a`
- `dockspace clean --volumes` → `docker system prune -f --volumes`
- `dockspace clean --all --volumes` → `docker system prune -f -a --volumes`

⚠️ `--all`, `--volumes` 옵션은 삭제 범위가 넓어질 수 있으니
실제로 어떤 컨테이너/이미지가 필요한지 확인 후 사용하는 것을 권장합니다.

---

## Project Structure
```
dockspace/
  ├─ dockspace/
  │   ├─ __init__.py
  │   ├─ cli.py          # CLI 엔트리포인트 (argparse 기반)
  │   ├─ disk_info.py    # WSL/Windows 디스크 및 Temp 사용량 관련 로직
  │   └─ docker_info.py  # Docker 디스크 사용량 및 prune 래핑 로직
  ├─ pyproject.toml      # 패키지 설정 및 entry point 정의
  ├─ README.md
  └─ .gitignore
```
