"""Train and track a risk model using the synthetic future-outcome label."""
from __future__ import annotations
import argparse,json,os
from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score,f1_score,precision_score,recall_score,roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler
ROOT=Path(__file__).resolve().parents[1]
NUMERIC=["attendance_rate_7d","late_rate_7d","engagement_7d","engagement_score","assignment_submissions","scheduled_sessions","day_of_week"]
CATEGORICAL=["person_type","department","campus"]

def train_model(input_path:Path,model_dir:Path)->dict:
    data=pd.read_csv(input_path)
    if data.at_risk.nunique()<2: raise ValueError("Training requires both classes.")
    x=data[NUMERIC+CATEGORICAL]; y=data.at_risk.astype(int)
    x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=.22,random_state=42,stratify=y)
    prep=ColumnTransformer([
        ("numeric",Pipeline([("imputer",SimpleImputer(strategy="median")),("scale",StandardScaler())]),NUMERIC),
        ("categorical",Pipeline([("imputer",SimpleImputer(strategy="most_frequent")),("onehot",OneHotEncoder(handle_unknown="ignore"))]),CATEGORICAL)])
    algorithm="HistGradientBoostingClassifier"
    try:
        from xgboost import XGBClassifier
        estimator=XGBClassifier(n_estimators=220,max_depth=4,learning_rate=.05,subsample=.85,
            colsample_bytree=.85,reg_lambda=1.5,eval_metric="logloss",random_state=42,n_jobs=4)
        algorithm="XGBClassifier"
    except ImportError:
        estimator=HistGradientBoostingClassifier(max_iter=180,learning_rate=.07,random_state=42)
    model=Pipeline([("preprocessor",prep),("classifier",estimator)])
    model.fit(x_train,y_train)
    prob=model.predict_proba(x_test)[:,1]; pred=(prob>=.5).astype(int)
    metrics={"algorithm":algorithm,"dataset":"synthetic","rows":int(len(data)),"test_rows":int(len(y_test)),
      "positive_rate":round(float(y.mean()),4),"accuracy":round(float(accuracy_score(y_test,pred)),4),
      "precision":round(float(precision_score(y_test,pred,zero_division=0)),4),
      "recall":round(float(recall_score(y_test,pred,zero_division=0)),4),
      "f1":round(float(f1_score(y_test,pred,zero_division=0)),4),
      "roc_auc":round(float(roc_auc_score(y_test,prob)),4),"threshold":.5,
      "note":"Metrics are from generated synthetic data and are not evidence of real-world or institutional performance."}
    model_dir.mkdir(parents=True,exist_ok=True)
    joblib.dump(model,model_dir/"attendance_risk_model.joblib")
    (model_dir/"metrics.json").write_text(json.dumps(metrics,indent=2),encoding="utf-8")
    scored=pd.read_csv(input_path)
    scored["risk_probability"]=model.predict_proba(scored[NUMERIC+CATEGORICAL])[:,1]
    scored["risk_band"]=pd.cut(scored.risk_probability,bins=[-.001,.35,.65,1.0],labels=["Low","Medium","High"])
    latest=scored.sort_values("date").groupby("person_id",as_index=False).tail(1)
    latest.sort_values("risk_probability",ascending=False).to_csv(input_path.parent/"risk_predictions.csv",index=False)
    tracking=os.getenv("MLFLOW_TRACKING_URI")
    if tracking:
        try:
            import mlflow
            import mlflow.sklearn
            mlflow.set_tracking_uri(tracking); mlflow.set_experiment("student-staff-attendance-risk")
            with mlflow.start_run(run_name=algorithm):
                mlflow.log_param("algorithm",algorithm); mlflow.log_param("dataset","synthetic")
                mlflow.log_param("risk_threshold",.5)
                mlflow.log_metrics({k:v for k,v in metrics.items() if isinstance(v,(int,float))})
                mlflow.log_artifact(str(model_dir/"metrics.json"))
                mlflow.sklearn.log_model(model,artifact_path="model")
        except Exception as exc: print(f"MLflow tracking unavailable; model saved locally. Detail: {exc}")
    return metrics

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,default=ROOT/"data/processed/person_features.csv")
    parser.add_argument("--model-dir",type=Path,default=ROOT/"models")
    args=parser.parse_args()
    if not args.input.exists(): raise FileNotFoundError("Run python src/pipeline.py before training.")
    print(json.dumps(train_model(args.input,args.model_dir),indent=2))

if __name__=="__main__": main()