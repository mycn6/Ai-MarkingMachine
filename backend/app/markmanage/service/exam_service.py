# import os
# from datetime import datetime
# from typing import Optional
#
# from sqlalchemy.future import select
# from fastapi import UploadFile, Form, File
#
# from backend.common.exception import errors
# from backend.utils.file_utils import validate_file, save_upload_file
#
# from backend.database.engine import async_db_session
# from backend.app.markmanage.schema.exam import ExamBase
# from backend.app.markmanage.models.exam import Exam
# from backend.config.fileConfig import settings
#
#
# class ExamFileService:
#     # 创建考试
#     # Form为FastAPI提供的表单参数装饰器
#     # File为FastAPI提供的文件上传装饰器
#     # 此时可以成功从前端获取表单参数和文件上传
#     async def create_exam(
#             self,
#             title: str = Form(...),
#             subject: str = Form(...),
#             description: str = Form(...),
#             time: datetime = Form(...),
#             # 这里的默认值是1，表示当前用户ID，后续需要改成登录用户ID
#             creator_id: int = Form(...),
#             # answers_file: UploadFile = File(...),
#             questions_file: UploadFile = File(...)
#     ):
#         """创建考试记录并保存相关文件"""
#
#         # if not answers_file and not questions_file:
#         #     raise errors.RequestError(msg='请上传答案和题目文件')
#         # # 验证答案文件
#         # answer_validate, answers_msg = await validate_file(answers_file, settings.ALLOWED_EXAM_FILE_TYPES,
#         #                                                    settings.MAX_EXAM_FILE_SIZE)
#         # if not answer_validate:
#         #     raise errors.InvalidFileName(msg=answers_msg)
#
#         # 验证题目文件
#         questions_validate, questions_msg = await validate_file(questions_file, settings.ALLOWED_EXAM_FILE_TYPES,
#                                                                 settings.MAX_EXAM_FILE_SIZE)
#         if not questions_validate:
#             raise errors.InvalidFileName(msg=questions_msg)
#
#         # # 保存答案文件
#         # answers_path, answers_filename = await save_upload_file(answers_file, settings.ANSWER_UPLOAD_DIR)
#         #
#         # if not answers_path and not answers_filename:
#         #     raise errors.ServerError(msg='保存答案文件失败')
#         # 保存题目文件
#         questions_path, questions_filename = await save_upload_file(questions_file, settings.QUESTION_UPLOAD_DIR)
#
#         if not questions_path and not questions_filename:
#             raise errors.ServerError(msg='保存题目文件失败')
#
#         # 创建考试模型实例
#         new_exam = Exam(
#             title=title,
#             subject=subject,
#             description=description,
#             time=time,
#             creator_id=creator_id,
#             # answers_path=answers_path,
#             # answers_filename=answers_filename,
#             questions_path=questions_path,
#             questions_filename=questions_filename
#         )
#
#         # 异步保存到数据库
#         async with async_db_session() as session:
#
#             session.add(new_exam)
#             await session.commit()
#             await session.refresh(new_exam)
#
#         # 返回 Pydantic 模型
#         return new_exam.id
#
#     # 更新考试
#     async def update_exam_files(
#             self,
#             exam_id: int = Form(...),
#             # answers_file: UploadFile = File(None),
#             questions_file: UploadFile = File(None)
#     ) -> ExamBase:
#         """更新考试的答案或题目文件"""
#         # 获取考试记录
#         async with async_db_session() as session:
#             result = await session.execute(select(Exam).filter(Exam.id == exam_id))
#             exam = result.scalars().first()
#
#             if not exam:
#                 raise errors.NotFoundError(msg='考试记录不存在')
#
#             # 更新答案文件
#             # if answers_file:
#             #     await validate_file(answers_file, settings.ALLOWED_EXAM_FILE_TYPES, settings.MAX_EXAM_FILE_SIZE)
#             #
#             #     # 删除旧文件
#             #     if exam.answers_path and os.path.exists(exam.answers_path):
#             #         try:
#             #             os.remove(exam.answers_path)
#             #         except OSError as e:
#             #             # 记录错误但不中断操作
#             #             # print(f"删除旧答案文件失败: {str(e)}")
#             #             raise errors.ServerError(msg='删除旧答案文件失败')
#             #
#             #     # 保存新文件
#             #     answers_path, answers_filename = await save_upload_file(answers_file, settings.UPLOAD_DIR)
#             #     exam.answers_path = answers_path
#             #     exam.answers_filename = answers_filename
#
#             # 更新题目文件
#             if questions_file:
#                 await validate_file(questions_file, settings.ALLOWED_EXAM_FILE_TYPES, settings.MAX_EXAM_FILE_SIZE)
#
#                 # 删除旧文件
#                 if exam.questions_path and os.path.exists(exam.questions_path):
#                     try:
#                         os.remove(exam.questions_path)
#                     except OSError as e:
#                         # 记录错误但不中断操作
#                         # print(f"删除旧题目文件失败: {str(e)}")
#                         raise errors.ServerError(msg='删除旧题目文件失败')
#
#                 # 保存新文件
#                 questions_path, questions_filename = await save_upload_file(questions_file,
#                                                                             settings.QUESTION_UPLOAD_DIR)
#                 exam.questions_path = questions_path
#                 exam.questions_filename = questions_filename
#
#             # 更新考试记录
#             exam.updated_at = datetime.utcnow()
#             await session.commit()
#             await session.refresh(exam)
#
#         return ExamBase.from_orm(exam)
#
#     # 删除考试
#     async def delete_exam_files(
#             self,
#             exam_id: int
#     ) -> None:
#         """删除考试及其相关文件"""
#         async with async_db_session() as session:
#             result = await session.execute(select(Exam).filter(Exam.id == exam_id))
#             exam = result.scalars().first()
#
#             if not exam:
#                 raise errors.NotFoundError(msg='考试记录不存在')
#
#             # # 删除相关文件
#             # if exam.answers_path and os.path.exists(exam.answers_path):
#             #     try:
#             #         os.remove(exam.answers_path)
#             #     except OSError as e:
#             #         # print(f"删除答案文件失败: {str(e)}")
#             #         raise errors.ServerError(msg='删除答案文件失败')
#
#             if exam.questions_path and os.path.exists(exam.questions_path):
#                 try:
#                     os.remove(exam.questions_path)
#                 except OSError as e:
#                     # print(f"删除题目文件失败: {str(e)}")
#                     raise errors.ServerError(msg='删除题目文件失败')
#
#             # 删除数据库记录
#             await session.delete(exam)
#             await session.commit()
#
#     # 获取考试记录
#     async def get_exam_by_id(
#             self,
#             exam_id: int
#     ) -> Optional[ExamBase]:
#         """根据ID获取考试记录"""
#         async with async_db_session() as session:
#             result = await session.execute(select(Exam).filter(Exam.id == exam_id))
#             exam = result.scalars().first()
#
#             if not exam:
#                 raise errors.NotFoundError(msg='考试记录不存在')
#
#             return ExamBase.from_orm(exam)
#
#     # 获取考试列表
#     # skip: 跳过的记录数
#     # limit: 每页记录数
#     # 默认返回最新100条记录
#     async def list_exams(
#             self,
#             skip: int = 0,
#             limit: int = 100
#     ) -> list[ExamBase]:
#         """获取考试列表"""
#         async with async_db_session() as session:
#             result = await session.execute(
#                 select(Exam)
#                 .order_by(Exam.time.desc())
#                 .offset(skip)
#                 .limit(limit)
#             )
#             exams = result.scalars().all()
#
#             return [ExamBase.from_orm(exam) for exam in exams]
#
#     # 获取文件路径和原始文件名
#     async def get_file_path(
#             self,
#             exam_id: int,
#             # file_type: str  # 'answers' or 'questions'
#     ) -> tuple[str, str]:
#         """获取文件路径和原始文件名"""
#         async with async_db_session() as session:
#             result = await session.execute(select(Exam).filter(Exam.id == exam_id))
#             exam = result.scalars().first()
#
#             if not exam:
#                 raise errors.NotFoundError(msg='考试记录不存在')
#
#             # if file_type == 'answers':
#             #     file_path = exam.answers_path
#             #     filename = exam.answers_filename
#             # elif file_type == 'questions':
#             #     file_path = exam.questions_path
#             #     filename = exam.questions_filename
#             # else:
#             #     raise errors.RequestError(msg='文件类型错误')
#
#             # return file_path, filename
#             return exam.questions_path, exam.questions_filename
#
#
# exam_service = ExamFileService()


