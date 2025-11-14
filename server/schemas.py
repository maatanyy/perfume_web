"""Pydantic 스키마"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# User 스키마
class UserBase(BaseModel):
    username: str


class UserCreate(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    is_approver: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    username: str
    is_active: bool
    is_admin: bool
    is_approver: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Auth 스키마
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


# CrawlingJob 스키마
class CrawlingJobBase(BaseModel):
    site_name: str


class CrawlingJobCreate(CrawlingJobBase):
    pass


class CrawlingJobResponse(CrawlingJobBase):
    id: int
    user_id: int
    status: str
    progress: int
    current_product: int
    total_products: int
    result_file_path: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CrawlingProgress(BaseModel):
    status: str
    progress: int
    current: int
    total: int
    is_crawling: bool
    elapsed_time: int


# Admin 스키마
class UserApprovalRequest(BaseModel):
    user_id: int
    is_approved: bool  # is_active를 의미 (기존 호환성 유지)

