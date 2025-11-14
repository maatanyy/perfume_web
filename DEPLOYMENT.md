# 배포 가이드

## 목차
1. [서버 배포](#서버-배포)
2. [클라이언트 빌드](#클라이언트-빌드)
3. [환경 설정](#환경-설정)

---

## 서버 배포

### 옵션 1: 무료 호스팅 (Render, Railway, Fly.io 등)

#### Render 배포

1. **GitHub 저장소 준비**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Render에서 새 서비스 생성**
   - [Render](https://render.com) 접속
   - "New" → "Web Service" 선택
   - GitHub 저장소 연결
   - 설정:
     - **Build Command**: `pip install -r server/requirements.txt`
     - **Start Command**: `cd server && uvicorn main:app --host 0.0.0.0 --port $PORT`
     - **Environment Variables**:
       ```
       SECRET_KEY=your-secret-key-here
       DATABASE_URL=sqlite:///./price_crawler.db
       ```

3. **환경 변수 설정**
   - Render 대시보드에서 Environment Variables 추가
   - `SECRET_KEY`: 강력한 랜덤 문자열 생성
   - `DATABASE_URL`: PostgreSQL 사용 시 Render의 PostgreSQL 서비스 URL 사용

#### Railway 배포

1. **Railway 계정 생성 및 프로젝트 생성**
   - [Railway](https://railway.app) 접속
   - "New Project" → "Deploy from GitHub repo"

2. **설정**
   - Root Directory: `server`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Environment Variables 추가:
     ```
     SECRET_KEY=your-secret-key
     DATABASE_URL=postgresql://... (Railway가 자동 생성)
     ```

#### Fly.io 배포

1. **Fly CLI 설치**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **배포**
   ```bash
   cd server
   fly launch
   fly secrets set SECRET_KEY=your-secret-key
   fly deploy
   ```

### 옵션 2: 유료 호스팅 (AWS, GCP, Azure)

#### AWS EC2 배포

1. **EC2 인스턴스 생성**
   - Ubuntu 22.04 LTS 선택
   - 보안 그룹에서 포트 8000 열기

2. **서버 설정**
   ```bash
   # SSH 접속
   ssh -i your-key.pem ubuntu@your-ec2-ip

   # 시스템 업데이트
   sudo apt update && sudo apt upgrade -y

   # Python 설치
   sudo apt install python3-pip python3-venv -y

   # 프로젝트 클론
   git clone <your-repo-url>
   cd perfume/server

   # 가상환경 생성 및 활성화
   python3 -m venv venv
   source venv/bin/activate

   # 의존성 설치
   pip install -r requirements.txt

   # 환경 변수 설정
   export SECRET_KEY=your-secret-key
   export DATABASE_URL=sqlite:///./price_crawler.db

   # 서버 실행 (백그라운드)
   nohup uvicorn main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
   ```

3. **Nginx 리버스 프록시 설정 (선택)**
   ```bash
   sudo apt install nginx -y
   sudo nano /etc/nginx/sites-available/default
   ```
   
   Nginx 설정:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```
   
   ```bash
   sudo systemctl restart nginx
   ```

#### Docker 배포

1. **Dockerfile 생성** (`server/Dockerfile`)
   ```dockerfile
   FROM python:3.10-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   EXPOSE 8000

   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **빌드 및 실행**
   ```bash
   cd server
   docker build -t price-crawler-server .
   docker run -d -p 8000:8000 \
     -e SECRET_KEY=your-secret-key \
     -e DATABASE_URL=sqlite:///./price_crawler.db \
     price-crawler-server
   ```

---

## 클라이언트 빌드

### Windows 실행 파일 빌드

1. **의존성 설치**
   ```bash
   pip install -r client_requirements.txt
   pip install pyinstaller
   ```

2. **PyInstaller spec 파일 생성** (`client.spec`)
   ```python
   # -*- mode: python ; coding: utf-8 -*-

   block_cipher = None

   a = Analysis(
       ['client_new.py'],
       pathex=[],
       binaries=[],
       datas=[('templates', 'templates')],
       hiddenimports=[],
       hookspath=[],
       hooksconfig={},
       runtime_hooks=[],
       excludes=[],
       win_no_prefer_redirects=False,
       win_private_assemblies=False,
       cipher=block_cipher,
       noarchive=False,
   )

   pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

   exe = EXE(
       pyz,
       a.scripts,
       a.binaries,
       a.zipfiles,
       a.datas,
       [],
       name='가격비교크롤러',
       debug=False,
       bootloader_ignore_signals=False,
       strip=False,
       upx=True,
       upx_exclude=[],
       runtime_tmpdir=None,
       console=False,
       disable_windowed_traceback=False,
       argv_emulation=False,
       target_arch=None,
       codesign_identity=None,
       entitlements_file=None,
   )
   ```

3. **빌드 실행**
   ```bash
   pyinstaller client.spec
   ```

4. **실행 파일 위치**
   - `dist/가격비교크롤러.exe`

### 환경 변수 설정

클라이언트 실행 파일과 같은 폴더에 `config.ini` 파일 생성:

```ini
[SERVER]
URL=http://your-server-url:8000
```

또는 환경 변수로 설정:
```bash
set SERVER_URL=http://your-server-url:8000
```

---

## 환경 설정

### 서버 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `SECRET_KEY` | JWT 토큰 암호화 키 | `your-secret-key-change-in-production` |
| `DATABASE_URL` | 데이터베이스 연결 URL | `sqlite:///./price_crawler.db` |

### 클라이언트 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `SERVER_URL` | 서버 API URL | `http://localhost:8000` |

### 기본 관리자 계정

서버 시작 시 자동 생성:
- **사용자명**: `admin`
- **비밀번호**: `admin123`

**⚠️ 중요**: 프로덕션 환경에서는 반드시 비밀번호를 변경하세요!

---

## 데이터베이스 마이그레이션

### SQLite → PostgreSQL 마이그레이션

1. **PostgreSQL 데이터베이스 생성**
   ```sql
   CREATE DATABASE price_crawler;
   ```

2. **환경 변수 변경**
   ```
   DATABASE_URL=postgresql://user:password@localhost/price_crawler
   ```

3. **서버 재시작**
   - 서버가 자동으로 새 데이터베이스에 테이블 생성

---

## 트러블슈팅

### 서버가 시작되지 않음

1. 포트가 이미 사용 중인지 확인
2. 환경 변수가 올바르게 설정되었는지 확인
3. 로그 확인: `server.log`

### 클라이언트가 서버에 연결되지 않음

1. `SERVER_URL` 환경 변수 확인
2. 방화벽 설정 확인
3. 서버가 실행 중인지 확인

### 관리자 페이지 접근 불가

1. 관리자 계정이 생성되었는지 확인
2. JWT 토큰이 유효한지 확인
3. 브라우저 콘솔에서 에러 확인

---

## 보안 권장사항

1. **SECRET_KEY**: 강력한 랜덤 문자열 사용
   ```python
   import secrets
   print(secrets.token_urlsafe(32))
   ```

2. **HTTPS 사용**: 프로덕션 환경에서는 반드시 HTTPS 사용

3. **CORS 설정**: 특정 도메인만 허용
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-domain.com"],
       ...
   )
   ```

4. **데이터베이스 백업**: 정기적으로 데이터베이스 백업

5. **로그 모니터링**: 서버 로그를 정기적으로 확인

---

## 추가 리소스

- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [Render 문서](https://render.com/docs)
- [Railway 문서](https://docs.railway.app/)
- [PyInstaller 문서](https://pyinstaller.org/)

