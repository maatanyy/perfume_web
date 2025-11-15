"""크롤링 라우터"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
import os
import time
import threading
from datetime import datetime
import sys
import logging

# 프로젝트 루트 경로 추가
project_root = os.path.join(os.path.dirname(__file__), '../..')
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from server.database import get_db
from server.models import CrawlingJob, User
from server.schemas import CrawlingJobCreate, CrawlingJobResponse, CrawlingProgress
from server.auth import get_current_active_user
from server.config import get_data_dir
from crawler import PriceCompareCrawler

router = APIRouter(prefix="/api/crawler", tags=["crawler"])

# 전역 크롤러 상태 관리
crawler_instances = {}  # {user_id: {job_id: crawler_instance}}
logger = logging.getLogger(__name__)


def run_crawler_task(
    db: Session,
    job_id: int,
    user_id: int,
    site_name: str,
    config_file_path: str
):
    """백그라운드 크롤링 작업"""
    try:
        job = db.query(CrawlingJob).filter(CrawlingJob.id == job_id).first()
        if not job:
            return
        
        job.status = "running"
        job.started_at = datetime.utcnow()
        db.commit()
        
        # 크롤러 인스턴스 생성
        crawler = PriceCompareCrawler(
            config_file=config_file_path,
            site_name=site_name
        )
        
        # 전역 상태에 저장
        if user_id not in crawler_instances:
            crawler_instances[user_id] = {}
        crawler_instances[user_id][job_id] = crawler
        
        # 크롤링 실행
        cancelled = crawler.run_crawling()
        
        if cancelled:
            job.status = "cancelled"
            job.progress = crawler.progress
            job.current_product = crawler.current_product
            job.result_file_path = None
            job.error_message = "사용자 요청으로 취소되었습니다."
            job.completed_at = datetime.utcnow()
            db.commit()
            return
        
        # Excel 변환
        excel_file = crawler.export_to_excel_format()
        
        job.status = "completed"
        job.progress = 100
        job.current_product = job.total_products
        job.result_file_path = excel_file
        job.completed_at = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        job = db.query(CrawlingJob).filter(CrawlingJob.id == job_id).first()
        if job:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()
    finally:
        # 크롤러 인스턴스 정리
        if user_id in crawler_instances and job_id in crawler_instances[user_id]:
            del crawler_instances[user_id][job_id]


@router.post("/start/{site_name}", response_model=CrawlingJobResponse)
def start_crawling(
    site_name: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """크롤링 시작"""
    # 이미 실행 중인 작업이 있는지 확인
    running_job = db.query(CrawlingJob).filter(
        CrawlingJob.user_id == current_user.id,
        CrawlingJob.status.in_(["running", "cancelling"])
    ).first()
    
    if running_job:
        raise HTTPException(
            status_code=400,
            detail="이미 크롤링이 진행 중입니다."
        )
    
    # 설정 파일 경로 확인 (환경 변수 또는 상대 경로)
    data_dir = get_data_dir()
    logger.info("Preparing to start %s crawl. DATA_DIR=%s", site_name, data_dir)

    config_file = os.path.join(data_dir, f"{site_name}_input_list.jsonl")
    base_dir = os.path.dirname(__file__)
    search_paths = [
        config_file,
        os.path.join(os.getcwd(), f"{site_name}_input_list.jsonl"),
        os.path.join(base_dir, "data", f"{site_name}_input_list.jsonl"),
        os.path.join(os.path.dirname(base_dir), "data", f"{site_name}_input_list.jsonl"),
    ]
    logger.info("Search paths for %s: %s", site_name, search_paths)

    found_file = next((os.path.abspath(p) for p in search_paths if os.path.exists(p)), None)

    if not found_file:
        logger.error("Failed to locate %s file. Checked: %s", site_name, search_paths)
        raise HTTPException(
            status_code=404,
            detail=(
                f"{site_name}_input_list.jsonl 파일을 찾을 수 없습니다. "
                f"확인한 경로: {', '.join(search_paths)}. "
                f"DATA_DIR 환경 변수 또는 data 폴더 위치를 다시 확인해주세요."
            ),
        )

    config_file = found_file
    
    # 새 작업 생성
    new_job = CrawlingJob(
        user_id=current_user.id,
        site_name=site_name,
        status="pending"
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    # 제품 수 확인 (크롤러로)
    crawler_temp = PriceCompareCrawler(config_file=config_file, site_name=site_name)
    products = crawler_temp.load_products()
    new_job.total_products = len(products)
    db.commit()
    
    # 백그라운드 작업 시작 (정규화된 경로 전달)
    config_file_path = os.path.abspath(config_file) if not os.path.isabs(config_file) else config_file
    background_tasks.add_task(
        run_crawler_task,
        db=db,
        job_id=new_job.id,
        user_id=current_user.id,
        site_name=site_name,
        config_file_path=config_file_path
    )
    
    return new_job


@router.get("/progress", response_model=CrawlingProgress)
def get_progress(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """크롤링 진행률 조회"""
    # 가장 최근 작업 조회
    job = db.query(CrawlingJob).filter(
        CrawlingJob.user_id == current_user.id
    ).order_by(CrawlingJob.created_at.desc()).first()
    
    if not job:
        return CrawlingProgress(
            status="idle",
            progress=0,
            current=0,
            total=0,
            is_crawling=False,
            elapsed_time=0
        )
    
    # 크롤러 인스턴스에서 진행률 가져오기 (실행 중일 때만)
    if (
        job.status in ("running", "cancelling")
        and current_user.id in crawler_instances
        and job.id in crawler_instances[current_user.id]
    ):
        crawler = crawler_instances[current_user.id][job.id]
        progress_data = crawler.get_progress()
        job.progress = progress_data["percentage"]
        job.current_product = progress_data["current"]
        db.commit()
    
    # 경과 시간 계산 (timezone-aware 안전 처리)
    def _to_naive(dt: Optional[datetime]) -> Optional[datetime]:
        if dt is None:
            return None
        return dt.astimezone(tz=None).replace(tzinfo=None) if dt.tzinfo else dt

    start = _to_naive(job.started_at)
    end = _to_naive(job.completed_at)

    if start:
        reference_end = end or datetime.utcnow()
        elapsed_time = max(0, int((reference_end - start).total_seconds()))
    else:
        elapsed_time = 0
    
    return CrawlingProgress(
        status=job.status,
        progress=job.progress,
        current=job.current_product,
        total=job.total_products,
        is_crawling=(job.status in ("running", "cancelling")),
        elapsed_time=elapsed_time
    )


@router.get("/download")
def download_file(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Excel 파일 다운로드"""
    # 가장 최근 완료된 작업 조회
    job = db.query(CrawlingJob).filter(
        CrawlingJob.user_id == current_user.id,
        CrawlingJob.status == "completed"
    ).order_by(CrawlingJob.completed_at.desc()).first()
    
    if not job or not job.result_file_path:
        raise HTTPException(
            status_code=404,
            detail="다운로드할 파일이 없습니다."
        )
    
    if not os.path.exists(job.result_file_path):
        raise HTTPException(
            status_code=404,
            detail="파일이 존재하지 않습니다."
        )
    
    return FileResponse(
        job.result_file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=os.path.basename(job.result_file_path)
    )


