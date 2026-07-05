from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

from app.domain.parser import analyze_code_to_mermaid
from app.infrastructure.database import get_db, AnalysisHistory

router = APIRouter(prefix="/api")

# --- СХЕМЫ ВАЛИДАЦИИ (Pydantic) ---
class CodeRequest(BaseModel):
    code: str

class HistoryResponse(BaseModel):
    id: int
    source_code: str
    mermaid_result: str

    class Config:
        from_attributes = True


# --- СУЩЕСТВУЮЩИЕ ЭНДПОИНТЫ ---

@router.post("/analyze")
def analyze_code(request: CodeRequest, db: Session = Depends(get_db)):
    """Анализ кода из JSON-строки"""
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    
    result_mermaid = analyze_code_to_mermaid(request.code)
    db_history = AnalysisHistory(source_code=request.code, mermaid_result=result_mermaid)
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return {"id": db_history.id, "format": "mermaid", "result": result_mermaid}


# --- НОВЫЙ МОЩНЫЙ ЭНДПОИНТ ДЛЯ ДЛИННЫХ ФАЙЛОВ ---

@router.post("/analyze-file")
async def analyze_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    5. Загрузка файла (File Upload): Принимает целый файл .py, 
    читает его содержимое и строит визуализацию. Подходит для больших кодов.
    """
    # Проверяем, что нам отправляют именно Python файл
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only .py files are allowed")
    
    # Читаем содержимое файла в память (декодируем в текст)
    contents = await file.read()
    source_code = contents.decode("utf-8")
    
    if not source_code.strip():
        raise HTTPException(status_code=400, detail="The uploaded file is empty")
        
    # Запускаем наш парсер
    result_mermaid = analyze_code_to_mermaid(source_code)
    
    # Сохраняем в базу данных историю
    db_history = AnalysisHistory(source_code=source_code, mermaid_result=result_mermaid)
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    
    return {
        "filename": file.filename,
        "id": db_history.id,
        "format": "mermaid",
        "result": result_mermaid
    }


# Остальные GET и DELETE эндпоинты остаются без изменений
@router.get("/history", response_model=List[HistoryResponse])
def get_history(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(AnalysisHistory).offset(skip).limit(limit).all()

@router.get("/history/{history_id}", response_model=HistoryResponse)
def get_history_by_id(history_id: int, db: Session = Depends(get_db)):
    record = db.query(AnalysisHistory).filter(AnalysisHistory.id == history_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Record with ID {history_id} not found")
    return record

@router.delete("/history/{history_id}")
def delete_history_record(history_id: int, db: Session = Depends(get_db)):
    record = db.query(AnalysisHistory).filter(AnalysisHistory.id == history_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Record with ID {history_id} not found")
    db.delete(record)
    db.commit()
    return {"message": f"Record {history_id} successfully deleted"}