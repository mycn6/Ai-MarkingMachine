from sqlalchemy import Column, Integer, String, Text, DateTime

from sqlalchemy.orm import relationship
from backend.database.base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    full_name = Column(String(100))
    email = Column(String(100), unique=True)
    role = Column(String(20), nullable=False)  # 'teacher' 或 'student'
    # 老师教的班级,假设一个老师只能教一个班级
    class_name = Column(String(100))

    # 关系
    exams_created = relationship("Exam", back_populates="creator")
    papers = relationship("Paper", back_populates="student")
