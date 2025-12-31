"""
数据库迁移脚本：添加用户资料字段
运行方式: python migrate_add_profile_fields.py
"""
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

def migrate():
    """添加用户资料字段到 users 表"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # 检查字段是否已存在
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result]
            
            # 添加 nickname 字段
            if 'nickname' not in columns:
                print("添加 nickname 字段...")
                conn.execute(text("ALTER TABLE users ADD COLUMN nickname VARCHAR(50)"))
                conn.commit()
                print("✓ nickname 字段添加成功")
            else:
                print("✓ nickname 字段已存在")
            
            # 添加 gender 字段
            if 'gender' not in columns:
                print("添加 gender 字段...")
                conn.execute(text("ALTER TABLE users ADD COLUMN gender VARCHAR(10)"))
                conn.commit()
                print("✓ gender 字段添加成功")
            else:
                print("✓ gender 字段已存在")
            
            # 添加 age 字段
            if 'age' not in columns:
                print("添加 age 字段...")
                conn.execute(text("ALTER TABLE users ADD COLUMN age INTEGER"))
                conn.commit()
                print("✓ age 字段添加成功")
            else:
                print("✓ age 字段已存在")
            
            print("\n数据库迁移完成！")
            
        except Exception as e:
            print(f"迁移失败: {e}")
            conn.rollback()
            sys.exit(1)

if __name__ == "__main__":
    migrate()