@router.get("/jobs", response_model=list[CrawlingJobResponse])
def get_jobs(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 10
):
    """사용자의 크롤링 작업 목록 조회"""
    jobs = db.query(CrawlingJob).filter(
        CrawlingJob.user_id == current_user.id
    ).order_by(CrawlingJob.created_at.desc()).limit(limit).all()
    
    return jobs


@router.post("/cancel", response_model=CrawlingJobResponse)
def cancel_job(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """진행 중인 크롤링 작업 취소"""
    job = db.query(CrawlingJob).filter(
        CrawlingJob.user_id == current_user.id,
        CrawlingJob.status.in_(["pending", "running", "cancelling"])
    ).order_by(CrawlingJob.created_at.desc()).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="취소할 진행 중인 작업이 없습니다.")
    
    user_jobs = crawler_instances.get(current_user.id, {})
    crawler = user_jobs.get(job.id)
    
    if crawler:
        crawler.request_cancel()
        job.status = "cancelling"
    else:
        # 아직 실행되지 않았거나 이미 종료된 경우
        job.status = "cancelled"
        job.progress = job.progress or 0
        job.current_product = job.current_product or 0
        job.completed_at = datetime.utcnow()
        job.error_message = "사용자 요청으로 취소되었습니다."
    
    db.commit()
    db.refresh(job)
    
    return job

