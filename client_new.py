"""새로운 클라이언트 - 서버 API 호출 방식"""
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_cors import CORS
import requests
import os
import sys
import webbrowser
import time
import threading
import logging
from datetime import datetime

# 로그 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# 서버 URL (환경변수 또는 기본값)
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000")

# PyInstaller 리소스 경로 처리
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Flask 앱 생성
app = Flask(__name__, template_folder=resource_path('templates'))
app.secret_key = os.getenv("SECRET_KEY", "client-secret-key-change-in-production")
CORS(app)

# 전역 변수
access_token = None
check_interval = None


def get_auth_headers():
    """인증 헤더 반환"""
    global access_token
    if access_token:
        return {"Authorization": f"Bearer {access_token}"}
    return {}


@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index_new.html')


@app.route('/api/login', methods=['POST'])
def login():
    """로그인"""
    global access_token
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    try:
        response = requests.post(
            f"{SERVER_URL}/api/auth/login-json",
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data['access_token']
            session['access_token'] = access_token
            return jsonify({'status': 'success', 'message': '로그인 성공'})
        else:
            error_data = response.json()
            return jsonify({'status': 'error', 'message': error_data.get('detail', '로그인 실패')})
    except Exception as e:
        logging.error(f"로그인 에러: {e}")
        return jsonify({'status': 'error', 'message': f'서버 연결 실패: {str(e)}'})


@app.route('/api/register', methods=['POST'])
def register():
    """회원가입"""
    data = request.json
    
    try:
        response = requests.post(
            f"{SERVER_URL}/api/auth/register",
            json=data
        )
        
        if response.status_code == 201:
            return jsonify({'status': 'success', 'message': '회원가입 성공. 관리자 승인을 기다려주세요.'})
        else:
            error_data = response.json()
            return jsonify({'status': 'error', 'message': error_data.get('detail', '회원가입 실패')})
    except Exception as e:
        logging.error(f"회원가입 에러: {e}")
        return jsonify({'status': 'error', 'message': f'서버 연결 실패: {str(e)}'})


@app.route('/api/start/<site>', methods=['POST'])
def start_crawling(site):
    """크롤링 시작"""
    global access_token
    
    if not access_token:
        return jsonify({'status': 'error', 'message': '로그인이 필요합니다.'})
    
    try:
        response = requests.post(
            f"{SERVER_URL}/api/crawler/start/{site}",
            headers=get_auth_headers()
        )
        
        if response.status_code == 200:
            return jsonify({'status': 'success', 'message': f'{site.upper()} 크롤링이 시작되었습니다.'})
        else:
            error_data = response.json()
            return jsonify({'status': 'error', 'message': error_data.get('detail', '크롤링 시작 실패')})
    except Exception as e:
        logging.error(f"크롤링 시작 에러: {e}")
        return jsonify({'status': 'error', 'message': f'서버 연결 실패: {str(e)}'})


@app.route('/api/progress', methods=['GET'])
def get_progress():
    """진행률 조회"""
    global access_token
    
    if not access_token:
        return jsonify({
            'status': 'idle',
            'progress': 0,
            'current': 0,
            'total': 0,
            'is_crawling': False,
            'elapsed_time': 0
        })
    
    try:
        response = requests.get(
            f"{SERVER_URL}/api/crawler/progress",
            headers=get_auth_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'status': data['status'],
                'progress': data['progress'],
                'current': data['current'],
                'total': data['total'],
                'is_crawling': data['is_crawling'],
                'elapsed_time': data['elapsed_time']
            })
        else:
            return jsonify({
                'status': 'idle',
                'progress': 0,
                'current': 0,
                'total': 0,
                'is_crawling': False,
                'elapsed_time': 0
            })
    except Exception as e:
        logging.error(f"진행률 조회 에러: {e}")
        return jsonify({
            'status': 'idle',
            'progress': 0,
            'current': 0,
            'total': 0,
            'is_crawling': False,
            'elapsed_time': 0
        })


@app.route('/api/download', methods=['GET'])
def download_file():
    """파일 다운로드"""
    global access_token
    
    if not access_token:
        return jsonify({'status': 'error', 'message': '로그인이 필요합니다.'})
    
    try:
        response = requests.get(
            f"{SERVER_URL}/api/crawler/download",
            headers=get_auth_headers(),
            stream=True
        )
        
        if response.status_code == 200:
            from flask import Response
            return Response(
                response.content,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={
                    'Content-Disposition': f'attachment; filename={response.headers.get("filename", "result.xlsx")}'
                }
            )
        else:
            error_data = response.json()
            return jsonify({'status': 'error', 'message': error_data.get('detail', '다운로드 실패')})
    except Exception as e:
        logging.error(f"다운로드 에러: {e}")
        return jsonify({'status': 'error', 'message': f'서버 연결 실패: {str(e)}'})


@app.route('/api/cancel', methods=['POST'])
def cancel_crawling():
    """진행 중인 크롤링 취소"""
    global access_token
    
    if not access_token:
        return jsonify({'status': 'error', 'message': '로그인이 필요합니다.'})
    
    try:
        response = requests.post(
            f"{SERVER_URL}/api/crawler/cancel",
            headers=get_auth_headers()
        )
        if response.status_code == 200:
            return jsonify({'status': 'success', 'message': '작업 취소를 요청했습니다.'})
        else:
            error_data = response.json()
            return jsonify({'status': 'error', 'message': error_data.get('detail', '작업 취소 실패')})
    except Exception as e:
        logging.error(f"작업 취소 에러: {e}")
        return jsonify({'status': 'error', 'message': f'서버 연결 실패: {str(e)}'})


@app.route('/api/logout', methods=['POST'])
def logout():
    """로그아웃"""
    global access_token
    access_token = None
    session.pop('access_token', None)
    return jsonify({'status': 'success', 'message': '로그아웃되었습니다.'})


if __name__ == '__main__':
    # templates 폴더 확인
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("="*50)
    print("가격 비교 크롤러 클라이언트 시작")
    print(f"서버 URL: {SERVER_URL}")
    print("브라우저에서 http://localhost:5000 접속")
    print("="*50)
    
    # 브라우저 자동 열기
    def open_browser():
        time.sleep(1)
        webbrowser.open('http://localhost:5000')
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    app.run(debug=False, host='0.0.0.0', port=5000)

