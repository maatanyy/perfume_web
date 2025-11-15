"""서버 설정"""
import os
from pathlib import Path


def get_project_root():
    """프로젝트 루트 경로 반환"""
    # 환경 변수로 명시적으로 설정된 경우
    project_root = os.getenv("PROJECT_ROOT")
    if project_root:
        return os.path.abspath(project_root)
    
    # server/config.py -> server/ -> 프로젝트 루트
    current_file = Path(__file__)
    server_dir = current_file.parent
    project_root = server_dir.parent
    return str(project_root.resolve())


def get_data_dir():
    """데이터 파일 디렉토리 경로 반환"""
    data_dir = os.getenv("DATA_DIR")
    if data_dir:
        return os.path.abspath(data_dir)

    project_root = Path(get_project_root())
    server_dir = Path(__file__).resolve().parent

    candidates = [
        project_root / "data",
        project_root / "server" / "data",
        server_dir / "data",
    ]

    for candidate in candidates:
        if candidate.exists():
            return str(candidate.resolve())

    return str(project_root)


def get_output_dir():
    """출력 파일 디렉토리 경로 반환"""
    # 환경 변수로 명시적으로 설정된 경우
    output_dir = os.getenv("OUTPUT_DIR")
    if output_dir:
        return os.path.abspath(output_dir)
    
    # 기본값: 프로젝트 루트
    return get_project_root()

