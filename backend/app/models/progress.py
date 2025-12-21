"""学习进度模型"""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class LearningProgress(Base):
    """学习进度模型"""
    __tablename__ = "learning_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    total_conversations = Column(Integer, default=0)
    total_time = Column(Integer, default=0)  # 总学习时长（秒）
    average_score = Column(Float, default=0.0)  # 平均发音评分
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User", backref="learning_progress")