# backend/app/markmanage/service/exam_service.py

import os
from datetime import datetime
from typing import Optional, Union

from fastapi import UploadFile, Form, File

from backend.common.exception import errors
from backend.utils.file_utils import validate_file, save_upload_file
from backend.app.markmanage.schema.exam import ExamBase
from backend.config.fileConfig import settings
from backend.database.engine import async_db_session
from backend.app.markmanage.crud.crud_exam import ExamCRUD
from backend.app.markmanage.models.exam import Exam


class ExamService:
    """考试业务逻辑服务层"""

    def __init__(self):
        self.crud = ExamCRUD()

    async def create_exam(
            self,
            title: str = Form(...),
            subject: str = Form(...),
            description: str = Form(...),
            time: datetime = Form(...),
            creator_id: int = Form(...),
            questions_file: UploadFile = File(...)
    ):
        """创建考试记录并保存相关文件"""
        # 验证题目文件
        questions_validate, questions_msg = await validate_file(
            questions_file,
            settings.ALLOWED_EXAM_FILE_TYPES,
            settings.MAX_EXAM_FILE_SIZE
        )
        if not questions_validate:
            raise errors.InvalidFileName(msg=questions_msg)

        # 保存题目文件
        questions_path, questions_filename = await save_upload_file(
            questions_file,
            settings.QUESTION_UPLOAD_DIR
        )

        if not questions_path or not questions_filename:
            raise errors.ServerError(msg='保存题目文件失败')

        # 构造考试数据
        exam_data = {
            "title": title,
            "subject": subject,
            "description": description,
            "time": time,
            "creator_id": creator_id,
            "questions_path": questions_path,
            "questions_filename": questions_filename
        }

        # 使用CRUD创建考试记录
        async with async_db_session() as session:
            exam = await self.crud.create_exam(session,
                                               **exam_data)
            if not exam:
                raise errors.ServerError(msg='创建考试记录失败')
            return exam.id

    async def update_exam_files(
            self,
            exam_id: int = Form(...),
            questions_file: UploadFile = File(...)
    ):
        """更新考试的题目文件"""
        async with async_db_session() as session:
            # 获取考试记录
            exam = await self.crud.get_exam_by_id(session, exam_id)

            if not exam:
                raise errors.NotFoundError(msg='考试记录不存在')

            update_data = {}

            # 更新题目文件
            if questions_file:
                await validate_file(
                    questions_file,
                    settings.ALLOWED_EXAM_FILE_TYPES,
                    settings.MAX_EXAM_FILE_SIZE
                )

                # 删除旧文件
                if exam.questions_path and os.path.exists(exam.questions_path):
                    try:
                        os.remove(exam.questions_path)
                    except OSError:
                        raise errors.ServerError(msg='删除旧题目文件失败')

                # 保存新文件
                questions_path, questions_filename = await save_upload_file(
                    questions_file,
                    settings.QUESTION_UPLOAD_DIR
                )

                update_data.update({
                    "questions_path": questions_path,
                    "questions_filename": questions_filename
                })

            # 使用CRUD更新考试记录
            updated_exam = await self.crud.update_exam(session, exam.id, update_data)
            return updated_exam

    async def delete_exam_files(
            self,
            exam_id: int
    ):
        """删除考试及其相关文件"""
        async with async_db_session() as session:
            # 获取考试记录
            exam = await self.crud.get_exam_by_id(session, exam_id)

            if not exam:
                raise errors.NotFoundError(msg='考试记录不存在')

            # 删除题目文件
            if exam.questions_path and os.path.exists(exam.questions_path):
                try:
                    os.remove(exam.questions_path)
                except OSError:
                    raise errors.ServerError(msg='删除题目文件失败')

            # 使用CRUD删除考试记录
            await self.crud.delete_exam(session, exam.id)
            return exam_id

    async def get_exam_by_id(
            self,
            exam_id: int
    ):
        """根据ID获取考试记录"""
        async with async_db_session() as session:
            exam = await ExamCRUD.get_exam_by_id(self.crud, session, exam_id)

            if not exam:
                raise errors.NotFoundError(msg='考试记录不存在')

            return exam

    async def list_exams(
            self,
            limit: int = 100,
            offset: int = 0
    ) -> list[Exam]:
        """获取考试列表"""
        async with async_db_session() as session:
            exams = await self.crud.get_exam_list(session, limit, offset)
            return exams

    async def get_exam_file_info(
            self,
            exam_id: int
    ) -> tuple[str, str]:
        """获取考试的文件信息"""
        async with async_db_session() as session:
            exam = await self.crud.get_exam_by_id(session, exam_id)

            if not exam:
                raise errors.NotFoundError(msg='考试记录不存在')

            return exam.questions_path, exam.questions_filename


# Service 实例
exam_service = ExamService()
