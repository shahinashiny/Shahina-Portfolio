from pathlib import Path
from src.generate_data import generate_attendance
from src.pipeline import transform_attendance

def test_generate_and_transform_synthetic_data(tmp_path:Path):
    source=tmp_path/"raw.csv"; out=tmp_path/"processed"
    generated=generate_attendance(source,people=20,days=15,seed=7)
    assert len(generated)>0
    result=transform_attendance(source,out)
    assert len(result["features"])>0
    assert set(result["features"]["at_risk"].unique()).issubset({0,1})
    assert (out/"daily_summary.csv").exists()
    assert (out/"department_summary.csv").exists()
    assert (out/"latest_person_features.csv").exists()

def test_invalid_row_is_rejected(tmp_path:Path):
    source=tmp_path/"raw.csv"; out=tmp_path/"processed"
    frame=generate_attendance(source,people=8,days=10,seed=9)
    frame.loc[0,"attended_sessions"]=frame.loc[0,"scheduled_sessions"]+3
    frame.to_csv(source,index=False)
    result=transform_attendance(source,out)
    assert len(result["rejected"])==1