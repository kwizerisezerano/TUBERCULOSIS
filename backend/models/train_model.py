import os
import json
import time
import urllib.request
import os
import json
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
        'has_fatigue': 1 if 'fatigue' in symptoms_text or 'tired' in symptoms_text else 0,
        'has_shortness_of_breath': 1 if 'shortness' in symptoms_text or 'breath' in symptoms_text or 'dyspnea' in symptoms_text else 0
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

# Global stats for filling missing values during prediction
_global_fill_values = None

def _calculate_global_fill_values():
    """Calculate global fill values from existing patients (median for numerical, mode for categorical)"""
    global _global_fill_values
    if _global_fill_values:
        return _global_fill_values

    from collections import Counter
    import numpy as np
    from models.models import Patient

    patients = Patient.query.all()

    numerical_fields = ['age', 'weight', 'persistent_cough_duration_weeks', 'oxygen_saturation_spo2']
    categorical_fields = ['gender', 'hiv', 'diabetes', 'smoking_status', 'alcohol_use',
                          'contact_with_tb_patient', 'previous_tb_treatment',
                          'sputum_smear_test', 'genexpert_test', 'chest_xray']

    values = {f: [] for f in numerical_fields + categorical_fields}

    for patient in patients:
        for field in numerical_fields:
            val = _get_value(patient, field)
            if val is not None and (isinstance(val, (int, float)) and not np.isnan(val)):
                values[field].append(val)
        for field in categorical_fields:
            val = _get_value(patient, field)
            if val is not None and val not in ['', 'Unknown']:
                values[field].append(val)

    fill_values = {}

    # Numerical fields: use median
    for field in numerical_fields:
        if len(values[field]) > 0:
            fill_values[field] = np.median(values[field])
        else:
            if field == 'age':
                fill_values[field] = 35
            elif field == 'weight':
                fill_values[field] = 70
            elif field == 'persistent_cough_duration_weeks':
                fill_values[field] = 0
            elif field == 'oxygen_saturation_spo2':
                fill_values[field] = 98

    # Categorical fields: use mode
    for field in categorical_fields:
        if len(values[field]) > 0:
            fill_values[field] = Counter(values[field]).most_common(1)[0][0]
        else:
            if field == 'gender':
                fill_values[field] = 'Male'
            elif field in ['hiv', 'diabetes', 'contact_with_tb_patient', 'previous_tb_treatment']:
                fill_values[field] = 'No'
            elif field == 'smoking_status':
                fill_values[field] = 'Never'
            elif field == 'alcohol_use':
                fill_values[field] = 'Never'
            else:
                fill_values[field] = 'Unknown'

    _global_fill_values = fill_values
    return fill_values


def _get_bool_symptom(patient, key):
    """Helper to get boolean symptom field"""
    val = _get_value(patient, key, None)
    if val is not None:
        val_str = str(val).lower().strip()
        if val_str in ['yes', 'y', '1', 'true']:
            return 1
        elif val_str in ['no', 'n', '0', 'false']:
            return 0
    return None


