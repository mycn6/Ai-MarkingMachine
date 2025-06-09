import os
from dotenv import load_dotenv
from typing import List

# 加载环境变量
load_dotenv()


class Settings:
    # 基本配置
    ANSWER_UPLOAD_DIR = os.getenv("ANSWER_UPLOAD_DIR", "./answer_uploads")
    QUESTION_UPLOAD_DIR = os.getenv("QUESTION_UPLOAD_DIR", "./question_uploads")

    # 允许的文件类型
    @property
    def ALLOWED_EXAM_FILE_TYPES(self) -> List[str]:
        types = os.getenv("ALLOWED_EXAM_FILE_TYPES", "pdf")
        return [t.strip().lower() for t in types.split(",")]

    # 最大文件大小（默认为20MB）
    MAX_EXAM_FILE_SIZE = int(os.getenv("MAX_EXAM_FILE_SIZE", 20971520))

    # 分块大小（默认为1MB）
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1048576))

    # 其他配置
    PROJECT_NAME = "Exam Management System"
    API_V1_STR = "/api/v1"


settings = Settings()
