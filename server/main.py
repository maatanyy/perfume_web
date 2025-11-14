"""FastAPI 메인 애플리케이션"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from server.database import init_db, get_db
from server.models import User
from server.auth import get_password_hash
from server.routers import auth, crawler, admin

# 정적 파일 디렉토리 생성
os.makedirs("server/static", exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작 시 실행
    # 데이터베이스 초기화
    init_db()
    
    # 기본 관리자 계정 생성 (없는 경우)
    db = next(get_db())
    admin_user = db.query(User).filter(User.username == "yunkung").first()
    if not admin_user:
        admin_user = User(
            username="yunkung",
            hashed_password=get_password_hash("yunkung98"),  # 기본 비밀번호 변경 필수!
            is_admin=True,
            is_approver=True,
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        print("기본 관리자 계정이 생성되었습니다. (username: admin, password: admin123)")
    db.close()
    
    yield  # 애플리케이션이 실행 중
    
    # 종료 시 실행 (필요한 경우)
    pass


app = FastAPI(
    title="가격 비교 크롤러 API",
    description="가격 비교 크롤링 서비스 백엔드",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router)
app.include_router(crawler.router)
app.include_router(admin.router)

# 정적 파일 서빙 (관리자 페이지용)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 관리자 페이지 경로 (환경 변수로 설정 가능, 기본값: /admin)
ADMIN_PATH = os.getenv("ADMIN_PATH", "/ykykyk")

# 관리자 페이지 라우트
@app.get(ADMIN_PATH, response_class=HTMLResponse)
async def admin_page():
    """관리자 페이지"""
    admin_html_path = os.path.join(os.path.dirname(__file__), "static", "admin.html")
    if os.path.exists(admin_html_path):
        with open(admin_html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>관리자 페이지를 찾을 수 없습니다.</h1>"


@app.get("/", response_class=HTMLResponse)
async def root():
    """루트 경로"""
    return f"""
    <html>
        <head>
            <title>가격 비교 크롤러 API</title>
        </head>
        <body>
            <h1>가격 비교 크롤러 API</h1>
            <p>API 문서: <a href="/docs">/docs</a></p>
            <p>관리자 페이지: <a href="{ADMIN_PATH}">{ADMIN_PATH}</a></p>
        </body>
    </html>
    """


@app.get("/health")
def health_check():
    """헬스 체크"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

