from fastapi import FastAPI
from app.routers import user_route, project_route, document_route
from app.database import Base, engine

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(user_route.router)
app.include_router(project_route.router)
app.include_router(project_route.router_project)
app.include_router(document_route.router)
