# utils/file_service.py
import os
import hashlib
from pathlib import Path
import logging

# 配置日志记录器
logger = logging.getLogger(__name__)  # 创建日志记录器实例
logger.setLevel(logging.INFO)         # 设置日志级别

# 创建控制台处理器并设置格式
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

class FileService:
    @staticmethod
    def save_file(data: bytes, file_path: Path) -> dict:
        """保存文件到指定路径，返回文件元数据"""
        with open(file_path, 'wb') as f:
            f.write(data)

        # 计算文件哈希
        file_hash = hashlib.sha256(data).hexdigest()
        file_size = len(data)

        # 提取纯净的文件名
        filename = file_path.name

        logger.info(f"文件保存成功: {filename} ({file_size / 1024:.2f}KB) [哈希: {file_hash}]")

        return {
            "path": str(file_path),
            "size": file_size,
            "hash": file_hash,
            "filename": filename
        }

    @staticmethod
    def load_file(file_path: Path) -> bytes:
        """从路径加载文件"""
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        with open(file_path, 'rb') as f:
            return f.read()

    @staticmethod
    def validate_pdf(file_data: bytes) -> bool:
        """简单验证PDF文件（检查文件头）"""
        # PDF文件以 '%PDF-' 开头
        return len(file_data) > 5 and file_data.startswith(b'%PDF-')

    @staticmethod
    def calculate_hash(data: bytes) -> str:
        """计算文件哈希"""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def get_file_metadata(file_path: Path) -> dict:
        """获取文件元数据"""
        file_size = os.path.getsize(file_path)
        with open(file_path, 'rb') as f:
            file_data = f.read()
            file_hash = hashlib.sha256(file_data).hexdigest()

        return {
            "path": str(file_path),
            "size": file_size,
            "hash": file_hash
        }