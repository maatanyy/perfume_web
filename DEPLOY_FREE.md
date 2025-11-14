# 🆓 무료 배포 가이드 (가장 간단한 방법)

## 추천: Render (가장 간단함)

Render는 무료 티어가 좋고 설정이 매우 간단합니다.

### 1단계: GitHub에 코드 업로드

```bash
# 프로젝트 폴더에서
git init
git add .
git commit -m "Initial commit"

# GitHub에서 새 저장소 생성 후
git remote add origin https://github.com/사용자명/저장소명.git
git push -u origin main
```

### 2단계: Render에서 배포

1. **Render 가입**
   - https://render.com 접속
   - GitHub 계정으로 로그인

2. **새 Web Service 생성**
   - Dashboard에서 "New +" 클릭
   - "Web Service" 선택
   - GitHub 저장소 연결

3. **설정 입력**
   - **Name**: `perfume-crawler` (원하는 이름)
   - **Region**: `Singapore` (한국과 가까움)
   - **Branch**: `main`
   - **Root Directory**: `server` ⚠️ 중요!
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```bash
     uvicorn main:app --host 0.0.0.0 --port $PORT
     ```

4. **환경 변수 설정**
   - "Environment" 탭에서 추가:
     ```
     SECRET_KEY = your-secret-key-here-change-this
     DATABASE_URL = sqlite:///./price_crawler.db
     DATA_DIR = /opt/render/project/src  # JSONL 입력 파일 위치 (선택사항)
     OUTPUT_DIR = /opt/render/project/src  # Excel 출력 파일 위치 (선택사항)
     ```
   - `SECRET_KEY`는 랜덤 문자열 생성 (예: `openssl rand -hex 32`)
   - `DATA_DIR`: JSONL 입력 파일(`ssg_input_list.jsonl` 등)이 있는 디렉토리
     - 설정하지 않으면 프로젝트 루트에서 자동으로 찾습니다
   - `OUTPUT_DIR`: Excel 출력 파일이 저장될 디렉토리
     - 설정하지 않으면 프로젝트 루트에 저장됩니다

5. **배포**
   - "Create Web Service" 클릭
   - 자동으로 배포 시작 (약 5-10분 소요)

### 3단계: 입력 파일 업로드

배포 환경에서 JSONL 파일을 사용하려면:

**방법 1: Git 저장소에 포함 (권장)**
- `ssg_input_list.jsonl`, `ssg_shoping_input_list.jsonl` 등을 프로젝트 루트에 배치
- Git에 커밋하고 푸시
- Render가 자동으로 배포

**방법 2: 환경 변수로 경로 지정**
- Render 대시보드에서 `DATA_DIR` 환경 변수 설정
- 예: `DATA_DIR=/opt/render/project/src/data`
- 해당 디렉토리에 JSONL 파일 배치

**방법 3: 런타임에 업로드 (API 추가 필요)**
- 파일 업로드 API를 추가하여 런타임에 파일 업로드 가능

### 4단계: 클라이언트 설정 변경

배포 완료 후 Render에서 제공하는 URL을 받습니다 (예: `https://perfume-crawler.onrender.com`)

`client_new.py` 파일을 수정:

```python
# client_new.py 상단 부분
SERVER_URL = "https://perfume-crawler.onrender.com"  # Render URL로 변경
```

또는 환경 변수로 설정:
```python
import os
SERVER_URL = os.getenv("SERVER_URL", "https://perfume-crawler.onrender.com")
```

### 5단계: 클라이언트 빌드 (선택사항)

클라이언트를 실행 파일로 만들려면:

```bash
# PyInstaller 설치
pip install pyinstaller

# 실행 파일 생성
pyinstaller --onefile --add-data "templates;templates" client_new.py
```

---

## 대안 1: Railway (간단하지만 무료 티어 제한적)

### 배포 방법

1. **Railway 가입**
   - https://railway.app 접속
   - GitHub 계정으로 로그인

2. **프로젝트 생성**
   - "New Project" → "Deploy from GitHub repo"
   - 저장소 선택

3. **설정**
   - Root Directory: `server`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Environment Variables:
     ```
     SECRET_KEY=your-secret-key
     ```

4. **배포**
   - 자동으로 배포됨

---

## 대안 2: PythonAnywhere (Python 전용, 매우 간단)

### 배포 방법

1. **계정 생성**
   - https://www.pythonanywhere.com 접속
   - 무료 계정 생성

2. **파일 업로드**
   - Files 탭에서 `server` 폴더 내용 업로드
   - 또는 Git으로 클론

3. **Web App 생성**
   - Web 탭 → "Add a new web app"
   - Manual configuration → Python 3.10
   - Source code 경로 설정

4. **WSGI 파일 설정**
   ```python
   import sys
   path = '/home/사용자명/perfume/server'
   if path not in sys.path:
       sys.path.insert(0, path)
   
   from main import app
   application = app
   ```

5. **환경 변수 설정**
   - Web 탭 → "Environment variables"
   - `SECRET_KEY` 추가

---

## 무료 티어 비교

| 서비스 | 무료 티어 | 장점 | 단점 |
|--------|----------|------|------|
| **Render** | ✅ 무제한 (15분 비활성 시 슬립) | 가장 간단, 자동 배포 | 슬립 후 첫 요청 느림 |
| **Railway** | ⚠️ $5 크레딧/월 | 빠름, 자동 배포 | 크레딧 소진 시 유료 |
| **PythonAnywhere** | ✅ 제한적 무료 | Python 전용, 안정적 | 설정 복잡, 제한적 |

---

## 추천: Render 사용 이유

1. ✅ **가장 간단한 설정**
2. ✅ **무료 티어 충분** (개인 프로젝트용)
3. ✅ **자동 배포** (Git push 시 자동 업데이트)
4. ✅ **환경 변수 관리 쉬움**
5. ✅ **로그 확인 쉬움**

### Render 무료 티어 제한사항

- 15분간 요청 없으면 슬립 (첫 요청 시 약 30초 대기)
- 월 750시간 무료 (거의 무제한)
- 메모리 512MB

**해결책**: 슬립 방지를 위해 UptimeRobot 같은 무료 모니터링 서비스 사용

---

## 배포 후 확인사항

1. ✅ 서버 URL이 정상 작동하는지 확인
2. ✅ `/health` 엔드포인트 테스트
3. ✅ `/admin` 페이지 접속 확인
4. ✅ 클라이언트에서 서버 URL 변경
5. ✅ CORS 설정 확인 (이미 `allow_origins=["*"]`로 설정됨)

---

## 문제 해결

### Render에서 배포 실패 시

1. **로그 확인**
   - Render Dashboard → Logs 탭
   - 에러 메시지 확인

2. **일반적인 문제**
   - `Root Directory`가 `server`로 설정되었는지 확인
   - `requirements.txt` 경로 확인
   - Python 버전 확인 (3.10 이상 권장)

3. **데이터베이스 문제**
   - SQLite는 무료 티어에서 작동하지만, PostgreSQL 권장
   - Render에서 PostgreSQL 서비스 추가 가능 (무료 티어)

### 슬립 방지 (선택사항)

UptimeRobot (무료) 설정:
1. https://uptimerobot.com 가입
2. "Add New Monitor" → HTTP(s)
3. URL: `https://your-app.onrender.com/health`
4. Interval: 5분

---

## 다음 단계

배포 완료 후:
1. 관리자 비밀번호 변경 (`/admin`에서)
2. 클라이언트 실행 파일 배포 (필요 시)
3. 도메인 연결 (선택사항, Render Pro 필요)

