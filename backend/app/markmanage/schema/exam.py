from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class ExamBase(BaseModel):
    # 考试
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(None, description="考试ID")
    title: str = Field(None, description="考试标题")
    subject: str = Field(None, description="考试科目")
    description: str = Field(None, description="考试描述")
    time: datetime = Field(None, description="考试时间")
    creator_id: int = Field(None, description="创建者ID")
    # answers_path: str = Field(None, description="答案文件路径")
    # answers_filename: str = Field(None, description="答案文件原始名称")
    questions_path: str = Field(None, description="题目文件路径")
    questions_filename: str = Field(None, description="题目文件原始名称")
