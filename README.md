# Predictive EHR Analytics Dashboard for Tuberculosis

## 🎯 Key Points

1. **ML-Powered Risk Prediction**: Random Forest models predict TB status and drug resistance with feature importance analysis
2. **Automatic Prescription Generation**: ML recommends and creates prescriptions automatically when diagnosis is completed
3. **Antimicrobial Stewardship**: Detects misuse (overuse, self-medication) and triggers real-time alerts
4. **Role-Based Access Control (RBAC)**:
   - Doctors: Full patient/diagnosis/prescription/lab access
   - Lab Techs: Only lab test requests and results
   - Pharmacists: Only prescriptions to approve/reject
   - Admins: Full system control
5. **Cumulative Antibiogram**: Includes TB-specific (MTBC) and common bacterial pathogens
6. **WHO-Aligned Treatment**: Follows WHO TB treatment guidelines
7. **Multi-Language Support**: English, French, Swahili, Kinyarwanda
8. **Real-Time Alerts & Audit Logs**: Complete audit trail of all clinical actions

## 📊 Project Overview

A **predictive EHR analytics dashboard** for patient risk monitoring and antimicrobial stewardship using machine learning. This system provides healthcare professionals with real-time insights, AI-driven recommendations, and comprehensive tools to improve patient outcomes and ensure safe antibiotic use.

## 🎯 Required Actions (Fully Implemented)

✅ **Machine Learning Models**: Built and validated ML models to predict patient health risks and support early intervention
✅ **Antimicrobial Stewardship**: Designed a system to monitor antibiotic usage, detect misuse, and provide recommendations for appropriate prescriptions
✅ **User-Friendly Dashboard**: Comprehensive dashboard to visualize patient risk levels, alerts, trends, and treatment insights
✅ **Secure Integration**: Securely integrates with clinical data sources (patient records) while ensuring confidentiality and compliance with healthcare data standards
✅ **Real-Time Alerts & Recommendations**: Provides real-time alerts, analytical reports, and AI-driven recommendations to support clinical decision-making

## 📋 System Roles & Access Control

| Role               | Permissions                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| **System Admin**   | Manages users, controls system settings, monitors reports and performance  |
| **Doctor**         | Creates/manages patient records, enters symptoms/diagnoses, views ML predictions, requests lab tests |
| **Lab Technician** | Accesses only lab test requests, performs and uploads results              |
| **Pharmacist**     | Views only prescriptions, approves/rejects based on availability            |

## 🛠️ Core Features

### 📊 Dashboard & Analytics
- **Patient risk visualization**: Real-time dashboards with risk levels (low/medium/high)
- **Trend analysis**: Monitor TB cases, treatment outcomes, and antibiotic usage over time
- **Alerts overview**: Centralized view of all high-risk cases and antimicrobial stewardship alerts
- **Model insights**: Feature importance display showing which factors contribute most to predictions

### 🤖 Machine Learning
- **Predictive models**: Random Forest Classifier for TB status and drug resistance prediction
- **Feature importance**: Shows % contribution of each feature to ML predictions
- **Continuous training**: Models train directly from database records
- **Risk assessment**: Classifies patients by risk level for early intervention

### 💊 Antimicrobial Stewardship
- **Prescription monitoring**: Tracks all antibiotic prescriptions
- **Misuse detection**: Alerts for overuse, wrong dosage, or frequent repetition
- **Recommendations**: Provides guidance for appropriate antibiotic use
- **Approval workflow**: Pharmacist review and approval process

### 🔬 Lab Test Management
- **Test requests**: Doctors can order lab tests (GeneXpert, smear, culture, etc.)
- **Result upload**: Lab technicians can upload and update test results
- **Integration**: Lab results linked back to patient records for ML updates

### 📝 Patient Management
- **Extended patient fields**: Weight, cough duration, TB contact, previous treatment, smoking, alcohol, SpO2
- **Complete records**: Symptoms, test results, diagnoses, treatments, prescriptions, and lab tests
- **Smart preprocessing**: Missing values filled using median (numerical) and mode (categorical)

### 🔒 Security & Compliance
- **Role-Based Access Control (RBAC)**: Strict access control by user role
- **Audit logs**: Tracks all actions (prescriptions, lab results, approvals, etc.)
- **Data confidentiality**: Secure patient data handling

## Project Structure

```
/
├── backend/          # Flask API + ML + Database import
│   ├── models/       # Database models + training code
│   ├── data/         # Public raw datasets + owner curated species dataset
│   ├── app.py        # Main API server
│   ├── requirements.txt
│   ├── data/raw/     # Raw CSV datasets staged for import
│   └── .env          # Configuration (copy from .env.example)
└── frontend/         # Nuxt 3 + Tailwind UI
    ├── app.vue
    ├── nuxt.config.ts
    ├── tailwind.config.js
    ├── package.json
    └── assets/css/main.css
```

