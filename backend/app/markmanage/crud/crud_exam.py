# import os
# from pathlib import Path
#
# # from sqlalchemy.orm import Session
# # 使用异步数据库连接
# from sqlalchemy.ext.asyncio import AsyncSession
# from backend.config import FileConfig
#
# from backend.utils.file_service import FileService
# from datetime import datetime
#
# from backend.app.markmanage.models import Exam  # 从统一入口导入
#
#
# class ExamCRUD:
#
#     def create_exam(self, db: AsyncSession, title: str, subject: str,creator_id: int, questions_data: bytes, answers_data: bytes,
#                     description: str = None,
#                     time: datetime = None,
#                     ) -> Exam:
#         """创建考试并保存文件"""
#
#         # 验证PDF文件
#         if not FileService.validate_pdf(questions_data):
#             raise ValueError("无效的题目PDF文件格式")
#
#         if answers_data and not FileService.validate_pdf(answers_data):
#             raise ValueError("无效的答案PDF文件格式")
#
#         try:
#             # 创建考试记录
#             new_exam = Exam(
#                 title=title,
#                 subject=subject,
#                 description=description,
#                 time=time,
#                 # creator_id=creator_id,
#                 # 其他文件元数据初始化为空
#             )
#             db.add(new_exam)
#             db.commit()
#             db.refresh(new_exam)
#
#             # 保存题目文件
#             questions_path = FileConfig.get_exam_path(new_exam.id, "questions.pdf")
#             questions_meta = FileService.save_file(questions_data, questions_path)
#             new_exam.questions_path = questions_meta['path']
#             new_exam.questions_size = questions_meta['size']
#             new_exam.questions_hash = questions_meta['hash']
#             new_exam.questions_filename = questions_meta['filename']
#
#             # 保存答案文件（如果有）
#             if answers_data:
#                 answers_path = FileConfig.get_exam_path(new_exam.id, "answers.pdf")
#                 answers_meta = FileService.save_file(answers_data, answers_path)
#                 new_exam.answers_path = answers_meta['path']
#                 new_exam.answers_size = answers_meta['size']
#                 new_exam.answers_hash = answers_meta['hash']
#                 new_exam.answers_filename = answers_meta['filename']
#
#             db.commit()
#             return new_exam
#
#         except Exception as e:
#             # 回滚文件操作:如果已经保存了题目文件，则删除
#             if new_exam.questions_path and os.path.exists(new_exam.questions_path):
#                 os.remove(new_exam.questions_path)
#
#             # 回滚文件操作:如果已经保存了答案文件，则删除
#             if new_exam.answers_path and os.path.exists(new_exam.answers_path):
#                 os.remove(new_exam.answers_path)
#
#             db.rollback()
#             raise RuntimeError(f"创建考试失败: {str(e)}")
#
#     def update_exam_files(self, db: AsyncSession, exam_id: int,
#                           questions_data: bytes = None,
#                           answers_data: bytes = None) -> Exam:
#         """更新考试文件"""
#         exam = db.query(Exam).filter(Exam.id == exam_id).first()
#         if not exam:
#             raise ValueError("考试不存在")
#
#         try:
#             # 备份旧文件路径
#             old_questions_path = exam.questions_path
#             old_answers_path = exam.answers_path
#
#             if questions_data:
#                 # 验证新题目文件
#                 if not FileService.validate_pdf(questions_data):
#                     raise ValueError("无效的题目PDF文件格式")
#
#                 # 保存新题目文件
#                 questions_path = FileConfig.get_exam_path(exam_id, "questions.pdf")
#                 questions_meta = FileService.save_file(questions_data, questions_path)
#
#                 # 更新数据库记录
#                 exam.questions_path = questions_meta['path']
#                 exam.questions_size = questions_meta['size']
#                 exam.questions_hash = questions_meta['hash']
#                 exam.questions_filename = questions_meta['filename']
#
#                 # 删除旧文件
#                 if old_questions_path and os.path.exists(old_questions_path):
#                     os.remove(old_questions_path)
#
#             if answers_data:
#                 # 验证新答案文件
#                 if not FileService.validate_pdf(answers_data):
#                     raise ValueError("无效的答案PDF文件格式")
#
#                 # 保存新答案文件
#                 answers_path = FileConfig.get_exam_path(exam_id, "answers.pdf")
#                 answers_meta = FileService.save_file(answers_data, answers_path)
#
#                 # 更新数据库记录
#                 exam.answers_path = answers_meta['path']
#                 exam.answers_size = answers_meta['size']
#                 exam.answers_hash = answers_meta['hash']
#                 exam.answers_filename = answers_meta['filename']
#
#                 # 删除旧文件
#                 if old_answers_path and os.path.exists(old_answers_path):
#                     os.remove(old_answers_path)
#
#             db.commit()
#             return exam
#
#         except Exception as e:
#             # 清理可能已创建的新文件
#             if questions_data:
#                 try:
#                     os.remove(questions_path)
#                 except:
#                     pass
#
#             if answers_data:
#                 try:
#                     os.remove(answers_path)
#                 except:
#                     pass
#
#             db.rollback()
#             raise RuntimeError(f"更新考试文件失败: {str(e)}")
#
#     def get_questions_file(self, exam: Exam) -> bytes:
#         """获取题目文件内容"""
#         if not exam.questions_path:
#             raise ValueError("该考试未上传题目文件")
#
#         return FileService.load_file(Path(exam.questions_path))
#
#     def get_answers_file(self, exam: Exam) -> bytes:
#         """获取答案文件内容"""
#         if not exam.answers_path:
#             raise ValueError("该考试未上传答案文件")
#
#         return FileService.load_file(Path(exam.answers_path))
#
#     def delete_exam(self, db, exam_id: int):
#         """删除考试（同时会级联删除答卷）"""
#         exam = db.query(Exam).filter(Exam.id == exam_id).first()
#         if not exam:
#             raise ValueError("考试不存在")
#
#         try:
#             db.delete(exam)
#             db.commit()
#             return True
#         except Exception as e:
#             db.rollback()
#             raise ValueError(f"删除考试失败: {str(e)}")
#
#     def list_exams(self, db, creator_id: int = None, limit: int = 100, offset: int = 0):
#         """列出所有考试"""
#         query = db.query(Exam)
#         if creator_id:
#             query = query.filter(Exam.creator_id == creator_id)
#         return query.offset(offset).limit(limit).all()
#
#     def get_exam(self, db, exam_id: int):
#         """获取考试"""
#         return db.query(Exam).filter(Exam.id == exam_id).first()
