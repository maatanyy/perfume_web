# 🚀 시작 가이드

## 1. 터미널에서 시작하기

### Windows (PowerShell 또는 CMD)

#### 첫 번째 터미널 창 (서버 실행)
```powershell
# 1. 프로젝트 폴더로 이동
cd C:\Users\minsung\Desktop\perfume

# 2. 서버 폴더로 이동
cd server

# 3. 필요한 패키지 설치 (처음 한 번만)
pip install -r requirements.txt

# 4. 서버 실행
python main.py
```

서버가 `http://localhost:8000`에서 실행됩니다.

#### 두 번째 터미널 창 (클라이언트 실행)
```powershell
# 1. 프로젝트 루트 폴더로 이동
cd C:\Users\minsung\Desktop\perfume

# 2. 필요한 패키지 설치 (처음 한 번만)
pip install -r client_requirements.txt

# 3. 클라이언트 실행
python client_new.py
```

클라이언트가 `http://localhost:5000`에서 실행됩니다.

### Linux/Mac

#### 첫 번째 터미널 창 (서버 실행)
```bash
# 1. 프로젝트 폴더로 이동
cd ~/Desktop/perfume

# 2. 서버 폴더로 이동
cd server

# 3. 필요한 패키지 설치 (처음 한 번만)
pip3 install -r requirements.txt

# 4. 서버 실행
python3 main.py
```

#### 두 번째 터미널 창 (클라이언트 실행)
```bash
# 1. 프로젝트 루트 폴더로 이동
cd ~/Desktop/perfume

# 2. 필요한 패키지 설치 (처음 한 번만)
pip3 install -r client_requirements.txt

# 3. 클라이언트 실행
python3 client_new.py
```

## 2. 접속하기

1. **클라이언트**: 브라우저에서 `http://localhost:5000` 접속
2. **서버 API 문서**: `http://localhost:8000/docs`
3. **관리자 페이지**: `http://localhost:8000/admin`

## 3. 첫 사용

### 회원가입
1. 클라이언트(`http://localhost:5000`) 접속
2. "회원가입" 탭 클릭
3. 아이디, 비밀번호 입력 후 회원가입

### 관리자 승인
1. 관리자 페이지(`http://localhost:8000/admin`) 접속
2. 로그인:
   - 사용자명: `admin`
   - 비밀번호: `admin123`
3. "승인 대기 사용자"에서 사용자 활성화

### 크롤링 시작
1. 클라이언트에서 로그인
2. 원하는 사이트 선택 (SSG, 신세계 쇼핑, 삼성)
3. "크롤링 시작" 버튼 클릭
4. 완료 후 Excel 다운로드

## 문제 해결

### 포트가 이미 사용 중일 때
```powershell
# Windows에서 포트 사용 중인 프로세스 확인
netstat -ano | findstr :8000
netstat -ano | findstr :5000

# 프로세스 종료 (PID는 위 명령어 결과에서 확인)
taskkill /PID <PID번호> /F
```

### 패키지 설치 오류
```powershell
# pip 업그레이드
python -m pip install --upgrade pip

# 가상환경 사용 권장
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

