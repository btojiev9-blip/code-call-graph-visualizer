from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

from app.domain.parser import analyze_code_to_mermaid
from app.infrastructure.database import get_db, AnalysisHistory

router = APIRouter(prefix="/api")

# --- СХЕМЫ ВАЛИДАЦИИ (Pydantic) ---

class CodeRequest(BaseModel):
    code: str

# Схема для красивого вывода истории (без лишней внутренней кухни базы данных)
class HistoryResponse(BaseModel):
    id: int
    source_code: str
    mermaid_result: str

    class Config:
        from_attributes = True


# --- ЭНДПОИНТЫ (API Routes) ---

@router.post("/analyze")
def analyze_code(request: CodeRequest, db: Session = Depends(get_db)):
    """
    1. Создание (Create): Анализирует код и сохраняет результат в БД.
    """
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    
    result_mermaid = analyze_code_to_mermaid(request.code)
    
    db_history = AnalysisHistory(
        source_code=request.code,
        mermaid_result=result_mermaid
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    
    return {
        "id": db_history.id,
        "format": "mermaid",
        "result": result_mermaid
    }


@router.get("/history", response_model=List[HistoryResponse])
def get_history(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    2. Чтение списка (Read All): Возвращает историю проверок с ПАГИНАЦИЕЙ.
    Защищает базу данных от перегрузки (параметры skip и limit).
    """
    history = db.query(AnalysisHistory).offset(skip).limit(limit).all()
    return history


@router.get("/history/{history_id}", response_model=HistoryResponse)
def get_history_by_id(history_id: int, db: Session = Depends(get_db)):
    """
    3. Чтение одного элемента (Read One): Поиск записи по ID.
    Если запись не найдена — возвращает чистую ошибку 404 Not Found.
    """
    record = db.query(AnalysisHistory).filter(AnalysisHistory.id == history_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Record with ID {history_id} not found")
    return record


@router.delete("/history/{history_id}")
def delete_history_record(history_id: int, db: Session = Depends(get_db)):
    """
    4. Удаление (Delete): Удаляет запись из базы данных по её ID.
    """
    record = db.query(AnalysisHistory).filter(AnalysisHistory.id == history_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Record with ID {history_id} not found")
    
    db.delete(record)
    db.commit()
    return {"message": f"Record {history_id} successfully deleted"}