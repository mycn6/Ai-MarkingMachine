from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from backend.database.db_mysql import Base


class Paper(Base):
    __tablename__ = 'papers'

    id = Column(Integer, primary_key=True, index=True)

    exam_id = Column(Integer, ForeignKey('exams.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    # 学生答案和评分数据
    paper_path = Column(String(100), nullable=False)
    content = Column(Text)   # 经过识别的文本内容
    # answers = Column(LargeBinary)  # 存储文件
    scores_comments = Column(Text)

    # total_score = Column(Float, default=0.0)
    status = Column(String(20), default='pending')   #（pending/reviewed/graded）

    # 关系
    exam = relationship("Exam", back_populates="papers")
    student = relationship("User", back_populates="papers")
