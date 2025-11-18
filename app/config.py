from dotenv import load_dotenv
import os
import sys

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL", "ERROR")
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
INIT_DB_METHOD = os.getenv("INIT_DB_METHOD", "ORM")


def use_sql_init() -> bool:
    """Read variable to create the db with orm or sql"""
    env = INIT_DB_METHOD.lower()
    if env == "sql":
        return True
    for arg in sys.argv:
        if arg.lower().startswith("--init-db="):
            return arg.split("=", 1)[1].lower() == "sql"
    return False
