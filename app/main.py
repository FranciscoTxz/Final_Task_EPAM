from fastapi import FastAPI
from app.routers import user_route, project_route, document_route
from app.database import Base, engine
from app.config import (
    use_sql_init,
    create_users_table,
    create_projects_table,
    create_documents_table,
    create_users_projects_table,
)
from sqlalchemy import text

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    if not use_sql_init():
        print("Creating db with ORM")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return
    async with engine.begin() as conn:
        print("Creating db with SQL")
        await conn.execute(text(create_users_table))
        await conn.execute(text(create_projects_table))
        await conn.execute(text(create_documents_table))
        await conn.execute(text(create_users_projects_table))


app.include_router(user_route.router)
app.include_router(project_route.router)
app.include_router(project_route.router_project)
app.include_router(document_route.router)
