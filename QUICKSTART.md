# 빠른 시작 가이드

## 1. 서버 실행

### Windows (PowerShell 또는 CMD)
```powershell
# 프로젝트 폴더로 이동
cd C:\Users\minsung\Desktop\perfume

# 서버 폴더로 이동
cd server

# 패키지 설치 (처음 한 번만)
pip install -r requirements.txt

# 서버 실행
python main.py
```

### Linux/Mac
```bash
# 프로젝트 폴더로 이동
cd ~/Desktop/perfume

# 서버 폴더로 이동
cd server

# 패키지 설치 (처음 한 번만)
pip3 install -r requirements.txt

# 서버 실행
python3 main.py
```

서버가 `http://localhost:8000`에서 실행됩니다.

## 2. 클라이언트 실행

**새 터미널 창**을 열어서:

### Windows
```powershell
# 프로젝트 루트 폴더로 이동
cd C:\Users\minsung\Desktop\perfume

# 패키지 설치 (처음 한 번만)
pip install -r client_requirements.txt

# 클라이언트 실행
python client_new.py
```

### Linux/Mac
```bash
# 프로젝트 루트 폴더로 이동
cd ~/Desktop/perfume

# 패키지 설치 (처음 한 번만)
pip3 install -r client_requirements.txt

# 클라이언트 실행
python3 client_new.py
```

클라이언트가 `http://localhost:5000`에서 실행됩니다.

## 3. 첫 사용

### 회원가입 방법

1. **클라이언트 접속**
   - 브라우저에서 `http://localhost:5000` 접속
   - 또는 클라이언트 실행 시 자동으로 브라우저가 열립니다

2. **회원가입**
   - 화면 상단의 "회원가입" 탭 클릭
   - 다음 정보 입력:
     - **아이디**: 로그인에 사용할 ID
     - **비밀번호**: 로그인 비밀번호
   - "회원가입" 버튼 클릭
   - "회원가입이 완료되었습니다." 메시지 확인

### 관리자 페이지 접속 방법

1. **관리자 페이지 접속**
   - 브라우저에서 `http://localhost:8000/admin` 접속
   - 또는 서버 루트(`http://localhost:8000`)에서 "관리자 페이지" 링크 클릭

2. **관리자 로그인**
   - 기본 관리자 계정으로 로그인:
     - **사용자명**: `admin`
     - **비밀번호**: `admin123`
   - ⚠️ **중요**: 프로덕션 환경에서는 반드시 비밀번호를 변경하세요!

3. **사용자 승인**
   - 로그인 후 "승인 대기 사용자" 섹션 확인
   - 승인할 사용자의 "승인" 버튼 클릭
   - 또는 "거절" 버튼으로 거절 가능

### 크롤링 시작

1. **일반 사용자 로그인**
   - 클라이언트(`http://localhost:5000`)에서 승인된 계정으로 로그인

2. **크롤링 실행**
   - 원하는 사이트 선택:
     - **SSG 크롤링**: SSG몰 크롤링
     - **신세계 쇼핑 크롤링**: 신세계TV쇼핑 크롤링
     - **삼성 크롤링**: 삼성 사이트 크롤링
   - "크롤링 시작" 버튼 클릭
   - 진행률 확인 (1초마다 자동 업데이트)
   - 완료 후 "EXCEL 다운로드" 버튼으로 결과 파일 다운로드

## 문제 해결

### 서버가 시작되지 않음
- 포트 8000이 사용 중인지 확인
- `pip install -r server/requirements.txt` 다시 실행

### 클라이언트가 서버에 연결되지 않음
- 서버가 실행 중인지 확인
- `SERVER_URL` 환경 변수 확인

### 관리자 페이지 접근 불가
- `server/static/admin.html` 파일이 존재하는지 확인
- 브라우저 콘솔에서 에러 확인

