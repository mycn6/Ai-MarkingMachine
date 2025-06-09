from backend.app.markmanage.models import User  # 从统一入口导入
from sqlalchemy.ext.asyncio import AsyncSession
# 使用外部库实现增删改查，不需手敲sqlalchemy语句
# from sqlalchemy_crud_plus import CRUDPlus


from sqlalchemy import select, update, delete


# ----- CRUD工具类 -----
class UserCRUD:
    """用户增删改查操作"""

    async def create_user(self, db: AsyncSession, username: str,
                          password: str,
                          role: str,
                          class_name: str,
                          full_name: str | None = None,
                          email: str | None = None
                          ):
        """创建用户"""

        user = User(
            username=username,
            password=password,
            email=email,
            full_name=full_name,
            role=role,
            class_name=class_name
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> User:
        """通过ID获取用户"""
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_user_by_username(self, db: AsyncSession, username: str) -> User:
        """通过用户名获取用户"""
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def update_user(self, db: AsyncSession, user_id: int, update_data: dict):
        """更新用户信息"""
        user = await self.get_user_by_id(db, user_id)
        if not user:
            return None
        # 更新用户信息
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(**update_data)
        )

        await db.execute(stmt)
        await db.commit()
        return await self.get_user_by_id(db, user_id)

    async def delete_user(self, db: AsyncSession, user_id: int):
        """删除模型"""
        if not await self.get_user_by_id(db, user_id):
            return None
        stmt = delete(User).where(User.id == user_id)
        await db.execute(stmt)
        await db.commit()
        return user_id

    async def list_users(self, db: AsyncSession, role: str = None, limit: int = 100, offset: int = 0):
        """列出所有用户"""

        # 1. 构建基础查询
        stmt = select(User)

        # 2. 应用过滤条件
        if role:
            stmt = stmt.where(User.role == role)

        # 3. 应用分页
        stmt = stmt.limit(limit).offset(offset)

        # 4. 执行异步查询
        result = await db.execute(stmt)
        users = result.scalars().all()
        return users
