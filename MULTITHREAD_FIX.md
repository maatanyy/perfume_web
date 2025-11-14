# 멀티스레드 크롤링 문제 해결

## 발견된 문제점

### 1. Rate Limiting
- 여러 스레드가 동시에 같은 사이트에 요청
- 타겟 사이트에서 과도한 요청으로 인한 차단 가능

### 2. 요청 간격 부족
- 고정된 0.5초 간격으로는 부족
- 동시 요청이 많을수록 문제 발생

### 3. 에러 처리 부족
- 일부 실패해도 계속 진행하지만, 에러 원인 파악 어려움
- 재시도 로직 없음

### 4. 워커 수 과다
- 기본값 7개는 너무 많을 수 있음
- 안정성을 위해 줄이는 것이 좋음

## 적용된 해결책

### 1. 재시도 로직 추가
```python
max_retries = 3
for attempt in range(max_retries):
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        break
    except Exception as e:
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # 지수 백오프
            continue
        else:
            raise
```

### 2. 랜덤 딜레이
- 요청 간격: 1-2초 (랜덤)
- Rate Limiting 방지
- 동시 요청 패턴 예측 어렵게 만듦

### 3. 개선된 HTTP 헤더
- 더 완전한 브라우저 헤더 시뮬레이션
- User-Agent, Accept, Accept-Language 등 추가

### 4. 워커 수 조정
- 기본값: 7개 → **3개**로 변경
- 안정성 우선
- 필요시 환경 변수로 조정 가능

### 5. 에러 로깅 개선
- 각 제품별 에러 상세 로깅
- 최종 통계에 에러 개수 및 성공률 표시

## 권장 설정

### 안정성 우선 (권장)
```bash
CRAWLER_WORKERS=3
```
- 워커 3개
- 요청 간격 1-2초
- 재시도 3회

### 속도 우선
```bash
CRAWLER_WORKERS=5
```
- 워커 5개
- 더 빠르지만 에러 가능성 증가

### 최대 안정성
```bash
CRAWLER_WORKERS=2
```
- 워커 2개
- 가장 안정적이지만 느림

## 문제가 계속되는 경우

### 1. 워커 수 더 줄이기
```python
# crawler.py에서
max_workers = int(os.getenv("CRAWLER_WORKERS", "2"))  # 2개로 변경
```

### 2. 요청 간격 늘리기
```python
# crawl_single_product에서
time.sleep(random.uniform(2.0, 3.0))  # 2-3초로 증가
```

### 3. 순차 처리로 전환
```python
# run_crawling에서
max_workers = 1  # 순차 처리
```

### 4. 타겟 사이트 확인
- 사이트가 크롤링을 차단하는지 확인
- robots.txt 확인
- IP 차단 여부 확인

## 모니터링

크롤링 완료 후 다음 정보가 표시됩니다:
```
✓ 크롤링 완료! 결과: ...
총 처리된 제품: 100/100
⚠️ 에러 발생한 제품: 5개
   성공률: 95.0%
```

또는

```
✓ 크롤링 완료! 결과: ...
총 처리된 제품: 100/100
✅ 모든 제품 크롤링 성공!
```

## 결론

멀티스레드는 속도를 높이지만, 안정성을 위해:
- ✅ 워커 수를 적절히 조정 (3개 권장)
- ✅ 요청 간격을 충분히 두기 (1-2초)
- ✅ 재시도 로직으로 일시적 오류 처리
- ✅ 에러 로깅으로 문제 파악

문제가 계속되면 워커 수를 더 줄이거나 순차 처리로 전환하는 것을 고려하세요.

