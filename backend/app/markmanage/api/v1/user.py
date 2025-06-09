# user的接口

from backend.app.markmanage.service.user_service import user_service

from fastapi import APIRouter
from backend.app.markmanage.schema.user import UserResponse
from backend.common.response.response_code import CustomResponse
from backend.common.response.response_schema import response_base
from backend.common.exception import errors

router = APIRouter()


@router.post("/users")
async def create_user(username: str, password: str, role: str, full_name: str = None, email: str = None):
    try:
        user_id = await user_service.create_user(username, password, role, full_name, email)
        return response_base.success(data={"user_id": user_id})
    # 捕获服务层抛出的自定义的错误
    except errors.RequestError as e:
        # 接受到自定义的错误，返回自定义的错误信息，相当于自定义了错误码和错误信息，也就是程的自定义错误类：CustomErrorCode。
        # 因为程的错误类不被fail接受，fail接受的是CustomResponseCode或CustomResponse，与之对应的关系为兄弟关系，所以直接使用自定义响应信息类CustomResponse即可
        # res = CustomResponseCode.HTTP_400
        CustomResponse.code = e.code
        CustomResponse.msg = e.msg
        return response_base.fail(res=CustomResponse)

        # 也可直接使用标准的错误码和信息
        # return response_base.fail(res=CustomResponseCode.HTTP_400)


@router.get("/users/{user_id}")
async def get_user_by_id(user_id: int):
    try:
        user = await user_service.get_user(user_id)
        data = UserResponse.from_orm(user)
        return response_base.success(data=data)
    except errors.NotFoundError as e:
        CustomResponse.code = e.code
        CustomResponse.msg = e.msg
        return response_base.fail(res=CustomResponse)


@router.get("/users/username/{username}")
async def get_user_by_username(username: str):
    try:
        user = await user_service.get_user_by_username(username)
        data = UserResponse.from_orm(user)
        return response_base.success(data=data)
    except errors.NotFoundError as e:
        CustomResponse.code = e.code
        CustomResponse.msg = e.msg
        return response_base.fail(res=CustomResponse)


@router.put("/users/{user_id}")
async def update_user(user_id: int, update_data: dict):
    try:
        await user_service.update_user(user_id, update_data)
        # if user is None:
        #     return response_base.fail(res=CustomResponseCode.HTTP_404)
        return response_base.success()
    except errors.NotFoundError as e:
        CustomResponse.code = e.code
        CustomResponse.msg = e.msg
        return response_base.fail(res=CustomResponse)


@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    try:
        user_id = await user_service.delete_user(user_id)
        data = {"user_id": user_id}
        return response_base.success(data=data)
    except errors.NotFoundError as e:
        CustomResponse.code = e.code
        CustomResponse.msg = e.msg
        return response_base.fail(res=CustomResponse)


@router.get("/users")
async def list_users(role: str = None, limit: int = 100, offset: int = 0):
    users = await user_service.list_users(role, limit, offset)
    if not users:
        return response_base.success(data=[])
    data = [UserResponse.from_orm(user) for user in users]
    return response_base.success(data=data)