def get_patient_features(patient):
    fill_values = _calculate_global_fill_values()
    import numpy as np

    # First check if we have pre-extracted symptom fields in the patient model
    has_fever_val = _get_bool_symptom(patient, "has_fever")
    has_cough_val = _get_bool_symptom(patient, "has_cough")
    has_blood_val = _get_bool_symptom(patient, "has_blood")
    has_chest_pain_val = _get_bool_symptom(patient, "has_chest_pain")
    has_night_sweats_val = _get_bool_symptom(patient, "has_night_sweats")
    has_weight_loss_val = _get_bool_symptom(patient, "has_weight_loss")
    has_fatigue_val = _get_bool_symptom(patient, "has_fatigue")
    has_shortness_of_breath_val = _get_bool_symptom(patient, "has_shortness_of_breath")

    # Fallback to parsing symptoms text if needed
    symptoms_text = _get_value(patient, "symptoms", "") or ""
    symptoms_features = preprocess_symptoms(symptoms_text)

    # Use model field if present, else fallback to parsed text
    has_fever = has_fever_val if has_fever_val is not None else symptoms_features["has_fever"]
    has_cough = has_cough_val if has_cough_val is not None else symptoms_features["has_cough"]
    has_blood = has_blood_val if has_blood_val is not None else symptoms_features["has_blood"]
    has_chest_pain = has_chest_pain_val if has_chest_pain_val is not None else symptoms_features["has_chest_pain"]
    has_night_sweats = has_night_sweats_val if has_night_sweats_val is not None else symptoms_features["has_night_sweats"]
    has_weight_loss = has_weight_loss_val if has_weight_loss_val is not None else symptoms_features["has_weight_loss"]
    has_fatigue = has_fatigue_val if has_fatigue_val is not None else symptoms_features["has_fatigue"]
    has_shortness_of_breath = has_shortness_of_breath_val if has_shortness_of_breath_val is not None else symptoms_features["has_shortness_of_breath"]

    # Get and fill gender
    gender = _normalize_gender(_get_value(patient, "gender", None))
    if gender is None or gender == 'Unknown':
        gender = fill_values['gender']

    # Get and fill test results
    sputum = _normalize_test_result(_get_value(patient, "sputum_smear_test", None))
    if sputum == 'Unknown':
        sputum = fill_values['sputum_smear_test']

    genexpert = _normalize_test_result(_get_value(patient, "genexpert_test", None))
    if genexpert == 'Unknown':
        genexpert = fill_values['genexpert_test']

    chest_xray = _normalize_test_result(_get_value(patient, "chest_xray", None))
    if chest_xray == 'Unknown':
        chest_xray = fill_values['chest_xray']

    # Get and fill yes/no fields
    hiv = _normalize_yes_no(_get_value(patient, "hiv", None))
    if hiv is None or hiv == 'Unknown':
        hiv = fill_values['hiv']

    diabetes = _normalize_yes_no(_get_value(patient, "diabetes", None))
    if diabetes is None or diabetes == 'Unknown':
        diabetes = fill_values['diabetes']

    # Get and fill numerical fields
    age = _get_value(patient, "age", None)
    try:
        age = int(age) if age is not None and not np.isnan(age) else fill_values['age']
    except Exception:
        age = fill_values['age']

    weight = _get_value(patient, "weight", None)
    try:
        weight = float(weight) if weight is not None and not np.isnan(weight) else fill_values['weight']
    except Exception:
        weight = fill_values['weight']

    persistent_cough_weeks = _get_value(patient, "persistent_cough_duration_weeks", None)
    try:
        persistent_cough_weeks = int(persistent_cough_weeks) if persistent_cough_weeks is not None and not np.isnan(persistent_cough_weeks) else fill_values['persistent_cough_duration_weeks']
    except Exception:
        persistent_cough_weeks = fill_values['persistent_cough_duration_weeks']

    # Get and fill other categorical fields
    contact_tb = _normalize_yes_no(_get_value(patient, "contact_with_tb_patient", None))
    if contact_tb is None or contact_tb == 'Unknown':
        contact_tb = fill_values['contact_with_tb_patient']

    previous_tb_tx = _normalize_yes_no(_get_value(patient, "previous_tb_treatment", None))
    if previous_tb_tx is None or previous_tb_tx == 'Unknown':
        previous_tb_tx = fill_values['previous_tb_treatment']

    smoking_status = str(_get_value(patient, "smoking_status", "") or "").strip()
    if smoking_status in ['', 'Unknown']:
        smoking_status = fill_values['smoking_status']

    alcohol_use = str(_get_value(patient, "alcohol_use", "") or "").strip()
    if alcohol_use in ['', 'Unknown']:
        alcohol_use = fill_values['alcohol_use']

    spo2 = _get_value(patient, "oxygen_saturation_spo2", None)
    try:
        spo2 = float(spo2) if spo2 is not None and not np.isnan(spo2) else fill_values['oxygen_saturation_spo2']
    except Exception:
        spo2 = fill_values['oxygen_saturation_spo2']

    return {
        "age": age,
        "weight": weight,
        "gender_male": 1 if gender == "Male" else 0,
        "gender_female": 1 if gender == "Female" else 0,
        "gender_other": 1 if gender == "Other" else 0,
        "persistent_cough_duration_weeks": persistent_cough_weeks,
        "contact_with_tb_patient_yes": 1 if contact_tb == "Yes" else 0,
        "previous_tb_treatment_yes": 1 if previous_tb_tx == "Yes" else 0,
        "smoking_current": 1 if "Current" in smoking_status else 0,
        "smoking_former": 1 if "Former" in smoking_status else 0,
        "alcohol_regular": 1 if "Regular" in alcohol_use else 0,
        "oxygen_saturation_spo2": spo2,
        "has_fever": has_fever,
        "has_cough": has_cough,
        "has_weight_loss": has_weight_loss,
        "has_night_sweats": has_night_sweats,
        "has_chest_pain": has_chest_pain,
        "has_blood": has_blood,
        "has_fatigue": has_fatigue,
        "has_shortness_of_breath": has_shortness_of_breath,
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
    
    # Calculate feature importances as percentages
    importances = model.feature_importances_
    feature_importances = {}
    total_importance = sum(importances)
    for i, feature in enumerate(X.columns):
        feature_importances[feature] = round((importances[i] / total_importance) * 100, 2)

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

    # Print model info
    print("\n=== Model Information ===")
    print(f"Model: Random Forest Classifier")
    print(f"Parameters: n_estimators=300, max_depth=14, min_samples_split=5, min_samples_leaf=2, class_weight='balanced', random_state=42")
    print(f"\nModel Accuracy: {accuracy:.2%}")
    print(f"\nFeature Importances (%):")
    for feat, imp in sorted(feature_importances.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {feat}: {imp}%")

    return {
        "accuracy": float(accuracy),
        "feature_names": list(X.columns),
        "feature_importances": feature_importances,
        "model_params": {
            "model_type": "RandomForestClassifier",
            "n_estimators": 300,
            "max_depth": 14,
            "min_samples_split": 5,
            "min_samples_leaf": 2,
            "class_weight": "balanced",
            "random_state": 42,
        },
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

    # Save results to JSON file
    model_info_path = os.path.join(os.path.dirname(__file__), "model_info.json")
    with open(model_info_path, "w") as f:
        json.dump(results, f, indent=2)

    return results

if __name__ == "__main__":
    from app import app
    with app.app_context():
        result = train_model_from_database()
        print("\nTraining complete!")
