# 创建一个老师用户，以便后续扩展
# 1. 创建异步引擎
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from backend.app.markmanage.crud.crud_user import UserCRUD

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
            role='teacher',
            class_name='1班',
        )
        print("✅ 用户创建成功")


async def main():
    """主函数"""

    # 创建初始用户
    await create_initial_user()

    print("🎉 所有操作成功完成！")
if __name__ == '__main__':
    import asyncio
    asyncio.run(main())