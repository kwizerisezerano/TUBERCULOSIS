import os
import json
import time
import urllib.request
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE
from models.models import Patient


def _emit_debug_event(hypothesis_id, location, message, data):
    # Debug telemetry should never break local training when no collector is running.
    try:
        payload = {
            "sessionId": "bootstrap-train-failure",
            "runId": "pre-fix",
            "hypothesisId": hypothesis_id,
            "location": location,
            "msg": message,
            "data": data,
            "ts": time.time_ns() // 1_000_000,
        }
        request = urllib.request.Request(
            "http://127.0.0.1:7778/event",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(request, timeout=1).read()
    except Exception:
        pass

def preprocess_symptoms(symptoms_text):
    if pd.isna(symptoms_text) or symptoms_text is None:
        symptoms_text = ""
    symptoms_text = str(symptoms_text).lower()
    
    features = {
        'has_cough': 1 if 'cough' in symptoms_text else 0,
        'has_fever': 1 if 'fever' in symptoms_text else 0,
        'has_weight_loss': 1 if 'weight' in symptoms_text or 'loss' in symptoms_text else 0,
        'has_night_sweats': 1 if 'night' in symptoms_text or 'sweat' in symptoms_text else 0,
        'has_chest_pain': 1 if 'chest' in symptoms_text and 'pain' in symptoms_text else 0,
        'has_blood': 1 if 'blood' in symptoms_text or 'hemoptysis' in symptoms_text else 0,
        'has_fatigue': 1 if 'fatigue' in symptoms_text or 'tired' in symptoms_text else 0
    }
    return features

def _get_value(record, key, default=None):
    if isinstance(record, dict):
        return record.get(key, default)
    return getattr(record, key, default)

def _normalize_yes_no(value):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    value = str(value).strip().lower()
    if value in {"yes", "y", "1", "true", "positive"}:
        return "Yes"
    if value in {"no", "n", "0", "false", "negative"}:
        return "No"
    return None

def _normalize_test_result(value):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "Unknown"
    v = str(value).strip().lower()
    if v in {"positive", "pos", "yes", "1", "true", "detected", "mtb detected"}:
        return "Positive"
    if v in {"negative", "neg", "no", "0", "false", "not detected", "mtb not detected"}:
        return "Negative"
    if v in {"abnormal"}:
        return "Abnormal"
    if v in {"normal"}:
        return "Normal"
    return "Unknown"

def _normalize_gender(value):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "Unknown"
    v = str(value).strip().lower()
    if v in {"m", "male", "man", "1"}:
        return "Male"
    if v in {"f", "female", "woman", "0"}:
        return "Female"
    if v in {"other", "non-binary", "nonbinary"}:
        return "Other"
    return "Unknown"

def get_patient_features(patient):
    symptoms_text = _get_value(patient, "symptoms", "") or ""
    symptoms_features = preprocess_symptoms(symptoms_text)

    gender = _normalize_gender(_get_value(patient, "gender", None))

    sputum = _normalize_test_result(_get_value(patient, "sputum_smear_test", None))
    genexpert = _normalize_test_result(_get_value(patient, "genexpert_test", None))
    chest_xray = _normalize_test_result(_get_value(patient, "chest_xray", None))
    hiv = _normalize_yes_no(_get_value(patient, "hiv", None)) or "No"
    diabetes = _normalize_yes_no(_get_value(patient, "diabetes", None)) or "No"

    age = _get_value(patient, "age", None)
    try:
        age = int(age) if age is not None else 30
    except Exception:
        age = 30

    return {
        "age": age,
        "gender_male": 1 if gender == "Male" else 0,
        "gender_female": 1 if gender == "Female" else 0,
        "gender_other": 1 if gender == "Other" else 0,
        "has_fever": symptoms_features["has_fever"],
        "has_cough": symptoms_features["has_cough"],
        "has_weight_loss": symptoms_features["has_weight_loss"],
        "has_night_sweats": symptoms_features["has_night_sweats"],
        "has_chest_pain": symptoms_features["has_chest_pain"],
        "has_blood": symptoms_features["has_blood"],
        "has_fatigue": symptoms_features["has_fatigue"],
        "sputum_positive": 1 if sputum == "Positive" else 0,
        "genexpert_positive": 1 if genexpert == "Positive" else 0,
        "chest_xray_abnormal": 1 if chest_xray == "Abnormal" else 0,
        "hiv_yes": 1 if hiv == "Yes" else 0,
        "diabetes_yes": 1 if diabetes == "Yes" else 0,
    }

def _derive_tb_status_label(patient):
    label = _normalize_yes_no(_get_value(patient, "tb_status_label", None))
    if label in {"Yes", "No"}:
        return label

    sputum = _normalize_test_result(_get_value(patient, "sputum_smear_test", None))
    genexpert = _normalize_test_result(_get_value(patient, "genexpert_test", None))
    chest_xray = _normalize_test_result(_get_value(patient, "chest_xray", None))

    if genexpert == "Positive" or sputum == "Positive":
        return "Yes"
    if sputum == "Negative" and genexpert == "Negative" and chest_xray == "Normal":
        return "No"
    return None

def _derive_drug_resistance_label(patient):
    label = _normalize_yes_no(_get_value(patient, "drug_resistance", None))
    if label in {"Yes", "No"}:
        return label
    return None

def prepare_training_data(task):
    patients = Patient.query.all()
    rows = []

    for patient in patients:
        features = get_patient_features(patient)
        if task == "tb_status":
            label = _derive_tb_status_label(patient)
        elif task == "drug_resistance":
            label = _derive_drug_resistance_label(patient)
        else:
            raise ValueError("Unknown task")

        if label is None:
            continue

        features["label"] = label
        rows.append(features)

    if len(rows) < 20:
        return None

    # #region debug-point A:prepared-data
    _emit_debug_event(
        "A",
        "backend/models/train_model.py:149",
        "[DEBUG] prepared training data",
        {"task": task, "rows": len(rows), "labels": pd.DataFrame(rows)["label"].value_counts().to_dict()},
    )
    # #endregion
    return pd.DataFrame(rows)

def _train_classifier(df, model_filename, encoder_filename):
    X = df.drop("label", axis=1)
    y = df["label"]
    class_counts = y.value_counts().to_dict()

    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    # #region debug-point B:encoded-classes
    _emit_debug_event(
        "B",
        "backend/models/train_model.py:158",
        "[DEBUG] encoded classifier classes",
        {
            "model_filename": model_filename,
            "classes": list(le.classes_),
            "encoded_unique": [int(v) for v in np.unique(y_enc).tolist()],
            "n_samples": int(len(df)),
        },
    )
    # #endregion

    if len(np.unique(y_enc)) > 1:
        try:
            smote = SMOTE(random_state=42)
            X, y_enc = smote.fit_resample(X, y_enc)
        except Exception:
            pass

    stratify = y_enc if len(np.unique(y_enc)) > 1 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=stratify
    )
    # #region debug-point C:train-test-split
    _emit_debug_event(
        "C",
        "backend/models/train_model.py:171",
        "[DEBUG] classifier split info",
        {
            "model_filename": model_filename,
            "y_train_unique": [int(v) for v in np.unique(y_train).tolist()],
            "y_test_unique": [int(v) for v in np.unique(y_test).tolist()],
            "train_size": int(len(y_train)),
            "test_size": int(len(y_test)),
        },
    )
    # #endregion

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=14,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    # #region debug-point D:predictions
    _emit_debug_event(
        "D",
        "backend/models/train_model.py:188",
        "[DEBUG] classifier predictions",
        {
            "model_filename": model_filename,
            "y_pred_unique": [int(v) for v in np.unique(y_pred).tolist()],
            "y_test_unique": [int(v) for v in np.unique(y_test).tolist()],
            "encoder_classes": list(le.classes_),
        },
    )
    # #endregion

    model_path = os.path.join(os.path.dirname(__file__), model_filename)
    encoder_path = os.path.join(os.path.dirname(__file__), encoder_filename)
    joblib.dump(model, model_path)
    joblib.dump(le, encoder_path)
    all_labels = list(range(len(le.classes_)))

    return {
        "accuracy": float(accuracy),
        "feature_names": list(X.columns),
        "classes": list(le.classes_),
        "class_counts": class_counts,
        "model_path": model_path,
        "encoder_path": encoder_path,
        "classification_report": classification_report(
            y_test,
            y_pred,
            labels=all_labels,
            target_names=list(le.classes_),
            zero_division=0,
            output_dict=False,
        ),
        "confusion_matrix": confusion_matrix(y_test, y_pred, labels=all_labels).tolist(),
        "n_samples": int(len(df)),
    }

def train_model_from_database():
    results = train_models_from_database()
    if results.get("drug_resistance"):
        return results["drug_resistance"]
    if results.get("tb_status"):
        return results["tb_status"]
    return {"message": "No models trained", "reason": results.get("reason")}

def train_models_from_database():
    results = {}

    tb_df = prepare_training_data("tb_status")
    if tb_df is not None:
        results["tb_status"] = _train_classifier(tb_df, "tb_status_model.pkl", "tb_status_label_encoder.pkl")

    dr_df = prepare_training_data("drug_resistance")
    if dr_df is not None:
        results["drug_resistance"] = _train_classifier(dr_df, "drug_resistance_model.pkl", "drug_resistance_label_encoder.pkl")

    if not results:
        results["reason"] = "Not enough labeled data in database (need at least ~20 labeled rows per task)"

    return results

if __name__ == "__main__":
    from app import app
    with app.app_context():
        result = train_model_from_database()
        print("\nTraining complete!")
