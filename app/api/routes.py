from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.domain.parser import analyze_code_to_mermaid
# Импортируем инструменты базы данных
from app.infrastructure.database import get_db, AnalysisHistory

router = APIRouter(prefix="/api")

class CodeRequest(BaseModel):
    code: str

@router.post("/analyze")
def analyze_code(request: CodeRequest, db: Session = Depends(get_db)):
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    
    # 1. Запускаем анализ
    result_mermaid = analyze_code_to_mermaid(request.code)
    
    # 2. Сохраняем в базу данных историю
    db_history = AnalysisHistory(
        source_code=request.code,
        mermaid_result=result_mermaid
    )
    db.add(db_history)
    db.commit() # Фиксируем изменения в БД
    db.refresh(db_history)
    
    return {
        "id": db_history.id, # Теперь возвращаем еще и ID записи из базы!
        "format": "mermaid",
        "result": result_mermaid
    }