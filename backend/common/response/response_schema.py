#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Any

from fastapi import Response
from pydantic import BaseModel, ConfigDict

from backend.common.response.response_code import CustomResponse, CustomResponseCode
# from core.conf import settings
# from utils.serializers import MsgSpecJSONResponse

# CustomResponseCode：自定义状态码枚举（基于之前的实现）
# settings：项目配置（包含日期时间格式）
# MsgSpecJSONResponse：自定义JSON响应序列化器
from starlette.responses import JSONResponse
import json

_ExcludeData = set[int | str] | dict[int | str, Any]

__all__ = ['ResponseModel', 'response_base']

# 把日期时间格式和序列化器直接放在响应模型中，避免多处配置
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'  # 日期时间格式

class MsgSpecJSONResponse(JSONResponse):
    """
    JSON response using the high-performance msgspec library to serialize data to JSON.
    """

    def render(self, content: Any) -> bytes:
        return json.encode(content)


# 响应模型 ResponseModel
class ResponseModel(BaseModel):
    """
    统一返回模型

    E.g. ::

        @router.get('/test', response_model=ResponseModel)
        def test():
            return ResponseModel(data={'test': 'test'})


        @router.get('/test')
        def test() -> ResponseModel:
            return ResponseModel(data={'test': 'test'})


        @router.get('/test')
        def test() -> ResponseModel:
            res = CustomResponseCode.HTTP_200
            return ResponseModel(code=res.code, msg=res.msg, data={'test': 'test'})
    """

    # TODO: json_encoders 配置失效: https://github.com/tiangolo/fastapi/discussions/10252


    model_config = ConfigDict(json_encoders={datetime: lambda x: x.strftime(DATETIME_FORMAT)})

    code: int = CustomResponseCode.HTTP_200.code
    msg: str = CustomResponseCode.HTTP_200.msg
    data: Any | None = None


class ResponseBase:
    """
    统一返回方法

    .. tip::

        此类中的方法将返回 ResponseModel 模型，作为一种编码风格而存在；

    E.g. ::

        @router.get('/test')
        def test() -> ResponseModel:
            return response_base.success(data={'test': 'test'})
    """

    @staticmethod
    def __response(*, res: CustomResponseCode | CustomResponse = None, data: Any | None = None) -> ResponseModel:
        """
        请求成功返回通用方法

        :param res: 返回信息
        :param data: 返回数据
        :return:
        """
        return ResponseModel(code=res.code, msg=res.msg, data=data)

    def success(
            self,
            *,
            res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_200,
            data: Any | None = None,
    ) -> ResponseModel:
        return self.__response(res=res, data=data)

    def fail(
            self,
            *,
            res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_400,
            data: Any = None,
    ) -> ResponseModel:
        return self.__response(res=res, data=data)

    @staticmethod
    def fast_success(
            *,
            res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_200,
            data: Any | None = None,
    ) -> Response:
        """
        此方法是为了提高接口响应速度而创建的，如果返回数据无需进行 pydantic 解析和验证，则推荐使用，相反，请不要使用！

        .. warning::

            使用此返回方法时，不要指定接口参数 response_model，也不要在接口函数后添加箭头返回类型

        :param res:
        :param data:
        :return:
        """
        return MsgSpecJSONResponse({'code': res.code, 'msg': res.msg, 'data': data})


response_base = ResponseBase()

# 使用API示例：
# @router.get('/user')
# def get_user() -> ResponseModel:
#     user = {'id': 1, 'name': 'John'}
#     return response_base.success(data=user)

# @router.post('/user')
# def create_user() -> ResponseModel:
#     # ...创建逻辑...
#     return response_base.success(res=CustomResponseCode.HTTP_201)

# @router.get('/user/{user_id}')
# def get_user(user_id: int) -> ResponseModel:
#     user = find_user(user_id)
#     if not user:
#         return response_base.fail(res=CustomResponseCode.HTTP_404)
#     return response_base.success(data=user)
