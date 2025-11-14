from flask import Flask, render_template, jsonify, send_file, request
from flask_cors import CORS
import threading
import os
from crawler import PriceCompareCrawler
import sys
import webbrowser
import time
import logging
from datetime import datetime
import tempfile

# 로그 파일 설정
temp_dir = tempfile.gettempdir()
log_filename = os.path.join(temp_dir, f"crawler_log_{datetime.now():%Y%m%d_%H%M%S}.txt")
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# 콘솔 출력도 로그에 저장
import sys
class LoggerWriter:
    def __init__(self, level):
        self.level = level



# PyInstaller 리소스 경로 처리 함수
def resource_path(relative_path):
    """PyInstaller로 만든 실행파일에서 리소스 경로 가져오기"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Flask 앱 생성 (templates 경로 설정)
app = Flask(__name__, 
            template_folder=resource_path('templates'))
CORS(app)

# 전역 크롤러 객체
crawler = None
crawling_thread = None
is_crawling = False
start_time = None  # 크롤링 시작 시간 추가


@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/api/start/<site>', methods=['POST'])
def start_crawling(site="ssg"):
    """크롤링 시작 - 싸이트별"""
    global crawler, crawling_thread, is_crawling, start_time
    
    logging.info(f"==={site} 크롤링 시작 요청 ===")

    if is_crawling:
        return jsonify({'status': 'error', 'message': '이미 크롤링이 진행 중입니다.'})
    
    try:
        # site 별 config 경로로
        config_file = resource_path(f'{site}_input_list.jsonl')
        logging.info(f"설정 파일 경로: {config_file}")
        logging.info(f"파일 존재 여부: {os.path.exists(config_file)}")

        if not os.path.exists(config_file):
            return jsonify({'status': 'error', 'message': f'{site}_input.jsonl 파일이 존재하지 않습니다다.'})

        crawler = PriceCompareCrawler(config_file=config_file, site_name =site)
        is_crawling = True
        start_time = time.time()  # 시작 시간 기록
        
        # 백그라운드에서 크롤링 실행
        def run_crawler():
            global is_crawling
            try:
                logging.info(f"{site} 크롤링 시작")
                crawler.run_crawling()
                logging.info(f"{site} Excel 변환 시작")
                crawler.export_to_excel_format()
                logging.info(f"{site} 크롤링 완료")
            except Exception as e:
                print(f"크롤링 에러: {e}")
            finally:
                is_crawling = False
        
        crawling_thread = threading.Thread(target=run_crawler)
        crawling_thread.start()
        
        return jsonify({'status': 'success', 'message': f'{site.upper()} 크롤링이 시작되었습니다.'})
    
    except Exception as e:
        logging.error(f"크롤러 생성 실패: {e}", exc_info=True)
        is_crawling = False
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/progress', methods=['GET'])
def get_progress():
    """현재 진행율 조회"""
    global crawler, is_crawling, start_time
    
    if crawler is None:
        return jsonify({
            'status': 'idle',
            'progress': 0,
            'current': 0,
            'total': 0,
            'is_crawling': False,
            'elapsed_time': 0
        })
    
    progress_data = crawler.get_progress()

    # 경과 시간 계산
    elapsed_time = 0
    if start_time is not None:
        elapsed_time = int(time.time() - start_time)
    
    return jsonify({
        'status': 'running' if is_crawling else 'completed',
        'progress': progress_data['percentage'],
        'current': progress_data['current'],
        'total': progress_data['total'],
        'is_crawling': is_crawling, 
        'elapsed_time': elapsed_time  # 경과 시간 추가 (초 단위)
    })

@app.route('/api/download', methods=['GET'])
def download_csv():
    """Excel 파일 다운로드"""
    if crawler is None:
        return jsonify({'status': 'error', 'message': '데이터 추출을 먼저 실행하세요.'})
    
    excel_file = crawler.csv_file  # 실제로는 .xlsx
    
    if not os.path.exists(excel_file):
        return jsonify({'status': 'error', 'message': 'Excel 파일이 없습니다.'})
    
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=os.path.basename(excel_file)
    )

@app.route('/api/reset', methods=['POST'])
def reset():
    """크롤러 상태 초기화"""
    global crawler, is_crawling
    
    if is_crawling:
        return jsonify({'status': 'error', 'message': '데이터 추출 진행 중입니다. 완료 후 다시 시도하세요.'})
    
    crawler = None
    return jsonify({'status': 'success', 'message': '초기화되었습니다.'})

@app.route('/api/shutdown', methods=['POST'])
def shutdown():
    """서버 종료"""
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        os._exit(0)  # 강제 종료
    func()
    return jsonify({'status': 'success', 'message': '서버가 종료됩니다.'})


if __name__ == '__main__':
    # templates 폴더가 없으면 생성
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("="*50)
    print("가격 비교 크롤러 웹 클라이언트 시작")
    print("브라우저에서 http://localhost:5000 접속")
    print("="*50)
    
    # 브라우저 자동 열기 (1초 후)
    def open_browser():
        time.sleep(1)
        webbrowser.open('http://localhost:5000')
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    app.run(debug=False, host='127.0.0.1', port=5000)