"""安全工具函数"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from app.core.config import settings
import hashlib


def _prepare_password_bytes(password: str) -> bytes:
    """准备密码字节用于bcrypt哈希
    
    bcrypt限制密码不能超过72字节。如果密码超过72字节，
    先使用SHA256哈希，然后再用bcrypt哈希。
    """
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # 先进行SHA256哈希，然后转换为字节
        return hashlib.sha256(password_bytes).digest()
    return password_bytes


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        # 准备密码字节
        password_bytes = _prepare_password_bytes(plain_password)
        # 验证密码
        return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """获取密码哈希
    
    如果密码超过72字节，先使用SHA256哈希，然后再用bcrypt哈希
    这样可以处理任意长度的密码
    """
    # 准备密码字节
    password_bytes = _prepare_password_bytes(password)
    # 生成盐并哈希密码
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """解码访问令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

