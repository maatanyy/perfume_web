# 경로 설정 가이드

## 개요

이 프로젝트는 배포 환경에서도 안전하게 작동하도록 **환경 변수 기반 경로 설정**을 지원합니다.

## 환경 변수

### DATA_DIR
- **용도**: JSONL 입력 파일(`ssg_input_list.jsonl` 등)이 있는 디렉토리
- **기본값**: 프로젝트 루트 (자동 감지)
- **예시**: `DATA_DIR=/opt/render/project/src/data`

### OUTPUT_DIR
- **용도**: Excel 출력 파일이 저장될 디렉토리
- **기본값**: 프로젝트 루트 (자동 감지)
- **예시**: `OUTPUT_DIR=/opt/render/project/src/output`

### PROJECT_ROOT
- **용도**: 프로젝트 루트 디렉토리 (고급 설정)
- **기본값**: 자동 감지 (`server/config.py` 기준)
- **예시**: `PROJECT_ROOT=/opt/render/project/src`

## 파일 검색 순서

입력 파일(`ssg_input_list.jsonl` 등)을 찾을 때 다음 순서로 검색합니다:

1. `DATA_DIR` 환경 변수가 설정된 경우: `{DATA_DIR}/{파일명}`
2. 프로젝트 루트: `{PROJECT_ROOT}/{파일명}`
3. 현재 작업 디렉토리: `{CWD}/{파일명}`
4. 상대 경로: `./{파일명}`

## 배포 환경 설정

### Render
```bash
# Environment Variables
DATA_DIR=/opt/render/project/src
OUTPUT_DIR=/opt/render/project/src
```

### Railway
```bash
# Environment Variables
DATA_DIR=/app
OUTPUT_DIR=/app
```

### 로컬 개발
환경 변수를 설정하지 않으면 자동으로 프로젝트 루트를 찾습니다.

## 파일 위치 권장사항

### 개발 환경
```
perfume/
├── server/
├── ssg_input_list.jsonl          # 프로젝트 루트에 배치
├── ssg_shoping_input_list.jsonl
└── ...
```

### 배포 환경
**방법 1: Git에 포함 (권장)**
- JSONL 파일을 프로젝트 루트에 배치
- Git에 커밋
- 자동으로 배포됨

**방법 2: 환경 변수 사용**
- `DATA_DIR` 환경 변수 설정
- 해당 디렉토리에 파일 배치

**방법 3: 런타임 업로드**
- 파일 업로드 API 구현 (향후 추가 가능)

## 문제 해결

### 파일을 찾을 수 없다는 에러가 발생하는 경우

1. **환경 변수 확인**
   ```bash
   echo $DATA_DIR
   ```

2. **파일 위치 확인**
   - 파일이 실제로 존재하는지 확인
   - 파일 경로가 올바른지 확인

3. **에러 메시지 확인**
   - 에러 메시지에 검색한 경로 목록이 표시됩니다
   - 해당 경로 중 하나에 파일을 배치하세요

4. **로그 확인**
   - 서버 로그에서 실제 검색 경로 확인

## 코드 예시

### 서버에서 경로 사용
```python
from server.config import get_data_dir, get_output_dir

data_dir = get_data_dir()  # 환경 변수 또는 자동 감지
config_file = os.path.join(data_dir, "ssg_input_list.jsonl")
```

### 크롤러에서 경로 사용
```python
# OUTPUT_DIR 환경 변수가 있으면 사용, 없으면 자동 감지
output_dir = os.getenv("OUTPUT_DIR") or get_executable_dir()
```

