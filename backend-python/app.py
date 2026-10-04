from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil
import os
import json
import re
from pathlib import Path
from datetime import datetime

from database import init_db, save_episode
from fact_extractor import extract_facts_from_pdf
from rule_engine import evaluate_quality, get_rules_for_diagnosis

app = FastAPI(title="Quality Checker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

init_db()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def extract_diagnosis_from_text(text: str) -> str:
    icd_pattern = r'([A-Z]\d{2}\.\d+)'
    match = re.search(icd_pattern, text)
    if match:
        return match.group(1).upper()
    
    keywords = {
        "I21": ["инфаркт миокарда", "импst", "острый коронарный", "стентирование", "чкв"],
        "I50": ["сердечная недостаточность", "хсн", "застойная сердечная"],
        "I10": ["гипертоническая болезнь", "артериальная гипертензия", "гипертония"],
        "E11": ["сахарный диабет 2 типа", "сд 2 типа", "диабет 2"],
        "I48": ["фибрилляция предсердий", "мерцательная аритмия", "фп"],
        "I20": ["стенокардия", "ишемическая болезнь", "ибс"]
    }
    
    for code, words in keywords.items():
        for word in words:
            if word in text.lower():
                return code
    
    return "I21" # Дефолтный диагноз, если ничего не нашли


def load_rules_by_diagnosis(diagnosis_code: str):
    """
    Загружает ВСЕ правила из одного файла и использует умный поиск 
    (точное совпадение или родительский код).
    """
    rules_path = Path(__file__).parent / "rules.json"
    
    if not rules_path.exists():
        print(f" Файл rules.json не найден! Используются резервные правила.")
        return get_fallback_rules()
    
    try:
        with open(rules_path, "r", encoding="utf-8") as f:
            all_rules_data = json.load(f)
        
        rules = get_rules_for_diagnosis(all_rules_data, diagnosis_code)
        
        if not rules:
             print(f" Правила для {diagnosis_code} не найдены даже в родительских категориях.")
             return get_fallback_rules()
             
        return rules

    except Exception as e:
        print(f" Ошибка загрузки правил: {e}")
        return get_fallback_rules()


def get_fallback_rules():
    return [
        {"drug": "Ацетилсалициловая кислота", "dosage": "75-100 мг/сут", "condition": "", "category": "antiplatelet", "required": True},
        {"drug": "Аторвастатин", "dosage": "40-80 мг/сут", "condition": "", "category": "statin", "required": True},
    ]


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.post("/check_epicrisis")
async def check_epicrisis(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files are supported")
    
    filepath = UPLOAD_DIR / f"{datetime.now().timestamp()}_{file.filename}"
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        import fitz
        doc = fitz.open(str(filepath))
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        
        diagnosis = extract_diagnosis_from_text(text)
        print(f" Определён диагноз: {diagnosis}")
        
        facts = extract_facts_from_pdf(str(filepath))
        print(f" Фактов найдено: {len(facts)}")
        
        # Загружаем правила с учетом родительских кодов
        rules = load_rules_by_diagnosis(diagnosis)
        print(f"Загружено {len(rules)} правил для проверки")
        
        results, quality_score = evaluate_quality(rules, facts)
        print(f"Результатов: {len(results)}, качество: {quality_score}%")
        
        episode_id = save_episode(file.filename, facts, quality_score)
        
        return JSONResponse({
            "episode_id": episode_id,
            "quality_score": round(quality_score, 1),
            "results": results,
            "extracted_facts": facts[:20], 
            "diagnosis": diagnosis
        })
    except Exception as e:
        print(f"ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "results": [], "quality_score": 0}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)