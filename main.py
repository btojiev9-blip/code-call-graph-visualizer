from fastapi import FastAPI
from app.api.routes import router as api_router
# Импортируем инициализацию базы данных
from app.infrastructure.database import init_db

app = FastAPI(title="Code Visualizer (Clean Architecture)")

# Запускаем создание базы данных при старте сервера
init_db()

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"status": "working", "message": "Backend with Database is running!"}