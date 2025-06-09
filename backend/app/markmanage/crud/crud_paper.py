from backend.app.markmanage.models import Paper  # 从统一入口导入

from crud_exam import ExamCRUD


class PaperCRUD:
    """答卷增删改查操作"""

    @staticmethod
    def submit_paper(db, exam_id: int, student_id: int, answers: dict):
        """提交答卷"""
        try:
            exam = ExamCRUD.get_exam(db, exam_id)
            if not exam:
                raise ValueError("考试不存在")

            # 验证答题数量
            exam_questions = {str(q["id"]): q for q in exam.questions}
            if set(answers.keys()) != set(exam_questions.keys()):
                missing = set(exam_questions.keys()) - set(answers.keys())
                extra = set(answers.keys()) - set(exam_questions.keys())
                raise ValueError(f"缺少题目ID: {missing}, 多余题目ID: {extra}")

            new_paper = Paper(
                exam_id=exam_id,
                student_id=student_id,
                # answers=answers,
                # scores={},  # 初始得分为空
                total_score=0.0,
                status="pending"
            )
            db.add(new_paper)
            db.commit()
            db.refresh(new_paper)
            return new_paper
        except Exception as e:
            db.rollback()
            raise ValueError(f"提交答卷失败: {str(e)}")

    @staticmethod
    def get_paper_by_id(db, paper_id: int):
        """通过ID获取答卷"""
        return db.query(Paper).filter(Paper.id == paper_id).first()

    @staticmethod
    def grade_paper(db, paper_id: int, scores: dict, comments: str = ""):
        """批改答卷"""
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise ValueError("答卷不存在")

        exam = paper.exam
        exam_questions = {str(q["id"]): q for q in exam.questions}

        try:
            # 验证批改数据
            if set(scores.keys()) != set(exam_questions.keys()):
                missing = set(exam_questions.keys()) - set(scores.keys())
                extra = set(scores.keys()) - set(exam_questions.keys())
                raise ValueError(f"缺少评分题目ID: {missing}, 多余题目ID: {extra}")

            # 验证单题分数不超过最大值
            total_score = 0.0
            for qid, score in scores.items():
                max_score = exam_questions[qid]["max_score"]
                if score > max_score:
                    raise ValueError(f"题目{qid}得分{score}超过最大值{max_score}")
                total_score += score

            # 更新批改信息
            paper.scores = scores
            paper.teacher_comments = comments
            paper.total_score = total_score
            paper.status = "graded"

            db.commit()
            db.refresh(paper)
            return paper
        except Exception as e:
            db.rollback()
            raise ValueError(f"批改答卷失败: {str(e)}")

    @staticmethod
    def update_paper_status(db, paper_id: int, status: str, comments: str = None):
        """更新答卷状态"""
        if status not in ["pending", "reviewed", "graded"]:
            raise ValueError("无效的状态值")

        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise ValueError("答卷不存在")

        try:
            paper.status = status
            if comments is not None:
                paper.teacher_comments = comments
            db.commit()
            db.refresh(paper)
            return paper
        except Exception as e:
            db.rollback()
            raise ValueError(f"更新答卷状态失败: {str(e)}")

    @staticmethod
    def delete_paper(db, paper_id: int):
        """删除答卷"""
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise ValueError("答卷不存在")

        try:
            db.delete(paper)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise ValueError(f"删除答卷失败: {str(e)}")

    @staticmethod
    def list_papers_by_exam(db, exam_id: int, status: str = None, limit: int = 100, offset: int = 0):
        """按考试列出答卷"""
        query = db.query(Paper).filter(Paper.exam_id == exam_id)
        if status:
            query = query.filter(Paper.status == status)
        return query.offset(offset).limit(limit).all()

    @staticmethod
    def list_papers_by_student(db, student_id: int, status: str = None, limit: int = 100, offset: int = 0):
        """按学生列出答卷"""
        query = db.query(Paper).filter(Paper.student_id == student_id)
        if status:
            query = query.filter(Paper.status == status)
        return query.offset(offset).limit(limit).all()

# if __name__ == "__main__":
#     # 创建所有表（生产环境应使用迁移工具）
#     Base.metadata.create_all(bind=engine)
#
#     # 依赖注入
#     db = SessionLocal()
#
#     try:
#
#         # 1. 学生提交答卷
#         student_answers = {
#             "1": "B",  # 第一题答案
#             "2": "ORM提高了开发效率，减少了SQL代码编写"  # 第二题答案
#         }
#
#         paper = PaperCRUD.submit_paper(
#             db,
#             exam_id=exam.id,
#             student_id=3,
#             answers=student_answers
#         )
#         print(f"提交答卷: ID={paper.id}, 学生=student_chen")
#
#         # 2. 教师批改答卷
#         grading_scores = {
#             "1": 5.0,  # 第一题满分
#             "2": 8.0  # 第二题部分得分
#         }
#
#         graded_paper = PaperCRUD.grade_paper(
#             db,
#             paper_id=paper.id,
#             scores=grading_scores,
#             comments="第二题回答不完整，缺少可读性优势"
#         )
#         print(f"批改完成: 总分={graded_paper.total_score}, 状态={graded_paper.status}")
#
#         # 3. 查询相关数据
#         # 查询教师创建的所有考试
#         teacher_exams = ExamCRUD.list_exams(db, creator_id=1)
#         print(f"\n教师创建的考试数: {len(teacher_exams)}")
#
#         # 查询指定考试的已批改答卷
#         graded_papers = PaperCRUD.list_papers_by_exam(db, exam_id=exam.id, status="graded")
#         print(f"\n考试{exam.title}的已批改答卷: {len(graded_papers)}份")
#
#         # 查询学生的所有答卷
#         student_papers = PaperCRUD.list_papers_by_student(db, student_id=3)
#         print(f"\n学生student_chen的答卷: {len(student_papers)}份")
#         for p in student_papers:
#             print(f"  考试ID:{p.exam_id}, 状态:{p.status}, 得分:{p.total_score}")
#
#     except Exception as e:
#         print(f"操作出错: {str(e)}")
#     finally:
#         db.close()
