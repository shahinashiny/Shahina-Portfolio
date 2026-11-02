# Power BI report build guide

Connect Power BI Desktop to the CSVs in data/processed/ or to the PostgreSQL tables created by the pipeline.

Suggested pages:
1. Executive overview: attendance rate, scheduled sessions, people represented, and risk count.
2. Attendance trends: daily attendance by student/staff, department, and campus.
3. Engagement and risk: risk-band distribution, engagement vs. attendance, and review table of highest risk scores.
4. Data quality: rejected row count, invalid records, and pipeline refresh timestamp.

Example DAX measures (adjust table names after import):

    Attendance Rate = DIVIDE(SUM(daily_summary[attended_sessions]), SUM(daily_summary[scheduled_sessions]))
    Scheduled Sessions = SUM(daily_summary[scheduled_sessions])
    Risk Cases = SUM(daily_summary[risk_cases])
    Average Engagement = AVERAGE(daily_summary[average_engagement])
    Risk Rate = DIVIDE([Risk Cases], DISTINCTCOUNT(risk_predictions[person_id]))

Use date as a date dimension and person_type, department, campus, and risk_band as slicers. Risk scores are demonstration signals for human review, not automated high-stakes decisions. All example data is synthetic.