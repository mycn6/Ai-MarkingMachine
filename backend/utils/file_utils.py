# backend/utils/file_utils.py
import os
import mimetypes
import uuid
from typing import List
from fastapi import UploadFile, File, Form

from backend.common.exception import errors
from backend.config.fileConfig import settings


async def validate_file(
        file: UploadFile = File(...),
        allowed_types: List[str] = Form(...),
        max_size: int = Form(...)
):
    """验证上传文件"""

    # 验证文件大小
    file.file.seek(0, 2)  # 移动到文件末尾
    file_size = file.file.tell()
    file.file.seek(0)  # 重置到文件开头

    if file_size > max_size:
        size_mb = max_size / (1024 * 1024)
        return False, f"文件大小不能超过 {size_mb:.2f}MB"


    # 验证文件类型
    filename = file.filename
    if '.' not in filename:
        return False, f"文件名 {filename} 无效"

    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in allowed_types:
        allowed_exts = ", ".join(allowed_types)
        return False, f"文件扩展名 {ext} 无效，只允许 {allowed_exts} 类型"


    return True, ""
    # 根据文件内容进一步验证
    # TODO: 添加更深入的文件内容验证


async def save_upload_file(upload_file: UploadFile = File(...), upload_dir: str = Form(...)) -> tuple[str, str]:
    """保存上传的文件"""
    # 确保上传目录存在
    os.makedirs(upload_dir, exist_ok=True)

    # 生成唯一的文件名
    # 获取文件扩展名
    file_ext = os.path.splitext(upload_file.filename)[1]
    # 生成唯一的文件名
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    # 拼接完整的文件保存路径（目录路径 + 唯一文件名）
    file_path = os.path.join(upload_dir, unique_filename)

    # 保存文件
    try:
        # 使用异步读取文件
        with open(file_path, "wb") as buffer:
            # 分块读取文件
            while chunk := await upload_file.read(settings.CHUNK_SIZE):
                buffer.write(chunk)
    except Exception as e:
        # 如果保存失败，删除可能已创建的文件
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        #     保存失败，返回空值
        return "", ""


    return file_path, upload_file.filename
