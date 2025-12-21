"""学习进度API路由"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.sql import extract
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.models.progress import LearningProgress

router = APIRouter(prefix="/api/progress", tags=["学习进度"])


class ProgressResponse(BaseModel):
    """学习进度响应模型"""
    total_conversations: int
    total_time: int  # 总学习时长（秒）
    average_score: float
    today_conversations: int
    today_time: int
    weekly_conversations: int
    weekly_time: int
    monthly_conversations: int
    monthly_time: int


class ConversationStats(BaseModel):
    """对话统计模型"""
    date: str
    count: int
    total_time: int


class ProgressStatsResponse(BaseModel):
    """进度统计响应模型"""
    progress: ProgressResponse
    daily_stats: List[ConversationStats]
    recent_conversations: List[dict]


@router.get("/", response_model=ProgressResponse)
async def get_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取学习进度"""
    # 获取或创建学习进度记录
    progress = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id
    ).first()
    
    if not progress:
        progress = LearningProgress(user_id=current_user.id)
        db.add(progress)
        db.commit()
        db.refresh(progress)
    
    # 计算统计数据
    total_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.user_id == current_user.id
    ).scalar() or 0
    
    # 计算总学习时长（估算：每条消息平均30秒）
    total_messages = db.query(func.count(Message.id)).join(Conversation).filter(
        Conversation.user_id == current_user.id
    ).scalar() or 0
    total_time = total_messages * 30  # 估算值
    
    # 计算平均发音评分
    avg_score = db.query(func.avg(Message.pronunciation_score)).join(Conversation).filter(
        Conversation.user_id == current_user.id,
        Message.pronunciation_score.isnot(None)
    ).scalar() or 0.0
    
    # 今日统计
    today = datetime.now().date()
    today_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.user_id == current_user.id,
        func.date(Conversation.started_at) == today
    ).scalar() or 0
    
    today_messages = db.query(func.count(Message.id)).join(Conversation).filter(
        Conversation.user_id == current_user.id,
        func.date(Message.created_at) == today
    ).scalar() or 0
    today_time = today_messages * 30
    
    # 本周统计
    week_start = today - timedelta(days=today.weekday())
    weekly_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.user_id == current_user.id,
        func.date(Conversation.started_at) >= week_start
    ).scalar() or 0
    
    weekly_messages = db.query(func.count(Message.id)).join(Conversation).filter(
        Conversation.user_id == current_user.id,
        func.date(Message.created_at) >= week_start
    ).scalar() or 0
    weekly_time = weekly_messages * 30
    
    # 本月统计
    month_start = today.replace(day=1)
    monthly_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.user_id == current_user.id,
        func.date(Conversation.started_at) >= month_start
    ).scalar() or 0
    
    monthly_messages = db.query(func.count(Message.id)).join(Conversation).filter(
        Conversation.user_id == current_user.id,
        func.date(Message.created_at) >= month_start
    ).scalar() or 0
    monthly_time = monthly_messages * 30
    
    # 更新进度记录
    progress.total_conversations = total_conversations
    progress.total_time = total_time
    progress.average_score = float(avg_score)
    db.commit()
    
    return ProgressResponse(
        total_conversations=total_conversations,
        total_time=total_time,
        average_score=float(avg_score),
        today_conversations=today_conversations,
        today_time=today_time,
        weekly_conversations=weekly_conversations,
        weekly_time=weekly_time,
        monthly_conversations=monthly_conversations,
        monthly_time=monthly_time
    )


@router.get("/stats", response_model=ProgressStatsResponse)
async def get_progress_stats(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取详细进度统计"""
    # 获取基础进度
    progress = await get_progress(current_user, db)
    
    # 获取每日统计
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    daily_stats = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        count = db.query(func.count(Conversation.id)).filter(
            Conversation.user_id == current_user.id,
            func.date(Conversation.started_at) == date
        ).scalar() or 0
        
        messages = db.query(func.count(Message.id)).join(Conversation).filter(
            Conversation.user_id == current_user.id,
            func.date(Message.created_at) == date
        ).scalar() or 0
        total_time = messages * 30
        
        daily_stats.append(ConversationStats(
            date=date.isoformat(),
            count=count,
            total_time=total_time
        ))
    
    # 获取最近的对话
    recent_conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.started_at.desc()).limit(10).all()
    
    recent_list = []
    for conv in recent_conversations:
        message_count = db.query(func.count(Message.id)).filter(
            Message.conversation_id == conv.id
        ).scalar() or 0
        
        recent_list.append({
            "id": conv.id,
            "scenario": conv.scenario,
            "started_at": conv.started_at.isoformat(),
            "message_count": message_count
        })
    
    return ProgressStatsResponse(
        progress=progress,
        daily_stats=daily_stats,
        recent_conversations=recent_list
    )


@router.post("/update-time")
async def update_learning_time(
    conversation_id: int,
    duration: int,  # 学习时长（秒）
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新学习时长"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        return {"success": False, "message": "对话不存在"}
    
    # 更新学习进度
    progress = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id
    ).first()
    
    if progress:
        progress.total_time += duration
        db.commit()
    
    return {"success": True, "message": "学习时长已更新"}

