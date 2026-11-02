"""FastAPI endpoints for attendance summaries and synthetic risk scores."""
from __future__ import annotations
import json,os,subprocess,sys
from pathlib import Path
import pandas as pd
from fastapi import FastAPI,HTTPException,Query
ROOT=Path(__file__).resolve().parents[1]
DATA_DIR=Path(os.getenv("DATA_DIR",ROOT/"data"))
app=FastAPI(title="Attendance Intelligence API",version="1.0.0",description="Synthetic-data demonstration API")

@app.get("/health")
def health(): return {"status":"ok","dataset":"synthetic","service":"attendance-intelligence"}

@app.get("/metrics")
def metrics():
    path=ROOT/"models/metrics.json"
    if not path.exists(): raise HTTPException(404,"Run src/train.py first.")
    return json.loads(path.read_text(encoding="utf-8"))

@app.get("/daily-summary")
def daily_summary():
    path=DATA_DIR/"processed/daily_summary.csv"
    if not path.exists(): raise HTTPException(404,"Run src/pipeline.py first.")
    return pd.read_csv(path).fillna(0).to_dict(orient="records")

@app.get("/risk")
def risk(limit:int=Query(25,ge=1,le=500),person_type:str|None=None):
    path=DATA_DIR/"processed/risk_predictions.csv"
    if not path.exists(): raise HTTPException(404,"Run src/train.py first.")
    frame=pd.read_csv(path).sort_values("risk_probability",ascending=False)
    if person_type:
        if person_type not in {"student","staff"}: raise HTTPException(400,"person_type must be student or staff")
        frame=frame[frame.person_type==person_type]
    return frame.head(limit).fillna("").to_dict(orient="records")

@app.post("/pipeline/run")
def run_pipeline():
    commands=[[sys.executable,str(ROOT/"src/generate_data.py")],
              [sys.executable,str(ROOT/"src/pipeline.py")],
              [sys.executable,str(ROOT/"src/train.py")]]
    for command in commands:
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
        if result.returncode: raise HTTPException(500,result.stderr[-2000:])
    return {"status":"completed","steps":["generate","validate-transform","train-score"],"dataset":"synthetic"}