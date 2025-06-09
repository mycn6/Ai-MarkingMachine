from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database.base import Base



class Exam(Base):
    __tablename__ = 'exams'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    subject = Column(String(200), nullable=False)
    description = Column(Text)
    time = Column(DateTime, nullable=False)
    # duration = Column(Integer)

    creator_id = Column(Integer, ForeignKey('users.id'))

    # 题目数据直接存储在数据库中
    # questions = Column(LargeBinary)  # 存储文件二进制内容
    # answers = Column(LargeBinary)  # 存储文件二进制内容
    # 暂时为英语作文批改，不需答案
    # answers_path = Column(String(200))  # 存储文件路径
    questions_path = Column(String(200))  # 存储文件路径
    questions_filename = Column(String(255), doc="题目文件原始名称")
    # answers_filename = Column(String(255), doc="答案文件原始名称")


    # 关系
    creator = relationship("User", back_populates="exams_created")
    papers = relationship("Paper", back_populates="exam")
