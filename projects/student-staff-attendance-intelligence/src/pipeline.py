"""Validate, transform, feature-engineer and publish attendance data."""
from __future__ import annotations
import argparse, os
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
REQUIRED={"person_id","person_type","date","department","campus","course_id","faculty_id",
"scheduled_sessions","attended_sessions","late_sessions","engagement_score","assignment_submissions","future_absence_days"}

def transform_attendance(source:Path, output_dir:Path)->dict[str,pd.DataFrame]:
    raw=pd.read_csv(source)
    missing=REQUIRED.difference(raw.columns)
    if missing: raise ValueError(f"Input is missing required columns: {sorted(missing)}")
    frame=raw.copy()
    frame["date"]=pd.to_datetime(frame["date"],errors="coerce")
    numeric=["scheduled_sessions","attended_sessions","late_sessions","engagement_score","assignment_submissions","future_absence_days"]
    for col in numeric: frame[col]=pd.to_numeric(frame[col],errors="coerce")
    valid=(frame.person_id.notna() & frame.date.notna() & frame.person_type.isin(["student","staff"])
        & frame.scheduled_sessions.gt(0) & frame.attended_sessions.ge(0)
        & frame.attended_sessions.le(frame.scheduled_sessions) & frame.late_sessions.ge(0)
        & frame.late_sessions.le(frame.attended_sessions) & frame.engagement_score.between(0,100)
        & frame.assignment_submissions.between(0,5) & frame.future_absence_days.between(0,7))
    rejected=frame.loc[~valid].copy()
    clean=frame.loc[valid].drop_duplicates(["person_id","date"],keep="last").copy()
    clean=clean.sort_values(["person_id","date"]).reset_index(drop=True)
    clean["daily_attendance_rate"]=clean.attended_sessions/clean.scheduled_sessions
    clean["daily_late_rate"]=clean.late_sessions/clean.scheduled_sessions
    groups=clean.groupby("person_id",sort=False)
    clean["attendance_rate_7d"]=groups.daily_attendance_rate.transform(lambda s:s.rolling(7,min_periods=1).mean())
    clean["late_rate_7d"]=groups.daily_late_rate.transform(lambda s:s.rolling(7,min_periods=1).mean())
    clean["engagement_7d"]=groups.engagement_score.transform(lambda s:s.rolling(7,min_periods=1).mean())
    clean["at_risk"]=(clean.future_absence_days>=4).astype("int8")
    clean["day_of_week"]=clean.date.dt.dayofweek
    clean=clean.drop(columns=["future_absence_days"])
    output_dir.mkdir(parents=True,exist_ok=True)
    clean["date"]=clean.date.dt.strftime("%Y-%m-%d")
    clean.to_csv(output_dir/"person_features.csv",index=False)
    rejected.to_csv(output_dir/"rejected_records.csv",index=False)
    daily=clean.groupby(["date","person_type"],as_index=False).agg(
        people_present=("person_id","nunique"),scheduled_sessions=("scheduled_sessions","sum"),
        attended_sessions=("attended_sessions","sum"),average_engagement=("engagement_score","mean"),risk_cases=("at_risk","sum"))
    daily["attendance_rate"]=daily.attended_sessions/daily.scheduled_sessions
    daily.to_csv(output_dir/"daily_summary.csv",index=False)
    dept=clean.groupby(["department","person_type"],as_index=False).agg(
        people=("person_id","nunique"),scheduled_sessions=("scheduled_sessions","sum"),
        attended_sessions=("attended_sessions","sum"),average_engagement=("engagement_score","mean"),risk_cases=("at_risk","sum"))
    dept["attendance_rate"]=dept.attended_sessions/dept.scheduled_sessions
    dept["risk_rate"]=dept.risk_cases/dept.people.clip(lower=1)
    dept.to_csv(output_dir/"department_summary.csv",index=False)
    clean.sort_values("date").groupby("person_id",as_index=False).tail(1).to_csv(output_dir/"latest_person_features.csv",index=False)
    db=os.getenv("DATABASE_URL")
    if db:
        from sqlalchemy import create_engine
        engine=create_engine(db,pool_pre_ping=True)
        clean.to_sql("attendance_features",engine,if_exists="replace",index=False,chunksize=2000)
        daily.to_sql("daily_attendance_summary",engine,if_exists="replace",index=False)
        dept.to_sql("department_attendance_summary",engine,if_exists="replace",index=False)
        engine.dispose()
    bucket=os.getenv("S3_BUCKET")
    if bucket:
        import boto3
        client=boto3.client("s3",endpoint_url=os.getenv("S3_ENDPOINT_URL") or None,region_name=os.getenv("AWS_DEFAULT_REGION","us-east-1"))
        for name in ["person_features.csv","daily_summary.csv","department_summary.csv","rejected_records.csv"]:
            client.upload_file(str(output_dir/name),bucket,f"processed/{name}")
    return {"features":clean,"daily":daily,"department":dept,"rejected":rejected}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,default=ROOT/"data/raw/attendance_events.csv")
    parser.add_argument("--output-dir",type=Path,default=ROOT/"data/processed")
    args=parser.parse_args()
    if not args.input.exists(): raise FileNotFoundError(f"{args.input} not found. Run: python src/generate_data.py")
    result=transform_attendance(args.input,args.output_dir)
    print(f"Curated {len(result['features']):,} rows; rejected {len(result['rejected']):,} rows.")
    print(f"Outputs written to {args.output_dir}")

if __name__=="__main__":
    main()