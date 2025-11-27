import os
from datetime import datetime

from flask import send_file
from sqlalchemy import inspect, text

from manager.db_manager import get_session, db_manager
from utils import ResponseFactory
from utils.basic.logging_utils import get_logger
from utils.file_utils import get_images_dir, get_app_dir

UPLOAD_FILE_DIR = os.path.join(get_app_dir(), "upload")
os.makedirs(UPLOAD_FILE_DIR, exist_ok=True)


logger = get_logger(__name__)

# 下载数据库文件
def download_sql():
    """使用 SQLAlchemy 导出所有表数据到 SQL 文件"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    sql_file = os.path.join(UPLOAD_FILE_DIR, f"backup_{timestamp}.sql")

    with get_session() as db:
        inspector = inspect(db_manager.engine)
        tables = inspector.get_table_names()

        with open(sql_file, "w", encoding="utf-8") as f:
            for table in tables:
                f.write(f"-- Table {table}\n")
                result = db.execute(text(f"SELECT * FROM {table}"))
                for row in result.mappings():  # 使用字典访问列
                    cols = row.keys()
                    values = []
                    for col in cols:
                        val = row[col]
                        if val is None:
                            values.append("NULL")
                        else:
                            values.append(f"'{str(val).replace('\'', '\\\'')}'")
                    f.write(f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join(values)});\n")

        logger.info("下载数据库")
        return send_file(
            sql_file,
            mimetype="application/sql",
            as_attachment=True,
            download_name=os.path.basename(sql_file)
        )

# 导入数据库文件
def import_sql(file):
    sql_text = file.read().decode("utf-8")

    delete_and_create_tables()

    with get_session() as db:
        try:
            statement = ""

            for line in sql_text.splitlines():
                stripped = line.strip()

                # 安全检查
                if not is_safe_sql(stripped):
                    logger.error(f"导入数据库文件失败: {stripped} 不安全")
                    return ResponseFactory.error(data={
                        "message": "setting.fileManager.message.importSqlFailed",
                        "messageType": "error"
                    }).to_response()

                # 跳过注释和空行
                if not stripped or stripped.startswith("--") or stripped.startswith("#"):
                    continue

                # 累积 SQL 直到遇到分号
                statement += " " + stripped

                if stripped.endswith(";"):
                    # 执行完整 SQL 语句
                    db.execute(text(statement[:-1]))  # 去掉最后的分号
                    statement = ""  # 重置继续下一条

            fix_all_sequences(db)

            db.commit()
            logger.info(f"导入数据库文件完成: {file.filename}")
            return ResponseFactory.success(data={
                "message": "setting.fileManager.message.importSqlSuccess",
                "messageType": "success"
            }).to_response()
        except Exception as e:
            db.rollback()
            logger.error(f"导入数据库文件失败: {e}")
            return ResponseFactory.error(data={
                "message": "setting.fileManager.message.importSqlFailed",
                "messageType": "error"
            }).to_response()


# 删除表和创建表
def delete_and_create_tables():
    with get_session() as db:
        db.execute(text("DROP TABLE IF EXISTS pics"))
        db.execute(text("DROP TABLE IF EXISTS albums"))
        db.execute(text("DROP TABLE IF EXISTS tokens"))
        db.execute(text("DROP TABLE IF EXISTS configs"))
        db.commit()

        db_manager.create_tables()


# 防止 SQL
import re

DANGEROUS_PATTERNS = [
    r"\bDROP\b",
    r"\bDELETE\b",
    r"\bTRUNCATE\b",
    r"\bUPDATE\b",
    r"\bALTER\b",
    r"\bCREATE\b",
    r"\bREPLACE\b",
]


def is_safe_sql(sql_line: str) -> bool:
    line = sql_line.strip().upper()

    # 跳过空行
    if not line:
        return True

    # 跳过注释
    if line.startswith("--") or line.startswith("/*"):
        return True

    # 必须为 INSERT INTO 开头
    if not line.startswith("INSERT INTO"):
        return False

    # 禁止危险 SQL
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            return False

    return True

def get_db_type(db):
    name = db.bind.dialect.name  # 'postgresql' 或 'mysql'
    return name

def get_pk_tables_and_columns(db):
    inspector = inspect(db.bind)
    tables = inspector.get_table_names()

    result = []
    for table in tables:
        pks = inspector.get_pk_constraint(table)
        if pks and pks.get("constrained_columns"):
            # 默认只处理单主键
            pk_col = pks["constrained_columns"][0]
            result.append((table, pk_col))
    return result

def fix_pg_sequence(db, table, pk):
    sql = f"""
        SELECT setval(
            pg_get_serial_sequence('{table}', '{pk}'),
            COALESCE((SELECT MAX({pk}) FROM {table}), 0) + 1,
            false
        );
    """
    db.execute(text(sql))

def fix_mysql_autoincrement(db, table, pk):
    sql = f"SELECT MAX({pk}) + 1 AS next_id FROM {table};"
    next_id = db.execute(text(sql)).scalar()
    next_id = next_id if next_id else 1

    db.execute(text(f"ALTER TABLE {table} AUTO_INCREMENT = {next_id};"))

def fix_all_sequences(db):
    db_type = get_db_type(db)
    pk_tables = get_pk_tables_and_columns(db)

    for table, pk in pk_tables:
        if db_type == "postgresql":
            fix_pg_sequence(db, table, pk)
        elif db_type == "mysql":
            fix_mysql_autoincrement(db, table, pk)