## 🌍 ATC/DDD Standard Integration
- **ATC Codes**: Full 5-level ATC (Anatomical Therapeutic Chemical) classification for all drugs
- **DDD Calculation**: Automated Defined Daily Dose (DDD) calculation for antibiotic usage monitoring
- **Consumption Tracking**: Tracks antibiotic consumption using DDD per 100 bed-days (standard hospital metric)
- **Drug Lookup**: When a doctor prescribes a medicine, the system automatically links it to the correct Level 5 ATC Code

## 📊 Cumulative Antibiogram
- **Automated Antibiogram Generation**: Mines lab results to calculate bacterial isolate susceptibility percentages
- **Empirical Treatment Guidance**: Helps doctors select the most effective antibiotic based on local resistance patterns
- **Trend Analysis**: Monitors resistance trends over time

## 🏗️ Implementation Pillars
1. **Predictive Risk Module**: ML models trained on historical data to predict patient readmission and treatment failure risks
2. **Automated Antibiogram Visualization**: Cumulative antibiogram dashboard showing susceptibility percentages
3. **Consumption Surveillance**: Antibiotic usage tracking using WHO ATC/DDD standards
4. **Real-Time Alerts**: Email and in-app alerts for highly resistant organisms and prescription deviations

## Additional Features

- **Multi-database support** (SQLite, MySQL, PostgreSQL)
- **Full translations** for all UI elements and alerts (English, French, Swahili, Kinyarwanda)
- **Dark/light mode UI**

## Tuberculosis Reference

### Main Tuberculosis Bacteria

The disease tuberculosis is mainly caused by bacteria in the **Mycobacterium tuberculosis complex (MTBC)**:

- **Mycobacterium tuberculosis** - the most common cause of human TB
- **Mycobacterium bovis** - zoonotic TB, can spread from infected cattle or unpasteurized milk
- **Mycobacterium africanum** - an important cause of TB in parts of West Africa
- **Mycobacterium canettii** - a rare MTBC member
- **Mycobacterium microti** - usually animal-associated, rarely infects humans
- **Mycobacterium caprae** - animal-associated, can occasionally infect humans
- **Mycobacterium pinnipedii** - associated with seals and sea lions, rare in humans
- **Mycobacterium orygis** - another MTBC member reported in both animals and humans

### Common Clinical Types Of TB

- **Pulmonary TB (PTB)** - affects the lungs
- **Extrapulmonary TB (EPTB)** - affects organs outside the lungs
- **Latent TB Infection (LTBI)** - TB bacteria are present but inactive
- **Miliary TB** - widespread disseminated TB
- **Drug-sensitive TB (DS-TB)** - responsive to standard first-line treatment
- **Rifampicin-resistant TB (RR-TB)** - resistant to rifampicin
- **Multidrug-resistant TB (MDR-TB)** - resistant to at least isoniazid and rifampicin
- **Extensively drug-resistant TB (XDR-TB)** - resistant to multiple key TB drugs

### WHO-Aligned Decision Chain

The system is designed around this medical decision flow:

1. **TB detection**
   - Determine whether the patient record is consistent with TB.
2. **Bacteria assessment**
   - Estimate the most likely MTBC species from clinician input, exposure history, culture context, and epidemiology.
3. **Infection assessment**
   - Classify pulmonary, extrapulmonary, latent, miliary, and related TB patterns.
4. **Resistance / antibiogram review**
   - Interpret GeneXpert, culture, DST/antibiogram summary, and resistance markers.
5. **Treatment engine**
   - Select WHO-aligned treatment options using infection type plus resistance class.
6. **Treatment administration**
   - Return duration, intensive phase, continuation phase, DOTS-style dosing, monitoring, and alternative options where appropriate.

### Important Medical Logic

- First-line treatment is broadly similar across many MTBC members.
- Final treatment choice depends mainly on:
  - **infection site / severity**
  - **drug resistance / DST / antibiogram**
  - **species-specific exceptions** such as **M. bovis** and pyrazinamide resistance
  - **patient risk factors** such as HIV and diabetes
- Because of this, the project uses a **WHO-aligned decision engine**, not species alone, to choose treatment.

## Setup

### Backend

1. Install dependencies:
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

2. Configure `.env` (optional, defaults to SQLite):
```env
DATABASE_TYPE=sqlite  # or mysql/postgresql
```

3. Run one backend bootstrap command:
```bash
cd backend
python bootstrap.py --runserver
```

Or, if you already have data in your database and don't want to reset it:
```bash
cd backend
python bootstrap.py --no-reset --runserver
```

If you see `ModuleNotFoundError: No module named 'sqlalchemy'`, it usually means you ran `python` outside the virtual environment. Run it with:
```bash
cd backend
.\.venv\Scripts\python bootstrap.py --runserver
```

This command:
- (By default) drops the existing database if it exists and recreates it from scratch
- creates database tables
- imports and cleans the CSV datasets
- seeds users and roles
- trains models from database records
- starts the backend API server

### ML Model Information

When the models are trained, you will see feature importance output in your terminal like this:

