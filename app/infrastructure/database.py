from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Указываем, где будет лежать файл нашей базы данных (создастся сам в корне проекта)
DATABASE_URL = "sqlite:///./history.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Описываем таблицу в базе данных
class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, index=True)
    source_code = Column(Text, nullable=False)      # Сюда сохраняем исходный код
    mermaid_result = Column(Text, nullable=False)   # Сюда сохраняем готовую схему

# 3. Функция для автоматического создания таблиц при старте
def init_db():
    Base.metadata.create_all(bind=engine)

# 4. Функция-помощник для получения сессии базы данных (Dependency)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()