from backend.app.markmanage.crud.crud_user import UserCRUD
from backend.app.markmanage.models.user import User
from backend.database.db_mysql import async_db_session
from backend.common.exception import errors
from passlib.context import CryptContext


class UserService:
    def __init__(self):
        self.crud = UserCRUD()  # 创建CRUD实例
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def create_user(self, username: str, password: str, role: str, full_name: str = None,
                          email: str = None) -> User:
        # 在服务层处理密码哈希
        hashed_password = self.pwd_context.hash(password)
        async with async_db_session() as db:
            user = await self.crud.create_user(
                db=db,
                username=username,
                password=hashed_password,  # 传递哈希后的密码
                role=role,
                full_name=full_name,
                email=email
            )
            if not user:
                # 抛出业务异常
                raise errors.RequestError(msg='创建用户失败')
            return user.id

    async def get_user(self, user_id) -> User:
        async with async_db_session() as db:
            user = await UserCRUD.get_user_by_id(self.crud, db, user_id)

            if not user:
                raise errors.NotFoundError(msg='用户不存在')

            return user

    async def get_user_by_username(self, username: str) -> User:
        async with async_db_session() as db:
            user = await UserCRUD.get_user_by_username(self.crud, db, username)
            if not user:
                raise errors.NotFoundError(msg='用户不存在')
            return user

    async def update_user(self, user_id: int, update_data: dict) -> User:
        async with async_db_session() as db:
            user = await UserCRUD.update_user(self.crud, db, user_id, update_data)
            if not user:
                raise errors.NotFoundError(msg='用户不存在')
            return user

    async def delete_user(self, user_id: int) -> None:
        async with async_db_session() as db:
            result = await UserCRUD.delete_user(self.crud, db, user_id)
            if not result:
                raise errors.NotFoundError(msg='用户不存在')
            return result

    async def list_users(self, role: str = None, limit: int = 100, offset: int = 0) -> list[User]:
        async with async_db_session() as db:
            users = await UserCRUD.list_users(self.crud, db, role, limit, offset)
            return users


user_service = UserService()
