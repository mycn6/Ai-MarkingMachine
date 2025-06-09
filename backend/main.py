from contextlib import asynccontextmanager

import os

import asyncio
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.app.markmanage.api.router import v1 as parent_router
import uvicorn
from fastapi.staticfiles import StaticFiles

from backend.app.markmanage.crud.crud_user import UserCRUD
from backend.config.fileConfig import settings
from backend.database.db_mysql import async_engine

# 创建主应用
app = FastAPI(title="ai批改服务平台")

app.mount("/static", StaticFiles(directory="E:/Ai-MarkingMachine/backend/app/markmanage/static"), name="static")

app.include_router(parent_router, prefix="/homework_correction")  # ✅ 正确挂载方式

# 创建一个老师用户，以便后续扩展
# 1. 创建异步引擎
async_engine = create_async_engine(
    "mysql+asyncmy://root:123456@localhost/exam",
    future=True
)

# 2. 创建异步会话工厂
async_session_factory = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


@asynccontextmanager
async def get_db_session():
    """获取数据库会话的异步上下文管理器"""
    # 创建异步数据库会话

    session = async_session_factory()
    try:
        yield session
        await session.commit()  # 尝试提交事务
    except Exception as e:
        await session.rollback()  # 出错时回滚
        raise e
    finally:
        await session.close()  # 确保关闭会话


async def create_initial_user():
    """正确方式创建初始用户"""
    async with get_db_session() as session:
        user_crud = UserCRUD()
        await user_crud.create_user(
            db=session,
            username='teacher1',
            password='123456',
            role='teacher'
        )
        print("✅ 用户创建成功")


async def main():
    """主函数"""

    # 创建初始用户
    await create_initial_user()

    print("🎉 所有操作成功完成！")


# 运行主函数
# if __name__ == '__main__':
#     asyncio.run(main())

# 创建一个老师后，就可以运行服务
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8003)