```
=== Model Information ===
Model: Random Forest Classifier
Parameters: n_estimators=300, max_depth=14, min_samples_split=5, min_samples_leaf=2, class_weight='balanced', random_state=42

Feature Importances (%):
  - genexpert_positive: 28.48%
  - chest_xray_abnormal: 23.02%
  - sputum_positive: 21.78%
  - persistent_cough_duration_weeks: 6.2%
  - age: 5.36%
  - oxygen_saturation_spo2: 3.58%
  - has_cough: 2.57%
  - has_weight_loss: 1.38%
  - has_fever: 1.36%
  - has_blood: 1.3%
  - weight: 0.95%
  - gender_female: 0.94%
  - gender_male: 0.75%
  - has_fatigue: 0.52%
  - has_shortness_of_breath: 0.48%
  - has_chest_pain: 0.42%
  - has_night_sweats: 0.37%
  - contact_with_tb_patient_yes: 0.18%
  - smoking_former: 0.1%
  - previous_tb_treatment_yes: 0.09%
  - smoking_current: 0.06%
  - alcohol_regular: 0.05%
  - gender_other: 0.03%
  - hiv_yes: 0.02%
  - diabetes_yes: 0.02%

=== Model Information ===
Model: Random Forest Classifier
Parameters: n_estimators=300, max_depth=14, min_samples_split=5, min_samples_leaf=2, class_weight='balanced', random_state=42

Feature Importances (%):
  - oxygen_saturation_spo2: 36.86%
  - weight: 14.67%
  - chest_xray_abnormal: 9.36%
  - genexpert_positive: 8.47%
  - persistent_cough_duration_weeks: 5.7%
  - has_fever: 5.19%
  - has_weight_loss: 4.73%
  - sputum_positive: 3.03%
  - has_fatigue: 1.81%
  - age: 1.78%
  - gender_male: 1.14%
  - gender_female: 1.04%
  - has_cough: 0.98%
  - contact_with_tb_patient_yes: 0.76%
  - has_shortness_of_breath: 0.75%
  - smoking_current: 0.65%
  - alcohol_regular: 0.55%
  - smoking_former: 0.49%
  - has_night_sweats: 0.39%
  - has_chest_pain: 0.39%
  - hiv_yes: 0.32%
  - previous_tb_treatment_yes: 0.3%
  - has_blood: 0.23%
  - gender_other: 0.2%
  - diabetes_yes: 0.2%
```

**What does this mean?**

Each feature importance percentage represents how much that factor contributed to the ML model's predictions:
- **Top features (20-30% for TB Status): GenXpert test results, chest X-ray abnormalities, and sputum smear results are the strongest predictors of TB status
- **Persistent Cough Duration (6.2%): Important for both TB and Drug Resistance
- **Oxygen Saturation (3.6% for TB, 36.9% for Drug Resistance): Significant factor for predicting drug resistance
- **Symptoms (0.3-2.6%): All WHO-aligned TB symptoms now captured, including `has_shortness_of_breath`
- **Total Patients:** 28,191 patients in training dataset

### Owner Dataset

- Curated species-labeled dataset file: `backend/data/raw/owner_tb_species_dataset.csv`
- Dataset schema guide: `backend/data/owner_tb_species_dataset_schema.md`
- The importer preserves the `patient_id` provided in this owner dataset.

### Seeded User Credentials

Use these accounts after running `python bootstrap.py --runserver`:

- `system_admin`
  - Email: `divinekageruka@gmail.com`
  - Password: `Admin123!`
- `doctor`
  - Email: `igiranezac459@gmail.com`
  - Password: `Doctor123!`
- `lab_technician`
  - Email: `clarisseigiraneza56@gmail.com`
  - Password: `LabTech123!`
- `pharmacist`
  - Email: `clarisseigiraneza915@gmail.com`
  - Password: `Pharm123!`
- `hospital_admin`
  - Email: `igiclarisse10@gmail.com`
  - Password: `Admin123!`

4. Optional individual commands:
```bash
python bootstrap.py --no-reset --runserver
python seed_users.py
python import_data.py
python seed_users.py
python setup.py
python app.py
cd backend
python bootstrap.py --runserver
```


### Frontend

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run development server:
```bash
npm run dev
```

## API Endpoints

- `GET /api/health` - Backend readiness and model status
- `POST /api/diagnose` - Analyze patient and get diagnosis
- `GET/POST /api/patients` - Patient management
- `GET /api/diagnoses` - View saved diagnoses
- `GET /api/alerts` - View alerts
- `PUT /api/alerts/:id/read` - Mark alert as read
- `POST /api/train-model` - Train ML models from database (system_admin only)

## Database Configuration

### SQLite (Default)
No extra config needed.

### MySQL
```env
DATABASE_TYPE=mysql
DB_USER=root
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=3306
DB_NAME=tb_diagnostic
```

### PostgreSQL
```env
DATABASE_TYPE=postgresql
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tb_diagnostic
```
