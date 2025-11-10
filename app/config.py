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


create_users_table = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    password VARCHAR NOT NULL
);
"""

create_projects_table = """
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


create_documents_table = """
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    url VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    project_id INTEGER NOT NULL,
    CONSTRAINT fk_project
        FOREIGN KEY(project_id)
        REFERENCES projects(id)
        ON DELETE CASCADE
);
"""


create_users_projects_table = """
CREATE TABLE IF NOT EXISTS users_projects (
    user_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    is_owner BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (user_id, project_id),
    CONSTRAINT fk_user
        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_project
        FOREIGN KEY(project_id)
        REFERENCES projects(id)
        ON DELETE CASCADE
);
"""
