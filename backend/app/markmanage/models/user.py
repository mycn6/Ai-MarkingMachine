from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from backend.database.db_mysql import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    full_name = Column(String(100))
    email = Column(String(100), unique=True)
    role = Column(String(20), nullable=False)  # 'teacher' 或 'student'
    # 班级信息
    # class_id = Column(Integer, nullable=True)

    # 关系
    exams_created = relationship("Exam", back_populates="creator")
    papers = relationship("Paper", back_populates="student")
