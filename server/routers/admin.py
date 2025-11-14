"""관리자 라우터"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import sys
import os

# 프로젝트 루트 경로 추가
project_root = os.path.join(os.path.dirname(__file__), '../..')
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from server.database import get_db
from server.models import User, CrawlingJob
from server.schemas import UserResponse, UserApprovalRequest, CrawlingJobResponse
from server.auth import get_current_admin_user

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    approved_only: bool = False,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """사용자 목록 조회"""
    query = db.query(User)
    
    if approved_only:
        query = query.filter(User.is_approved == True)
    
    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/users/pending", response_model=List[UserResponse])
def get_pending_users(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """승인 대기 사용자 목록 (비활성 사용자)"""
    users = db.query(User).filter(User.is_active == False).all()
    return users


@router.post("/users/{user_id}/approve")
def approve_user(
    user_id: int,
    approval_data: UserApprovalRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """사용자 활성화/비활성화"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = approval_data.is_approved
    db.commit()
    db.refresh(user)
    
    return {"message": f"User {'activated' if user.is_active else 'deactivated'}", "user": user}


@router.get("/jobs", response_model=List[CrawlingJobResponse])
def get_all_jobs(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """모든 크롤링 작업 조회"""
    jobs = db.query(CrawlingJob).order_by(CrawlingJob.created_at.desc()).offset(skip).limit(limit).all()
    return jobs


@router.get("/stats")
def get_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """관리자 통계"""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    pending_users = db.query(User).filter(User.is_active == False).count()
    total_jobs = db.query(CrawlingJob).count()
    completed_jobs = db.query(CrawlingJob).filter(CrawlingJob.status == "completed").count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "pending_users": pending_users,
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs
    }

