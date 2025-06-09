from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class UserResponse(BaseModel):
    # 返回的信息应该包含用户的基本信息，如ID、用户名、邮箱、姓名、角色等
    # 但是为了防止信息泄露，不应该返回密码等敏感信息
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: Optional[str] = Field(..., description="邮箱")
    full_name: Optional[str] = Field(None, description="姓名")
    role: str = Field(..., description="角色")


# class CreateUser(UserResponse):
#     pass

# class UpdateUser(BaseModel):
#     username: Optional[str] = Field(None, description="用户名")
#     email: Optional[str] = Field(None, description="邮箱")
#     full_name: Optional[str] = Field(None, description="姓名")
#     role: Optional[str] = Field(None, description="角色")
#
#
# class getUser(BaseModel):
#     id: int = Field(..., description="用户ID")
#     username: str = Field(..., description="用户名")
#     email: str = Field(..., description="邮箱")
#     full_name: str = Field(None, description="姓名")
#     role: str = Field(..., description="角色")
#
# class getUserList(BaseModel):
#     items: list[getUser] = Field(..., description="用户列表")