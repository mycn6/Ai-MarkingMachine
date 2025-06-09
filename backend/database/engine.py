# database/engine.py
import sys
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger("database")

# 数据库连接URL（从配置获取）
SQLALCHEMY_DATABASE_URL = "mysql+asyncmy://root:123456@localhost/exam"


def create_async_db_engine_and_session():
    """创建数据库引擎和会话工厂"""
    try:
        # future=True表示使用异步IO，pool_pre_ping=True表示ping数据库连接，防止连接断开
        engine = create_async_engine(SQLALCHEMY_DATABASE_URL, future=True, pool_pre_ping=True)
        logger.info('✅ 数据库引擎创建成功')

        db_session = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
        logger.info('✅ 数据库会话生成器创建成功')

        return engine, db_session
    except Exception as e:
        logger.error('❌ 数据库引擎创建失败: %s', e)
        sys.exit(1)


async_engine, async_db_session = create_async_db_engine_and_session()
