import json
import jsonlines
from datetime import datetime
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import time
import csv
import re
import sys
import os

def get_executable_dir():
    """실행 파일이 있는 디렉토리 경로 반환"""
    if getattr(sys, 'frozen', False):
        # PyInstaller로 실행된 경우
        return os.path.dirname(sys.executable)
    else:
        # 일반 Python으로 실행된 경우
        return os.path.dirname(os.path.abspath(__file__))

class PriceCompareCrawler:
    def __init__(self, config_file: str = 'perfume_list.jsonl', results_file: str = None):
        self.config_file = config_file
        if results_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")    
            exe_dir = get_executable_dir()
            self.results_file = os.path.join(exe_dir, f"신세계_가격조사_{timestamp}.jsonl")
            self.csv_file = os.path.join(exe_dir, f"신세계_가격조사_{timestamp}.csv")
        else:
            self.results_file = results_file
            self.csv_file = results_file.replace('.jsonl', '.csv')  
        self.progress = 0  # 진행율 저장
        self.total_products = 0  # 전체 제품 수
        self.current_product = 0  # 현재 처리 중인 제품 번호
        
    def load_products(self) -> List[Dict]:
        """JSONL 파일에서 제품 정보 로드"""
        products = []
        try:
            with jsonlines.open(self.config_file) as reader:
                for obj in reader:
                    products.append(obj)
        except FileNotFoundError:
            print(f"{self.config_file} 파일이 없습니다.")
        return products
    
    def get_progress(self) -> Dict:
        """현재 진행율 반환"""
        return {
            'current': self.current_product,
            'total': self.total_products,
            'percentage': self.progress
        }
    
    def crawl_price(self, url: str) -> Dict:
        """SSG에서 가격 정보 크롤링"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # SSG 가격 정보 추출 
            price_elem = soup.select_one('.cdtl_new_price.notranslate .ssg_price')
            if price_elem:
                product_price_text = price_elem.text.replace(',', '').replace('원', '').replace(' ', '').strip()
                try:
                    product_price = int(product_price_text)
                except ValueError:
                    product_price = None
            else:
                product_price = None

            # 배송비 추출
            delivery_elem = soup.select_one('.cdtl_dl.cdtl_delivery_fee')

            if delivery_elem:
                # 첫 번째 li 요소만 선택
                first_li = delivery_elem.select_one('li')
    
                if first_li:
                    delivery_price_elem = first_li.select_one('em.ssg_price')
                    if delivery_price_elem:
                        numbers = re.sub(r'[^\d]', '', delivery_price_elem.text)
                        delivery_price = int(numbers) if numbers else 0
                        delivery_status = "유료"
                    else:
                        delivery_price = 0
                        delivery_status = "무료"
                else:
                    delivery_price = 0
                    delivery_status = "무료"
            else:
                delivery_price = 0
                delivery_status = "정보 없음"

            # 총 가격 계산
            if product_price is not None:
                total_price = product_price + delivery_price
            else:
                total_price = None
            
            return {
                '상품 가격': product_price,
                '배송비': delivery_price,
                '배송비 여부': delivery_status,
                '최종 가격': total_price,
                '추출 날짜': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                '상품 가격': None,
                '배송비': None,
                '배송비 여부': None,
                '최종 가격': None,
                '에러 발생': str(e),
                '추출 날짜': datetime.now().isoformat()
            }
    
    def run_crawling(self):
        """전체 제품에 대해 크롤링 실행"""
        products = self.load_products()
        self.total_products = len(products)
        self.current_product = 0
        self.progress = 0
        
        with jsonlines.open(self.results_file, mode='w') as writer:
            for idx, product in enumerate(products, 1):
                self.current_product = idx
                self.progress = int((idx / self.total_products) * 100)
                
                print(f"\n[{self.progress}%] 크롤링 중 ({idx}/{self.total_products}): {product.get('product_name', 'Unknown')}")
                
                result = {
                    'product_id': product['product_id'],
                    'product_name': product['product_name'],
                    'timestamp': datetime.now().isoformat(),
                    'prices': []
                }
                
                # Waffle (우리 회사) 크롤링
                if 'waffle' in product:
                    print("  - 와플커머스 크롤링 중...")
                    waffle_data = self.crawl_price(product['waffle']['url'])
                    result['prices'].append({
                        'seller': 'waffle',
                        **waffle_data
                    })
                    time.sleep(1)
                
                # 경쟁사 크롤링 (개선된 구조)
                if 'competitors' in product:
                    for competitor in product['competitors']:
                        print(f"  - {competitor['name']} 크롤링 중...")
                        comp_data = self.crawl_price(competitor['url'])
                        result['prices'].append({
                            'seller': competitor['name'],
                            **comp_data
                        })
                        time.sleep(1)
                
                writer.write(result)
                print(f"  ✓ 완료: {product['product_name']}")
        
        self.progress = 100
        print(f"\n크롤링 완료! 결과: {self.results_file}")
    
    def analyze_prices(self):
        """가격 분석 및 비교"""
        results = []
        with jsonlines.open(self.results_file) as reader:
            for obj in reader:
                results.append(obj)
        
        for result in results:
            print(f"\n{'='*50}")
            print(f"제품: {result['product_name']}")
            print(f"{'='*50}")
            
            waffle_price = None
            competitor_prices = []
            
            for p in result['prices']:
                if p['seller'] == 'waffle':
                    waffle_price = p
                    print(f"\n[Waffle - 우리회사]")
                    print(f"  상품 가격: {p['상품 가격']}")
                    print(f"  배송비: {p['배송비']}")
                    print(f"  배송비 여부: {p['배송비 여부']}")
                    print(f"  최종 가격: {p['최종 가격']}")
                else:
                    competitor_prices.append(p)
                    print(f"\n[경쟁사 - {p['seller']}]")
                    print(f"  상품 가격: {p['상품 가격']}")
                    print(f"  배송비: {p['배송비']}")
                    print(f"  배송비 여부: {p['배송비 여부']}")
                    print(f"  최종 가격: {p['최종 가격']}")
            
            # 간단한 가격 비교
            if waffle_price and competitor_prices:
                print(f"\n📊 가격 비교 분석")
                print(f"   우리 회사와 경쟁사 {len(competitor_prices)}곳의 가격을 비교했습니다.")

    def export_to_excel_format_csv(self, csv_file: str):
        """제품별 가격 비교표 형식의 CSV 생성 (엑셀 스타일)"""
        try:
            results = []
            with jsonlines.open(self.results_file) as reader:
                for obj in reader:
                    results.append(obj)
            
            if not results:
                print("변환할 데이터가 없습니다.")
                return
            
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                for result in results:
                    # 제품 정보 헤더
                    writer.writerow([f"제품명: {result['product_name']}", f"제품ID: {result['product_id']}"])
                    writer.writerow([f"추출 시간: {result['timestamp']}"])
                    writer.writerow([])  # 빈 줄
                    
                    # 가격 비교 테이블 헤더
                    writer.writerow(['판매처', '상품가격', '배송비', '배송비여부', '최종가격'])
                    
                    # 데이터 행
                    for price_info in result['prices']:
                        seller_name = 'Waffle (우리회사)' if price_info['seller'] == 'waffle' else f"경쟁사 ({price_info['seller']})"
                        writer.writerow([
                            seller_name,
                            price_info.get('상품 가격', 'N/A'),
                            price_info.get('배송비', 'N/A'),
                            price_info.get('배송비 여부', 'N/A'),
                            price_info.get('최종 가격', 'N/A')
                        ])
                    
                    # 제품 간 구분선
                    writer.writerow([])
                    writer.writerow(['='*50])
                    writer.writerow([])
            
            print(f"✓ 가격 비교표 CSV 생성 완료: {csv_file}")
            return csv_file
            
        except FileNotFoundError:
            print(f"{self.results_file} 파일이 없습니다. 먼저 크롤링을 실행하세요.")
            return None
        except Exception as e:
            print(f"CSV 변환 중 에러 발생: {e}")
            return None
    
    def get_latest_prices(self, product_id: int) -> Dict:
        """특정 제품의 최신 가격 정보 조회"""
        try:
            with jsonlines.open(self.results_file) as reader:
                for obj in reader:
                    if obj['product_id'] == product_id:
                        return obj
        except FileNotFoundError:
            print(f"{self.results_file} 파일이 없습니다.")
        return None


# 사용 예시
if __name__ == "__main__":
    # 크롤러 실행
    crawler = PriceCompareCrawler()
    
    final_file = f"신세계_가격조사_{datetime.now():%Y%m%d_%H%M%S}"
    crawler.results_file = final_file +".jsonl"

    print("=== 가격 크롤링 시작 ===\n")
    crawler.run_crawling()
    
    print("\n=== 가격 분석 ===")
    crawler.analyze_prices()

    # csv로 변환
    print("\n=== CSV 변환 ===")
    crawler.export_to_excel_format_csv(final_file+".csv")

    # 특정 제품 조회
    print("\n=== 특정 제품 조회 ===")
    latest = crawler.get_latest_prices(product_id=1)
    if latest:
        print(f"제품: {latest['product_name']}")
        print(f"마지막 업데이트: {latest['timestamp']}")