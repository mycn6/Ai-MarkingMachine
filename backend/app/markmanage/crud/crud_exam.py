# backend/app/markmanage/crud/exam_crud.py

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.markmanage.models.exam import Exam
from datetime import datetime

from sqlalchemy import select, update, delete, text


class ExamCRUD:
    """考试模型的数据库操作"""

    async def create_exam(self, session: AsyncSession, title: str,
                          subject: str,
                          description: str,
                          time: datetime,
                          creator_id: int,
                          questions_path: str,
                          questions_filename: str
                          ) -> Exam:
        """创建考试记录"""
        exam = Exam(
            title=title,
            subject=subject,
            description=description,
            time=time,
            creator_id=creator_id,
            questions_filename=questions_filename,
            questions_path=questions_path
        )
        session.add(exam)
        await session.commit()
        await session.refresh(exam)
        return exam

    async def get_exam_by_id(self, session: AsyncSession, exam_id: int):
        """根据ID获取考试记录"""
        result = await session.execute(select(Exam).filter(Exam.id == exam_id))
        return result.scalars().first()

    async def update_exam(
            self, session: AsyncSession,
            exam_id: int,
            update_data: dict,

    ) -> Exam:
        """更新考试记录"""
        exam = await self.get_exam_by_id(session, exam_id)
        if not exam:
            return None
        stmt = (
            update(Exam)
            .where(Exam.id == exam_id)
            .values(**update_data)
        )
        await session.execute(stmt)
        await session.commit()
        await session.refresh(exam)
        return exam

    async def delete_exam(self, session: AsyncSession, exam_id: int):
        """删除考试记录"""
        if not await self.get_exam_by_id(session, exam_id):
            return None
        stmt = delete(Exam).where(Exam.id == exam_id)
        await session.execute(stmt)
        await session.commit()
        return exam_id

    #     async def list_users(self, db: AsyncSession, role: str = None, limit: int = 100, offset: int = 0):
    #         """列出所有用户"""
    #
    #         # 1. 构建基础查询
    #         stmt = select(User)
    #
    #         # 2. 应用过滤条件
    #         if role:
    #             stmt = stmt.where(User.role == role)
    #
    #         # 3. 应用分页
    #         stmt = stmt.limit(limit).offset(offset)
    #
    #         # 4. 执行异步查询
    #         result = await db.execute(stmt)
    #         users = result.scalars().all()
    #         return users
    async def get_exam_list(
            self,
            session: AsyncSession,
            limit: int = 100,
            offset: int = 0
    ):
        """获取考试列表"""
        result = await session.execute(text("SELECT DATABASE()"))
        db_name = result.scalar()
        print(f"当前连接数据库: {db_name}")

        # 调试: 检查表是否存在
        result = await session.execute(text("SHOW TABLES"))
        tables = result.scalars().all()
        print(f"数据库中的表: {tables}")

        # 执行查询
        query = select(Exam).order_by(Exam.time.desc()).offset(offset).limit(limit)
        print(f"生成的SQL: {str(query)}")

        result = await session.execute(
            select(Exam)
            .order_by(Exam.time.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()
        # stmt = select(Exam)
        # stmt = stmt.limit(limit).offset(offset)
        # result = await session.execute(stmt)
        # return result.scalars().all()

    #     获取文件路径和文件名
    async def get_file_path(self, session: AsyncSession, exam_id: int):
        """获取文件路径"""
        exam = await self.get_exam_by_id(session, exam_id)
        if not exam:
            return None
        return exam.questions_path, exam.questions_filename
