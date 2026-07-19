"""LightGBM model training script with Optuna hyperparameter search."""

import json
import os
from pathlib import Path

import joblib
import lightgbm as lgb
import numpy as np
import optuna
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.metrics import classification_report, fbeta_score
from sklearn.model_selection import train_test_split

# Suppress Optuna output
optuna.logging.set_verbosity(optuna.logging.WARNING)

DATA_PATH = Path(__file__).parent.parent.parent / "data" / "student_dropout.csv"
MODEL_PATH = "models/lgbm_model.joblib"
FEATURE_NAMES_PATH = "models/feature_names.json"

RANDOM_STATE = 1955

cat_features = [
    "Gender",
    "Internet_Access",
    "Part_Time_Job",
    "Scholarship",
    "Semester",
    "Department",
    "Parental_Education",
]

num_features = [
    "Age",
    "Family_Income",
    "Study_Hours_per_Day",
    "Attendance_Rate",
    "Assignment_Delay_Days",
    "Travel_Time_Minutes",
    "Stress_Index",
    "GPA",
    "Semester_GPA",
    "CGPA",
]

feature_columns = cat_features + num_features


def load_data():
    df = pd.read_csv(DATA_PATH)
    # Cast categoricals to category dtype
    for col in cat_features:
        df[col] = df[col].astype("category")
    X = df[feature_columns]
    y = df["Dropout"]
    return X, y


def split_data(X, y):
    # Stratified 70/15/15 split
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=RANDOM_STATE
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=RANDOM_STATE
    )
    return X_train, X_val, X_test, y_train, y_val, y_test


def f2_score(y_true, y_pred):
    return fbeta_score(y_true, y_pred, beta=2)


def objective(trial, X_train, y_train, X_val, y_val):
    params = {
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
        "max_depth": trial.suggest_int("max_depth", 3, 12),
        "num_leaves": trial.suggest_int("num_leaves", 15, 127),
        "min_child_samples": trial.suggest_int("min_child_samples", 10, 100),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "n_estimators": 1000,
        "class_weight": "balanced",
        "random_state": RANDOM_STATE,
        "verbose": -1,
    }
    model = LGBMClassifier(**params)
    model.fit(
        X_train,
        y_train,
        eval_set=[(X_val, y_val)],
        callbacks=[lgb.early_stopping(10, verbose=False)],
    )
    y_pred = model.predict(X_val)
    return f2_score(y_val, y_pred)


def main():
    print("Loading data...")
    X, y = load_data()

    print("Splitting data (70/15/15)...")
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(X, y)
    print(f"  Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")

    print("Running Optuna hyperparameter search (50 trials)...")
    study = optuna.create_study(
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=RANDOM_STATE),
    )
    study.optimize(
        lambda trial: objective(trial, X_train, y_train, X_val, y_val),
        n_trials=50,
    )

    best_params = study.best_params
    print(f"Best F2 on val: {study.best_value:.4f}")
    print(f"Best params: {best_params}")

    print("Retraining final model on train set with best params...")
    final_model = LGBMClassifier(
        **best_params,
        n_estimators=1000,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        verbose=-1,
    )
    final_model.fit(
        X_train,
        y_train,
        eval_set=[(X_val, y_val)],
        callbacks=[lgb.early_stopping(10, verbose=False)],
    )

    print("\nEvaluating on test set:")
    y_pred = final_model.predict(X_test)
    print(classification_report(y_test, y_pred))
    test_f2 = f2_score(y_test, y_pred)
    print(f"F2-score on test set: {test_f2:.4f}")

    print("\nSaving artifacts...")
    joblib.dump(final_model, MODEL_PATH)
    with open(FEATURE_NAMES_PATH, "w") as f:
        json.dump(feature_columns, f)

    print("Model saved to models/lgbm_model.joblib")


if __name__ == "__main__":
    main()
