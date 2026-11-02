"""Generate reproducible synthetic attendance data; no personal data is used."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def generate_attendance(output: Path, people: int = 360, days: int = 90, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    start = pd.Timestamp("2026-01-05")
    rows = []
    departments = ["Computing", "Business", "Science", "Arts", "Operations"]
    campuses = ["North", "Central", "West"]
    for i in range(people):
        kind = "student" if i < int(people * 0.82) else "staff"
        pid = f"{'STU' if kind == 'student' else 'STF'}-{i + 1:04d}"
        dept, campus = str(rng.choice(departments)), str(rng.choice(campuses))
        faculty = f"FAC-{rng.integers(1, 35):03d}"
        course = f"CRS-{rng.integers(1, 80):03d}" if kind == "student" else "STAFF-DUTY"
        reliability = float(np.clip(rng.beta(5, 2), .18, .99))
        engagement_base = float(np.clip(25 + reliability * 68 + rng.normal(0, 8), 5, 100))
        for day in range(days):
            date = start + pd.Timedelta(days=day)
            if date.weekday() >= 5:
                continue
            scheduled = int(rng.integers(2, 6) if kind == "student" else rng.integers(1, 5))
            tendency = float(np.clip(reliability + .08*np.sin(day/11) + rng.normal(0, .07), .08, .995))
            attended = int(rng.binomial(scheduled, tendency))
            late = int(rng.binomial(attended, .12 + (1-reliability)*.28)) if attended else 0
            engagement = float(np.clip(engagement_base + rng.normal(0, 12) - (scheduled-attended)*3.2, 0, 100))
            submissions = int(rng.binomial(5, np.clip(.12+engagement/120, .05, .98))) if kind == "student" else int(rng.binomial(5, .88))
            future_p = float(np.clip(.12 + (1-tendency)*.65 + (100-engagement)/350, .04, .92))
            rows.append({"person_id":pid,"person_type":kind,"date":date.date().isoformat(),
                "department":dept,"campus":campus,"course_id":course,"faculty_id":faculty,
                "scheduled_sessions":scheduled,"attended_sessions":attended,"late_sessions":late,
                "engagement_score":round(engagement,2),"assignment_submissions":submissions,
                "future_absence_days":int(rng.binomial(7,future_p))})
    result = pd.DataFrame(rows)
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output,index=False)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=ROOT/"data/raw/attendance_events.csv")
    parser.add_argument("--people",type=int,default=360)
    parser.add_argument("--days",type=int,default=90)
    parser.add_argument("--seed",type=int,default=42)
    args=parser.parse_args()
    frame=generate_attendance(args.output,args.people,args.days,args.seed)
    print(f"Generated {len(frame):,} synthetic daily records at {args.output}")

if __name__=="__main__":
    main()