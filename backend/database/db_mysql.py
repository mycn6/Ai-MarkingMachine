import sys  # 导入sys模块，用于处理系统相关操作

from typing import Annotated  # 导入Annotated，用于类型提示
from uuid import uuid4  # 导入uuid4，用于生成UUID

import asyncio
from fastapi import Depends  # 导入Depends，用于依赖注入

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # 导入SQLAlchemy异步操作相关组件
import logging

from sqlalchemy.orm import declarative_base, sessionmaker

# SQLALCHEMY_DATABASE_URL = "mysql://root:123456@localhost/exam"   # 同步数据库连接URL
SQLALCHEMY_DATABASE_URL = "mysql+asyncmy://root:123456@localhost/exam"  # 异步数据库连接URL


def create_engine_and_session(url: str = SQLALCHEMY_DATABASE_URL):
    """创建数据库引擎和会话"""
    try:
        # 创建异步数据库引擎
        engine = create_async_engine(url, echo=True, future=True, pool_pre_ping=True)
        # logg.success'数据库连接成功')  # 可用于成功日志，但被注释掉
    except Exception as e:
        logging.error('❌ 数据库链接失败 {}', e)  # 如果数据库连接失败，记录错误日志
        sys.exit()  # 退出程序
    else:
        # 创建异步数据库会话生成器
        db_session = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
        return engine, db_session  # 返回数据库引擎和会话生成器


# # 调用函数创建引擎和会话生成器
async_engine, async_db_session = create_engine_and_session(SQLALCHEMY_DATABASE_URL)


async def get_db() -> AsyncSession:
    """依赖注入生成数据库会话"""
    session = async_db_session()  # 获取一个数据库会话
    try:
        yield session  # 返回当前会话供依赖注入使用
    except Exception as se:
        await session.rollback()  # 出现异常时回滚会话
        raise se  # 抛出异常
    finally:
        await session.close()  # 最终关闭会话


# 为数据库会话类型加上注解，方便FastAPI依赖注入
CurrentSession = Annotated[AsyncSession, Depends(get_db)]

# async def create_table():
#     """创建数据库表"""
#     # 使用异步数据库引擎执行创建表操作
#     async with async_engine.begin() as coon:
#         Base = declarative_base()
#         await coon.run_sync(Base.metadata.create_all)  # 创建所有映射的表
Base = declarative_base()


async def create_table():
    async with async_engine.begin() as conn:
        # 使用包装函数将连接传递给create_all
        def create_tables(conn):
            Base.metadata.create_all(bind=conn)

        await conn.run_sync(create_tables)


def uuid4_str() -> str:
    """数据库引擎 UUID 类型兼容性解决方案"""
    return str(uuid4())  # 返回生成的UUID字符串形式


async def main():
    # 创建表格
    await create_table()


if __name__ == '__main__':
    asyncio.run(main())
