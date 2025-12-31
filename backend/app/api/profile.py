"""用户资料API路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.utils.security import get_password_hash, verify_password

router = APIRouter(prefix="/api/profile", tags=["用户资料"])


class ProfileResponse(BaseModel):
    """用户资料响应模型"""
    id: int
    username: str
    email: str
    nickname: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    created_at: str
    
    class Config:
        from_attributes = True


class ProfileUpdateRequest(BaseModel):
    """用户资料更新请求模型"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$", description="性别")
    age: Optional[int] = Field(None, ge=1, le=150, description="年龄")


class PasswordChangeRequest(BaseModel):
    """修改密码请求模型"""
    old_password: str = Field(..., min_length=6, description="旧密码")
    new_password: str = Field(..., min_length=6, description="新密码")


@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户资料"""
    return ProfileResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        nickname=current_user.nickname,
        gender=current_user.gender,
        age=current_user.age,
        created_at=current_user.created_at.isoformat() if current_user.created_at else ""
    )


@router.put("", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户资料"""
    # 更新用户信息
    if profile_data.nickname is not None:
        current_user.nickname = profile_data.nickname
    if profile_data.gender is not None:
        current_user.gender = profile_data.gender
    if profile_data.age is not None:
        current_user.age = profile_data.age
    
    db.commit()
    db.refresh(current_user)
    
    return ProfileResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        nickname=current_user.nickname,
        gender=current_user.gender,
        age=current_user.age,
        created_at=current_user.created_at.isoformat() if current_user.created_at else ""
    )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    # 验证旧密码
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码不正确"
        )
    
    # 更新密码
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "密码修改成功"}

