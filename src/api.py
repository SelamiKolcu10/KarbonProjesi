"""
FastAPI Backend API - Belge Yükleme ve İşleme
PDF/Excel/CSV dosyalarını kabul eder, işler ve sonuçları döndürür.
Frontend ve Backend tek port üzerinden çalışır (localhost:8000).
"""

import os
import sys
import re
import json
import importlib.util
import tempfile
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# Proje kökünü Python path'ine ekle
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import Config
from src.pipeline import map_extraction_to_payload
from src.agents.auditor.models import InputPayload
from src.agents.guards import DataQualityGuard
from src.orchestration import Orchestrator, JobStatus

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

orchestrator = Orchestrator()

app = FastAPI(
    title="Karbon Salınımı API",
    description="Belge yükleme ve veri çıkarımı API'si",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_EXTENSIONS = {".pdf", ".xlsx", ".xls", ".csv"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


QUALITY_ERROR_CODES = {
    "Critical Anomaly: Energy consumption detected while production is zero.": "DQ_ZERO_PRODUCTION_ENERGY_CONFLICT",
    "Data Quality Error: Energy intensity per ton is physically improbable. Check your units.": "DQ_EXTREME_ENERGY_INTENSITY",
    "Insufficient Data: A factory must consume at least some energy.": "DQ_MISSING_CORE_ENERGY_DATA",
    "Data Quality Error: cbam_allocation_rate must be strictly between 0.01 and 1.0.": "DQ_INVALID_ALLOCATION_RATE",
}


def _map_quality_errors(errors: List[str]) -> List[Dict[str, Any]]:
    """Convert guard messages to API-friendly error code objects."""
    mapped = []
    for msg in errors:
        mapped.append({
            "code": QUALITY_ERROR_CODES.get(msg, "DQ_VALIDATION_FAILED"),
            "message": msg,
        })
    return mapped


def extract_text_from_pdf_basic(file_path: str) -> dict:
    """pdfplumber ile PDF'den temel metin çıkarımı yapar."""
    try:
        import pdfplumber
    except ImportError:
        raise HTTPException(status_code=500, detail="pdfplumber yüklü değil. 'pip install pdfplumber' çalıştırın.")

    text_pages = []
    tables_found = []
    total_chars = 0

    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text() or ""
            text_pages.append(page_text)
            total_chars += len(page_text)

            # Tablo çıkarımı
            page_tables = page.extract_tables()
            if page_tables:
                for table in page_tables:
                    tables_found.append({
                        "page": i + 1,
                        "rows": len(table),
                        "data": table[:5]  # İlk 5 satır
                    })

    full_text = "\n\n".join(text_pages)
    page_count = len(text_pages)

    # Metin güvenilirliği skoru hesapla
    confidence = calculate_text_confidence(full_text, page_count)

    return {
        "text": full_text[:5000],  # İlk 5000 karakter
        "total_pages": len(text_pages),
        "total_characters": total_chars,
        "tables_found": len(tables_found),
        "tables_preview": tables_found[:3],
        "confidence": confidence,
        "extraction_method": "TEXT_LAYER" if total_chars > 100 else "OCR_NEEDED"
    }


def calculate_text_confidence(text: str, page_count: int) -> float:
    """Metin güvenilirliği skorunu hesaplar (0.0-1.0)."""
    if not text.strip():
        return 0.0

    score = 0.5  # Başlangıç

    # Karakter yoğunluğu (sayfa başına ortalama karakter)
    avg_chars = len(text) / max(page_count, 1)
    if avg_chars > 500:
        score += 0.2
    elif avg_chars > 200:
        score += 0.1

    # Sayısal veri varlığı
    numbers = re.findall(r'\d+[.,]?\d*', text)
    if len(numbers) > 10:
        score += 0.15
    elif len(numbers) > 5:
        score += 0.1

    # Birim varlığı (enerji/yakıt birimleri)
    units = ['MWh', 'kWh', 'ton', 'kg', 'm³', 'm3', 'GJ', 'TJ', 'MJ']
    found_units = sum(1 for u in units if u.lower() in text.lower())
    if found_units >= 3:
        score += 0.15
    elif found_units >= 1:
        score += 0.1

    return min(round(score, 2), 1.0)


def extract_data_from_excel(file_path: str, extension: str) -> dict:
    """Excel/CSV dosyasından veri çıkarır. Türkçe ve İngilizce sütun başlıkları desteklenir."""
    try:
        import pandas as pd
    except ImportError:
        raise HTTPException(status_code=500, detail="pandas yüklü değil. 'pip install pandas' çalıştırın.")

    sheets_data = {}
    column_language = "unknown"

    if extension == ".csv":
        df = pd.read_csv(file_path)
        column_language = detect_column_language(df.columns.tolist())
        sheets_data["Sheet1"] = {
            "columns": df.columns.tolist(),
            "row_count": len(df),
            "preview": json.loads(df.head(10).to_json(orient="records", force_ascii=False)),
            "column_language": column_language,
        }
    else:
        # openpyxl is an optional runtime dependency for xlsx/xls support.
        if importlib.util.find_spec("openpyxl") is None:
            raise HTTPException(status_code=500, detail="openpyxl yüklü değil. 'pip install openpyxl' çalıştırın.")

        xls = pd.ExcelFile(file_path)
        for sheet_name in xls.sheet_names[:5]:  # Maks 5 sayfa
            df = pd.read_excel(xls, sheet_name=sheet_name)
            lang = detect_column_language(df.columns.tolist())
            if lang != "unknown":
                column_language = lang
            sheets_data[sheet_name] = {
                "columns": df.columns.tolist(),
                "row_count": len(df),
                "preview": json.loads(df.head(10).to_json(orient="records", force_ascii=False)),
                "column_language": lang,
            }

    return {
        "sheets": sheets_data,
        "total_sheets": len(sheets_data),
        "column_language": column_language,
    }


def detect_column_language(columns: list) -> str:
    """Sütun başlıklarının dilini tespit eder (Türkçe/İngilizce)."""
    turkish_keywords = [
        "tarih", "miktar", "birim", "tüketim", "üretim", "yakıt", "enerji",
        "dönem", "toplam", "açıklama", "şirket", "tesis", "rapor", "ay",
        "doğalgaz", "kömür", "elektrik", "mazot", "dizel", "buhar",
    ]
    english_keywords = [
        "date", "amount", "unit", "consumption", "production", "fuel", "energy",
        "period", "total", "description", "company", "facility", "report", "month",
        "natural gas", "coal", "electricity", "diesel", "steam",
    ]

    cols_lower = [str(c).lower() for c in columns]
    tr_count = sum(1 for c in cols_lower for kw in turkish_keywords if kw in c)
    en_count = sum(1 for c in cols_lower for kw in english_keywords if kw in c)

    if tr_count > en_count:
        return "Türkçe"
    elif en_count > tr_count:
        return "İngilizce"
    return "unknown"


def try_llm_extraction(text: str) -> Optional[dict]:
    """LLM ile yapılandırılmış veri çıkarımı dener. API key yoksa None döner."""
    try:
        from src.agents.data_extractor import DataExtractor

        api_key = Config.GEMINI_API_KEY or Config.OPENAI_API_KEY
        if not api_key:
            return None

        provider = "gemini" if Config.GEMINI_API_KEY else "gpt"
        extractor = DataExtractor(llm_provider=provider, api_key=api_key)
        result = extractor.extract_with_llm(text[:15000])
        return result
    except Exception as e:
        logger.warning(f"LLM çıkarımı başarısız: {e}")
        return None


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Belge yükler ve işler.
    Desteklenen formatlar: PDF, XLSX, XLS, CSV
    İşlem sonrası dosya güvenli şekilde silinir.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Dosya adı bulunamadı")

    # Uzantı kontrolü
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Desteklenmeyen dosya formatı: {ext}. Desteklenen: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Geçici dosya oluştur
    temp_dir = tempfile.mkdtemp(prefix="karbon_upload_")
    temp_path = os.path.join(temp_dir, file.filename)

    try:
        # Dosyayı kaydet
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Dosya boyutu 50 MB'dan büyük olamaz")

        with open(temp_path, "wb") as f:
            f.write(content)

        logger.info(f"Dosya yüklendi: {file.filename} ({len(content)} bytes)")

        # Dosya tipine göre işle
        result = {
            "filename": file.filename,
            "file_size": len(content),
            "file_type": ext.upper().replace(".", ""),
            "processed_at": datetime.now().isoformat(),
        }

        if ext == ".pdf":
            # PDF işleme
            pdf_data = extract_text_from_pdf_basic(temp_path)
            result["extraction"] = pdf_data

            # LLM ile yapılandırılmış veri çıkarımı dene
            llm_result = try_llm_extraction(pdf_data["text"])
            if llm_result:
                result["structured_data"] = llm_result
                result["extraction_mode"] = "LLM"

                # Business-logic validation (DataQualityGuard) on structured payload
                try:
                    payload = map_extraction_to_payload(llm_result)
                    guard = DataQualityGuard()
                    passed, errors = guard.validate_business_logic(payload)

                    if not passed:
                        raise HTTPException(
                            status_code=422,
                            detail={
                                "error": "DATA_QUALITY_VALIDATION_FAILED",
                                "errors": _map_quality_errors(errors),
                            },
                        )

                    result["data_quality"] = {
                        "passed": True,
                        "errors": [],
                    }
                    # Frontend can submit this directly to orchestrator endpoints.
                    result["structured_payload"] = payload.model_dump(mode="json")
                except HTTPException:
                    raise
                except Exception as e:
                    logger.warning(f"Data quality validation skipped due to mapping/validation error: {e}")
                    result["data_quality"] = {
                        "passed": False,
                        "errors": [
                            {
                                "code": "DQ_VALIDATION_PIPELINE_ERROR",
                                "message": "Data quality validation could not be completed.",
                            }
                        ],
                    }
            else:
                result["extraction_mode"] = "basic"

        elif ext in (".xlsx", ".xls", ".csv"):
            # Excel/CSV işleme
            excel_data = extract_data_from_excel(temp_path, ext)
            result["extraction"] = excel_data
            result["extraction_mode"] = "spreadsheet"

        result["status"] = "success"
        result["file_deleted"] = True  # Dosya silindi bilgisi

        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"İşleme hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Belge işleme hatası: {str(e)}")
    finally:
        # Güvenli dosya silme - her durumda çalışır
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
            logger.info(f"Geçici dosyalar güvenli şekilde silindi: {temp_dir}")
        except Exception:
            pass


@app.get("/api/health")
async def health_check():
    """API sağlık kontrolü."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "pdf_extraction": True,
            "excel_support": True,
            "file_cleanup": True,
        }
    }


@app.post("/api/validate-payload")
async def validate_payload(payload: InputPayload):
    """Validate InputPayload with DataQualityGuard business rules."""
    guard = DataQualityGuard()
    passed, errors = guard.validate_business_logic(payload)

    if not passed:
        return JSONResponse(
            status_code=422,
            content={
                "valid": False,
                "error": "DATA_QUALITY_VALIDATION_FAILED",
                "errors": _map_quality_errors(errors),
            },
        )

    return {
        "valid": True,
        "errors": [],
    }


@app.post("/api/orchestrator/jobs")
async def submit_orchestrator_job(payload: InputPayload, background_tasks: BackgroundTasks):
    """Submit a job to orchestrator and process it asynchronously if accepted."""
    job_id = orchestrator.submit_job(payload)
    job = orchestrator.get_job_status(job_id)

    if job.status == JobStatus.PENDING:
        background_tasks.add_task(orchestrator.process_job, job_id, payload)

    return {
        "job_id": job_id,
        "status": job.status.value,
        "created_at": job.created_at.isoformat(),
        "error_message": job.error_message,
    }


@app.get("/api/orchestrator/jobs/{job_id}")
async def get_orchestrator_job_status(job_id: str):
    """Fetch current status/result for a submitted orchestrator job."""
    try:
        job = orchestrator.get_job_status(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return job.model_dump(mode="json")


@app.post("/api/orchestrator/jobs/{job_id}/process")
async def process_orchestrator_job(job_id: str, payload: InputPayload):
    """Manually process an already-submitted job (MVP helper endpoint)."""
    try:
        orchestrator.get_job_status(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    orchestrator.process_job(job_id, payload)
    job = orchestrator.get_job_status(job_id)
    return job.model_dump(mode="json")


# --- Frontend Static Files (tek port) ---
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"

if FRONTEND_DIST.exists():
    # Frontend build dosyalarını sun (CSS, JS, assets)
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """SPA fallback - tüm route'ları index.html'e yönlendir."""
        file_path = FRONTEND_DIST / full_path
        if full_path and file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(FRONTEND_DIST / "index.html"))
else:
    @app.get("/")
    async def no_frontend():
        return JSONResponse(content={
            "message": "Frontend build bulunamadı. Önce 'cd frontend && npm run build' çalıştırın.",
            "api_docs": "/docs"
        })


if __name__ == "__main__":
    import uvicorn
    print("🚀 Sunucu başlatılıyor: http://localhost:8000")
    print("📄 API Docs: http://localhost:8000/docs")
    if FRONTEND_DIST.exists():
        print("🌐 Frontend: http://localhost:8000")
    else:
        print("⚠️  Frontend build yok. 'cd frontend && npm run build' çalıştırın.")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
