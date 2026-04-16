"""
QAMini v2 — FastAPI Backend
Statistical Analysis Dashboard with post-analysis QA chat.
"""
from __future__ import annotations

import io
import time
import math
import threading
import numpy as np
import pandas as pd
import faiss
from typing import Optional, Any, Union, List, Dict
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from analyzer import EXPERIMENTS, run_all_experiments
from qa_builder import build_qa_pairs

# ─── App Setup ───────────────────────────────────────────────────

app = FastAPI(title="QAMini v2", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Robust Serialization Helper ────────────────────────────────

def clean_json_data(obj, seen=None):
    """
    Recursively clean data for JSON serialization.
    Optimized for performance and handles numpy/pandas types.
    """
    if seen is None: seen = set()
    
    # Handle basic types quickly
    if obj is None or isinstance(obj, (str, bool, int)):
        return obj
        
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
        
    # Handle numpy/pandas types
    if hasattr(obj, 'tolist'): # numpy arrays, pandas Series
        return clean_json_data(obj.tolist())
    if hasattr(obj, 'item'): # numpy scalars
        val = obj.item()
        return val if not isinstance(val, float) or math.isfinite(val) else None
    
    # Handle lists/tuples
    if isinstance(obj, (list, tuple)):
        return [clean_json_data(v) for v in obj]
        
    # Handle dicts
    if isinstance(obj, dict):
        return {str(k): clean_json_data(v) for k, v in obj.items()}
        
    # Fallback to string representation if still not serializable
    try:
        import json
        json.dumps(obj)
        return obj
    except:
        return str(obj)


# ─── Application State ──────────────────────────────────────────

class AppState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.df: Optional[pd.DataFrame] = None
        self.df_info: dict = {}
        self.model = None
        self.experiment_status: dict[str, str] = {e['id']: 'pending' for e in EXPERIMENTS}
        self.experiment_results: dict[str, Any] = {}
        self.qa_pairs: list[dict[str, str]] = []
        self.qa_embeddings: Optional[np.ndarray] = None
        self.faiss_index = None
        self.analysis_phase: str = 'waiting'  # waiting | analyzing | building_qa | ready
        self.error: Optional[str] = None
        self.upload_filename: Optional[str] = None

state = AppState()

# ─── Lazy model loading ─────────────────────────────────────────

_model_lock = threading.Lock()

def get_model():
    """Lazy-load the sentence transformer model (thread-safe)."""
    with _model_lock:
        if state.model is None:
            print("[QAMini] Loading sentence-transformer model...")
            from sentence_transformers import SentenceTransformer
            state.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("[QAMini] Model loaded.")
        return state.model

# ─── Background Analysis ────────────────────────────────────────

def _run_analysis_background():
    """Run all experiments + build QA index in a background thread."""
    try:
        state.analysis_phase = 'analyzing'
        df = state.df

        def status_cb(exp_id, status, result=None):
            state.experiment_status[exp_id] = status
            if result is not None:
                state.experiment_results[exp_id] = result
            print(f"  [{exp_id}] -> {status}")

        print(f"[QAMini] Running {len(EXPERIMENTS)} experiments...")
        t0 = time.time()
        run_all_experiments(df, status_callback=status_cb)
        elapsed = time.time() - t0
        print(f"[QAMini] All experiments done in {elapsed:.2f}s")

        # Build QA index
        state.analysis_phase = 'building_qa'
        print("[QAMini] Building QA index...")

        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

        df_info = {
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': df.columns.tolist(),
            'numeric_columns': num_cols,
            'categorical_columns': cat_cols,
            'missing_values': int(df.isnull().sum().sum()),
        }
        state.df_info = df_info

        qa_pairs = build_qa_pairs(state.experiment_results, df_info)
        state.qa_pairs = qa_pairs

        if qa_pairs:
            model = get_model()
            questions = [p['question'] for p in qa_pairs]
            embeddings = model.encode(questions, show_progress_bar=False, normalize_embeddings=True)
            state.qa_embeddings = np.array(embeddings).astype('float32')

            dim = state.qa_embeddings.shape[1]
            index = faiss.IndexFlatIP(dim)
            index.add(state.qa_embeddings)
            state.faiss_index = index
            print(f"[QAMini] QA index built: {len(qa_pairs)} pairs, {dim} dims.")

        state.analysis_phase = 'ready'
        print("[QAMini] System ready for chat!")

    except Exception as e:
        state.analysis_phase = 'error'
        state.error = str(e)
        print(f"[QAMini] Error: {e}")
        import traceback
        traceback.print_exc()


# ─── API Models ──────────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: str
    top_k: int = 3

# ─── API Endpoints ───────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "phase": state.analysis_phase}


@app.get("/api/status")
async def get_status():
    """Get current analysis status including per-experiment progress."""
    return {
        "phase": state.analysis_phase,
        "filename": state.upload_filename,
        "experiments": [
            {
                "id": e['id'],
                "num": e['num'],
                "name": e['name'],
                "status": state.experiment_status.get(e['id'], 'pending'),
            }
            for e in EXPERIMENTS
        ],
        "total_experiments": len(EXPERIMENTS),
        "completed": sum(1 for s in state.experiment_status.values() if s == 'done'),
        "chat_ready": state.analysis_phase == 'ready',
        "qa_pairs_count": len(state.qa_pairs),
        "df_info": state.df_info if state.df_info else None,
        "error": state.error,
    }


@app.post("/api/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """Upload CSV and trigger analysis."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "Only CSV files are supported.")

    try:
        content = await file.read()
        # Use more robust parsing options
        df = pd.read_csv(io.BytesIO(content), engine='python', on_bad_lines='skip', encoding_errors='replace')
    except Exception as e:
        raise HTTPException(400, f"Failed to parse CSV: {e}")

    if len(df) < 2:
        raise HTTPException(400, "Dataset must have at least 2 rows.")

    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(num_cols) < 1:
        raise HTTPException(400, "Dataset must have at least 1 numeric column.")

    # Reset state
    state.reset()
    state.df = df
    state.upload_filename = file.filename

    # Start analysis in background
    thread = threading.Thread(target=_run_analysis_background, daemon=True)
    thread.start()

    return {
        "message": f"Dataset '{file.filename}' uploaded successfully.",
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "numeric_columns": num_cols,
        "status": "analyzing",
    }


@app.get("/api/experiment/{exp_id}")
async def get_experiment(exp_id: str):
    """Fetch results for a specific experiment with robust error handling."""
    print(f"[DEBUG] Fetching experiment: {exp_id}")
    try:
        # Check if experiment results exist
        if exp_id not in state.experiment_results:
            status = state.experiment_status.get(exp_id, 'pending')
            print(f"[DEBUG] Result not found for {exp_id}. Status: {status}")
            
            if status in ('running', 'pending'):
                return {"status": status, "results": {}}
            
            # If done but missing, it might be a race condition or a crash
            return {
                "status": "failed",
                "error": f"Results for {exp_id} are unavailable. The analysis might have encountered a memory issue.",
                "results": {}
            }
        
        result = state.experiment_results[exp_id]
        
        # Performance logging for serialization
        t0 = time.time()
        cleaned = clean_json_data(result)
        elapsed = time.time() - t0
        
        if elapsed > 1.0:
            print(f"[WARNING] Slow serialization for {exp_id}: {elapsed:.2f}s")
            
        return cleaned

    except Exception as e:
        print(f"[ERROR] Serialization failed for {exp_id}: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "failed",
            "error": f"Serialization Error: {str(e)}",
            "results": {}
        }


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """Semantic search chat over analysis results."""
    if state.analysis_phase != 'ready':
        raise HTTPException(503, "Analysis not complete. Please wait.")

    if not state.qa_pairs or state.faiss_index is None:
        raise HTTPException(500, "QA index not available.")

    model = get_model()
    t0 = time.time()

    q_embedding = model.encode([req.question], normalize_embeddings=True).astype('float32')
    scores, indices = state.faiss_index.search(q_embedding, min(req.top_k, len(state.qa_pairs)))

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < len(state.qa_pairs):
            pair = state.qa_pairs[idx]
            results.append({
                'answer': pair['answer'],
                'matched_question': pair['question'],
                'similarity': round(float(score) * 100, 1),
            })

    elapsed = time.time() - t0
    return {
        "results": results,
        "processing_time": round(elapsed, 4),
        "query": req.question,
    }
