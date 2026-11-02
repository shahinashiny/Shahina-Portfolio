"""Optional PySpark batch path for distributed validation and rolling features."""
from __future__ import annotations
import argparse
from pathlib import Path
from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F
ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",default=str(ROOT/"data/raw/attendance_events.csv"))
    parser.add_argument("--output",default=str(ROOT/"data/processed/spark_features"))
    args=parser.parse_args()
    spark=SparkSession.builder.appName("attendance-intelligence-batch").getOrCreate()
    try:
        raw=spark.read.option("header",True).option("inferSchema",True).csv(args.input)
        valid=raw.filter(F.col("person_id").isNotNull() & F.col("date").isNotNull()
            & F.col("scheduled_sessions").between(1,20)
            & F.col("attended_sessions").between(0,F.col("scheduled_sessions"))
            & F.col("late_sessions").between(0,F.col("attended_sessions"))
            & F.col("engagement_score").between(0,100)).dropDuplicates(["person_id","date"])
        prepared=valid.withColumn("date",F.to_date("date")) \
            .withColumn("daily_attendance_rate",F.col("attended_sessions")/F.col("scheduled_sessions")) \
            .withColumn("daily_late_rate",F.col("late_sessions")/F.col("scheduled_sessions")) \
            .withColumn("at_risk",(F.col("future_absence_days")>=4).cast("int"))
        window=Window.partitionBy("person_id").orderBy("date").rowsBetween(-6,0)
        features=prepared.withColumn("attendance_rate_7d",F.avg("daily_attendance_rate").over(window)) \
            .withColumn("late_rate_7d",F.avg("daily_late_rate").over(window)) \
            .withColumn("engagement_7d",F.avg("engagement_score").over(window)) \
            .drop("future_absence_days")
        Path(args.output).parent.mkdir(parents=True,exist_ok=True)
        features.write.mode("overwrite").parquet(args.output)
        print(f"Spark wrote {features.count():,} curated rows to {args.output}")
    finally:
        spark.stop()

if __name__=="__main__": main()