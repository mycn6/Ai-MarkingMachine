from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from datetime import datetime

from backend.app.markmanage.schema.exam import ExamBase
from backend.app.markmanage.service.exam_service import exam_service
from backend.common.exception import errors
from backend.common.response.response_code import CustomResponse
from backend.common.response.response_schema import response_base

router = APIRouter()


@router.post("/create_exam")
async def create_exam_with_files(
        title: str = Form(...),
        subject: str = Form(...),
        description: str = Form("考试描述"),
        time: datetime = Form(...),
        #   设置默认值
        creator_id: int = Form(1),
        # answers_file: UploadFile = File(...),
        questions_file: UploadFile = File(...),
):
    """创建考试记录并上传相关文件"""
    try:
        exam_id = await exam_service.create_exam(
            title=title,
            subject=subject,
            description=description,
            time=time,
            creator_id=creator_id,
            # answers_file=answers_file,
            questions_file=questions_file,
        )
        return response_base.success(data={"exam_id": exam_id})
    except errors.InvalidFileName as e:
        CustomResponse.code = e.code
        CustomResponse.msg = e.msg
        return response_base.fail(res=CustomResponse)
    except errors.RequestError as e:
        CustomResponse.code = e.code
        CustomResponse.msg = e.msg
        return response_base.fail(res=CustomResponse)
    except errors.ServerError as e:
        CustomResponse.code = e.code
        CustomResponse.msg = e.msg
        return response_base.fail(res=CustomResponse)


@router.put("/update_exam/{exam_id}/files")
async def update_exam_files(
        exam_id: int,
        # answers_file: UploadFile = File(None),
        questions_file: UploadFile = File(None),
):
    """更新考试的文件"""
    try:
        # if not answers_file and not questions_file:
        #     raise errors.RequestError(msg='请上传答案或题目文件')
        #
        # await exam_service.update_exam_files(
        #     exam_id=exam_id,
        #     answers_file=answers_file,
        #     questions_file=questions_file
        # )
        if not questions_file:
            raise errors.RequestError(msg='请上传题目文件')
        await exam_service.update_exam_files(
            exam_id=exam_id,
            questions_file=questions_file
        )
        return response_base.success()

    except errors.NotFoundError as e:
        CustomResponse.code = e.code
        CustomResponse.msg = e.msg
        return response_base.fail(res=CustomResponse)
    except errors.RequestError as e:
        CustomResponse.code = e.code
        CustomResponse.msg = e.msg
        return response_base.fail(res=CustomResponse)


@router.get("/get_exam/{exam_id}")
async def get_exam(
        exam_id: int,
):
    """获取考试详情"""
    try:
        exam = await exam_service.get_exam_by_id(exam_id)
        data = ExamBase.from_orm(exam)
        return response_base.success(data=data)
    except errors.NotFoundError as e:
        CustomResponse.code = e.code
        CustomResponse.msg = e.msg
        return response_base.fail(res=CustomResponse)


@router.get("/get_exams")
async def list_exams(
        skip: int = 0,
        limit: int = 100,
):
    """获取考试列表"""
    exams = await exam_service.list_exams(skip, limit)
    if not exams:
        return response_base.success(data=[])
    data = [ExamBase.from_orm(exam) for exam in exams]
    return response_base.success(data=data)


@router.delete("/delete_exams/{exam_id}")
async def delete_exam(
        exam_id: int,
):
    """删除考试及其相关文件"""
    try:
        await exam_service.delete_exam_files(exam_id)
        data = {"user_id": exam_id}
        return response_base.success(data=data)

    except errors.NotFoundError as e:
        CustomResponse.code = e.code
        CustomResponse.msg = e.msg
        return response_base.fail(res=CustomResponse)
    except errors.ServerError as e:
        CustomResponse.code = e.code
        CustomResponse.msg = e.msg
        return response_base.fail(res=CustomResponse)


# 获取 获取文件路径和原始文件名
@router.get("/get_exam_file_path/{exam_id}/files/{file_type}/path")
async def get_exam_file_path(
        exam_id: int,
        # file_type: str,
):
    """获取考试文件路径"""
    try:
        # file_path, file_name = await exam_service.get_file_path(exam_id, file_type)
        file_path, file_name = await exam_service.get_file_path(exam_id)
        if not file_path or not file_name:
            raise errors.NotFoundError(msg='文件不存在')
        data = {"file_path": file_path, "file_name": file_name}
        return response_base.success(data=data)
    except errors.NotFoundError as e:
        CustomResponse.code = e.code
        CustomResponse.msg = e.msg
        return response_base.fail(res=CustomResponse)
    except errors.RequestError as e:
        CustomResponse.code = e.code
        CustomResponse.msg = e.msg
        return response_base.fail(res=CustomResponse)
