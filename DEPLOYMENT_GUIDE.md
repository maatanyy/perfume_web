# 🚀 배포 가이드 (상세)

## 1. URL 설정 방법

### 배포 후 URL 구조

**Render 배포 시:**
- 서버 URL: `https://your-app-name.onrender.com`
- 관리자 페이지: `https://your-app-name.onrender.com/admin` (또는 설정한 경로)
- API 문서: `https://your-app-name.onrender.com/docs`

**URL 지정 방법:**
1. Render는 자동으로 `https://{서비스명}.onrender.com` 형식의 URL을 제공
2. 커스텀 도메인 연결 가능 (Render Pro 플랜 필요)
3. 서비스명은 Render 대시보드에서 변경 가능

### 관리자 페이지 경로 변경

**환경 변수로 설정:**
```bash
ADMIN_PATH=/secure-admin-panel-2024
```

**Render에서 설정:**
1. Dashboard → Your Service → Environment
2. Key: `ADMIN_PATH`
3. Value: `/secure-admin-panel-2024` (원하는 경로)

**보안 강화 팁:**
- 복잡한 경로 사용: `/admin-xyz123-secure-2024`
- 환경 변수로 관리하여 코드에 노출되지 않도록
- 정기적으로 경로 변경

## 2. GitHub 연동 및 자동 배포

### Render와 GitHub 연동

1. **GitHub 저장소 준비**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/사용자명/저장소명.git
   git push -u origin main
   ```

2. **Render에서 GitHub 연결**
   - Render Dashboard → "New +" → "Web Service"
   - "Connect GitHub" 클릭
   - 저장소 선택
   - 자동으로 연결됨

3. **자동 배포 설정**
   - Render는 기본적으로 **자동 배포 활성화**
   - `main` 브랜치에 푸시하면 자동으로 배포 시작
   - 배포 상태는 Dashboard에서 실시간 확인 가능

### 자동 배포 작동 방식

**자동 배포가 트리거되는 경우:**
- ✅ `main` 브랜치에 `git push` 할 때
- ✅ Pull Request가 `main`에 머지될 때
- ✅ Render Dashboard에서 "Manual Deploy" 클릭 시

**배포 프로세스:**
1. GitHub에서 최신 코드 가져오기
2. `Build Command` 실행 (의존성 설치)
3. `Start Command` 실행 (서버 시작)
4. 헬스 체크 확인
5. 배포 완료

**배포 시간:**
- 첫 배포: 약 5-10분
- 이후 배포: 약 3-5분 (변경사항에 따라 다름)

## 3. 여러 유저 동시 사용 시 동작

### 현재 아키텍처

**사용자별 독립 작업:**
- 각 사용자는 자신의 크롤링 작업을 독립적으로 실행
- `crawler_instances` 딕셔너리로 사용자별 작업 관리:
  ```python
  crawler_instances = {
      user_id_1: {job_id_1: crawler_instance},
      user_id_2: {job_id_2: crawler_instance}
  }
  ```

**동시 실행 가능:**
- ✅ 여러 사용자가 동시에 크롤링 시작 가능
- ✅ 각 사용자는 자신의 진행률만 확인
- ✅ 서로의 작업에 영향 없음

**제한사항:**
- ❌ 같은 사용자는 한 번에 하나의 작업만 실행 가능
- ✅ 다른 사용자는 동시에 여러 작업 실행 가능

**데이터베이스:**
- SQLite는 동시 쓰기 제한이 있지만, 읽기는 병렬 가능
- 많은 사용자가 동시에 사용할 경우 PostgreSQL 권장

## 4. 멀티스레드 사용 조언

### 현재 크롤링 방식

**순차 처리:**
- 제품을 하나씩 순차적으로 크롤링
- 각 제품당 약 1-2초 소요
- 100개 제품 = 약 2-3분

### 멀티스레드 적용 가능성

**✅ 권장:**
- 크롤링 작업은 I/O 바운드 (네트워크 대기)
- 멀티스레드로 병렬 처리 시 속도 향상 가능
- 예상 속도: 2-3배 빠름

**⚠️ 주의사항:**
1. **서버 부하**
   - 너무 많은 스레드 = 서버 과부하
   - 권장: 5-10개 스레드

2. **타겟 사이트 제한**
   - 일부 사이트는 과도한 요청 시 IP 차단
   - Rate limiting 필요

3. **에러 처리**
   - 일부 실패해도 전체 작업 계속 진행
   - 재시도 로직 필요

**구현 예시:**
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def run_crawling_parallel(self, max_workers=5):
    """병렬 크롤링"""
    products = self.load_products()
    self.total_products = len(products)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for product in products:
            future = executor.submit(self.crawl_product, product)
            futures.append(future)
        
        for idx, future in enumerate(as_completed(futures), 1):
            result = future.result()
            self.current_product = idx
            self.progress = int((idx / self.total_products) * 100)
```

