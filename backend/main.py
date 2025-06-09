from fastapi import FastAPI

from backend.app.markmanage.api.router import v1 as parent_router
import uvicorn
from fastapi.staticfiles import StaticFiles

# 创建主应用
app = FastAPI(title="ai批改服务平台")

app.mount("/static", StaticFiles(directory="E:/Ai-MarkingMachine/backend/app/markmanage/static"), name="static")

app.include_router(parent_router, prefix="/homework_correction")  # ✅ 正确挂载方式

# 创建一个老师后，就可以运行服务
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8003)
