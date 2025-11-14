# 가격 비교 크롤러 시스템

서버-클라이언트 아키텍처를 사용하는 가격 비교 크롤링 시스템입니다.

## 주요 기능

- ✅ 사용자 인증 시스템 (회원가입/로그인)
- ✅ 관리자 승인 시스템
- ✅ 다중 사이트 크롤링 (SSG, 신세계 쇼핑, 삼성)
- ✅ 실시간 진행률 모니터링
- ✅ Excel 파일 다운로드
- ✅ 관리자 대시보드

## 시스템 구조

```
perfume/
├── server/                 # FastAPI 백엔드 서버
│   ├── main.py            # 메인 애플리케이션
│   ├── database.py        # 데이터베이스 설정
│   ├── models.py          # DB 모델
│   ├── schemas.py         # Pydantic 스키마
│   ├── auth.py            # 인증 유틸리티
│   ├── routers/           # API 라우터
│   │   ├── auth.py       # 인증 API
│   │   ├── crawler.py    # 크롤링 API
│   │   └── admin.py      # 관리자 API
│   └── static/            # 정적 파일
│       └── admin.html     # 관리자 대시보드
├── client_new.py          # 새로운 클라이언트 (서버 API 호출)
├── crawler.py             # 크롤러 로직
└── templates/             # HTML 템플릿
    └── index_new.html     # 새로운 클라이언트 UI
```

## 빠른 시작

### 1. 서버 실행

```bash
# 서버 디렉토리로 이동
cd server

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python main.py
# 또는
uvicorn main:app --reload
```

서버는 `http://localhost:8000`에서 실행됩니다.

### 2. 클라이언트 실행

```bash
# 의존성 설치
pip install -r client_requirements.txt

# 클라이언트 실행
python client_new.py
```

클라이언트는 `http://localhost:5000`에서 실행됩니다.

### 3. 관리자 페이지 접근

브라우저에서 **`http://localhost:8000/admin`** 접속

**기본 관리자 계정**:
- 사용자명: `admin`
- 비밀번호: `admin123`

⚠️ **프로덕션 환경에서는 반드시 비밀번호를 변경하세요!**

### 4. 회원가입

1. 클라이언트(`http://localhost:5000`) 접속
2. 상단의 "회원가입" 탭 클릭
3. 사용자명, 이메일, 비밀번호 입력
4. 회원가입 완료 후 관리자 승인 대기
5. 관리자가 승인하면 로그인 가능

## API 엔드포인트

### 인증
- `POST /api/auth/register` - 회원가입
- `POST /api/auth/login-json` - 로그인 (JSON)
- `POST /api/auth/login` - 로그인 (OAuth2)

### 크롤링
- `POST /api/crawler/start/{site_name}` - 크롤링 시작
- `GET /api/crawler/progress` - 진행률 조회
- `GET /api/crawler/download` - 파일 다운로드
- `GET /api/crawler/jobs` - 작업 목록

### 관리자
- `GET /api/admin/users` - 사용자 목록
- `GET /api/admin/users/pending` - 승인 대기 사용자
- `POST /api/admin/users/{user_id}/approve` - 사용자 승인/거절
- `GET /api/admin/jobs` - 모든 작업 목록
- `GET /api/admin/stats` - 통계

## 환경 변수

### 서버
- `SECRET_KEY`: JWT 토큰 암호화 키
- `DATABASE_URL`: 데이터베이스 연결 URL (기본: SQLite)

### 클라이언트
- `SERVER_URL`: 서버 API URL (기본: http://localhost:8000)

## 데이터베이스

기본적으로 SQLite를 사용합니다. PostgreSQL로 변경하려면:

```bash
export DATABASE_URL=postgresql://user:password@localhost/price_crawler
```

## 배포

자세한 배포 가이드는 [DEPLOYMENT.md](DEPLOYMENT.md)를 참조하세요.

## 개발

### 서버 개발

```bash
cd server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 클라이언트 개발

```bash
python client_new.py
```

## 라이선스

MIT