**결론:**
- 멀티스레드 적용 권장
- 단, 서버 리소스와 타겟 사이트 정책 고려
- 5-10개 워커로 시작하여 점진적으로 조정

## 5. Render 배포 상세 가이드

### 단계별 배포

#### 1단계: GitHub 저장소 준비

```bash
# .gitignore 확인 (중요 파일 제외)
git init
git add .
git commit -m "Initial commit"

# GitHub에서 새 저장소 생성 후
git remote add origin https://github.com/사용자명/저장소명.git
git push -u origin main
```

#### 2단계: Render에서 서비스 생성

1. **Render 접속**
   - https://render.com
   - GitHub 계정으로 로그인

2. **새 Web Service 생성**
   - Dashboard → "New +" → "Web Service"
   - "Connect GitHub" 클릭
   - 저장소 선택

3. **설정 입력**
   ```
   Name: perfume-crawler (원하는 이름)
   Region: Singapore (한국과 가까움)
   Branch: main
   Root Directory: server ⚠️ 중요!
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

#### 3단계: 환경 변수 설정

Render Dashboard → Environment → Add Environment Variable:

```
SECRET_KEY = your-very-secret-key-here-generate-random-string
DATABASE_URL = sqlite:///./price_crawler.db
ADMIN_PATH = /secure-admin-xyz123  # 관리자 페이지 경로
DATA_DIR = /opt/render/project/src  # JSONL 파일 위치 (선택)
OUTPUT_DIR = /opt/render/project/src  # Excel 출력 위치 (선택)
```

**SECRET_KEY 생성 방법:**
```bash
# Linux/Mac
openssl rand -hex 32

# Windows PowerShell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
```

#### 4단계: 배포 확인

1. "Create Web Service" 클릭
2. 배포 로그 확인 (약 5-10분 소요)
3. 배포 완료 후 제공된 URL 확인
4. `/health` 엔드포인트 테스트

#### 5단계: 클라이언트 설정

`client_new.py` 수정:
```python
SERVER_URL = "https://your-app-name.onrender.com"
```

또는 환경 변수로:
```python
SERVER_URL = os.getenv("SERVER_URL", "https://your-app-name.onrender.com")
```

### 자동 배포 확인

**GitHub 푸시 후:**
1. Render Dashboard에서 "Events" 탭 확인
2. "Deploy" 상태 확인
3. 배포 완료 시 자동으로 새 버전 적용

**자동 배포 비활성화 (필요 시):**
- Settings → "Auto-Deploy" → "No"

## 6. 보안 강화 권장사항

### 관리자 페이지 보안

1. **복잡한 경로 사용**
   ```
   ADMIN_PATH=/admin-secure-xyz-2024-abc123
   ```

2. **추가 인증 레이어 (선택)**
   - IP 화이트리스트
   - 2FA (Two-Factor Authentication)
   - 관리자 전용 토큰

3. **HTTPS 사용**
   - Render는 기본적으로 HTTPS 제공
   - SSL 인증서 자동 관리

### 환경 변수 보안

- ✅ 민감한 정보는 환경 변수로 관리
- ❌ 코드에 하드코딩 금지
- ✅ `.gitignore`에 `.env` 파일 추가

## 7. 문제 해결

### 배포 실패 시

1. **로그 확인**
   - Render Dashboard → Logs
   - 에러 메시지 확인

2. **일반적인 문제**
   - `Root Directory`가 `server`로 설정되었는지 확인
   - `requirements.txt` 경로 확인
   - Python 버전 확인 (3.10 이상 권장)

3. **파일 경로 문제**
   - `DATA_DIR` 환경 변수 확인
   - JSONL 파일이 프로젝트 루트에 있는지 확인

### 슬립 방지

Render 무료 티어는 15분 비활성 시 슬립합니다.

**해결책:**
1. UptimeRobot (무료) 설정
   - https://uptimerobot.com
   - URL: `https://your-app.onrender.com/health`
   - Interval: 5분

2. Render Pro 플랜 (유료)
   - 항상 실행 상태 유지

## 8. 모니터링

### Render Dashboard

- 실시간 로그 확인
- 배포 상태 확인
- 리소스 사용량 모니터링

### 애플리케이션 로그

- 서버 로그: Render Dashboard → Logs
- 에러 추적: 자동으로 로그에 기록

---

## 요약

✅ **URL 설정**: Render가 자동 제공, 환경 변수로 관리자 경로 변경 가능
✅ **자동 배포**: GitHub 푸시 시 자동 배포
✅ **여러 유저**: 동시 사용 가능, 사용자별 독립 작업
✅ **멀티스레드**: 권장, 5-10개 워커로 시작
✅ **보안**: 복잡한 관리자 경로 + 환경 변수 사용

