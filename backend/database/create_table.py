# create_table.py
import asyncio
import logging
from backend.database.engine import async_engine, async_db_session
from backend.database.base import Base
from backend.app.markmanage.models.user import User
from backend.app.markmanage.models.exam import Exam
from backend.app.markmanage.models.paper import Paper

# 导入所有模型以注册到Base.metadata
from sqlalchemy import inspect

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("create-table")

# 数据库URL
DATABASE_URL = "mysql+asyncmy://root:123456@localhost/exam"


def inspect_table_structure(connection):
    """检查表结构的方法"""
    inspector = inspect(connection)
    created_tables = inspector.get_table_names()

    for table_name in created_tables:
        logger.info(f"表名: {table_name}")

        # 获取表的所有列信息
        columns = inspector.get_columns(table_name)
        for col in columns:
            logger.info(f"  - 列名: {col['name']}")
            logger.info(f"    类型: {col['type']}")
            logger.info(f"    是否为主键: {'是' if col['primary_key'] else '否'}")
            logger.info(f"    可为空: {'是' if col['nullable'] else '否'}")
            logger.info(f"    默认值: {col['default'] or '无'}")

        # 获取主键信息
        primary_key = inspector.get_pk_constraint(table_name)
        if primary_key['constrained_columns']:
            logger.info(f"  - 主键: {', '.join(primary_key['constrained_columns'])}")

        # 获取索引信息
        indexes = inspector.get_indexes(table_name)
        for idx in indexes:
            logger.info(f"  - 索引: {idx['name']}")
            logger.info(f"    包含列: {', '.join(idx['column_names'])}")
            logger.info(f"    是否唯一: {'是' if idx['unique'] else '否'}")

        # 获取外键信息
        foreign_keys = inspector.get_foreign_keys(table_name)
        for fk in foreign_keys:
            logger.info(f"  - 外键: {fk['name']}")
            logger.info(f"    从表列: {', '.join(fk['constrained_columns'])}")
            logger.info(f"    引用表: {fk['referred_table']}")
            logger.info(f"    引用列: {', '.join(fk['referred_columns'])}")

        logger.info("\n")

async def create_tables():
    """创建所有注册的表"""
    try:
        # 1. 创建数据库引擎


        # 2. 打印模型表
        table_names = [table.name for table in Base.metadata.sorted_tables]
        logger.info("准备创建的表: %s", table_names)

        if not table_names:
            logger.error("❌ 没有注册的表定义")
            return False

        # 3. 创建表
        async with async_engine.begin() as conn:
            # 创建表
            logger.info("执行表创建...")

            def sync_create_all(connection):
                Base.metadata.create_all(connection, checkfirst=True)

            await conn.run_sync(sync_create_all)
            logger.info('✅ 表创建完成')

            # 4. 验证表是否存在
            def sync_get_table_names(connection):
                return inspect(connection).get_table_names()

            created_tables = await conn.run_sync(sync_get_table_names)
            logger.info("数据库中的表: %s", created_tables)

            # 5. 检查缺失的表
            missing = [t for t in table_names if t not in created_tables]
            if missing:
                logger.error("❌ 以下表未创建成功: %s", missing)
                return False

            # 6. 输出表结构 - 使用元数据反射方法
            def reflect_table_structure(connection):
                """使用元数据反射检查表结构"""
                from sqlalchemy import MetaData
                metadata = MetaData()
                metadata.reflect(connection)

                for table_name, table_obj in metadata.tables.items():
                    logger.info(f"表结构: {table_name}")
                    for column in table_obj.columns:
                        logger.info(f"  - {column.name}: {column.type}")

            await conn.run_sync(reflect_table_structure)

            return True

    except Exception as e:
        logger.exception("❌ 表创建失败: %s", e)
        return False

if __name__ == "__main__":
    logger.info("======= 开始数据库表创建 =======")

    # 运行异步任务
    loop = asyncio.get_event_loop()

    try:
        result = loop.run_until_complete(create_tables())
        if result:
            logger.info("🎉 数据库表创建成功！")
        else:
            logger.error("💥 数据库表创建失败！")
    except KeyboardInterrupt:
        logger.info("操作被用户中断")
    finally:
        loop.close()
        logger.info("======= 程序结束 =======")