# TB Diagnostic System

A comprehensive tuberculosis diagnostic system with ML-based predictions, patient management, and alerts.

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

## Features

- **Multi-database support** (SQLite, MySQL, PostgreSQL)
- **Symptom analysis** with risk assessment
- **Test result evaluation** with confidence scores
- **ML-based predictions** for TB status and drug resistance (trained from database)
- **ML Feature Importance**: Shows which factors contribute most to predictions
- **Comprehensive treatment recommendations**
- **Patient management system** with extended fields:
  - Weight (kg)
  - Persistent cough duration (weeks)
  - Contact with TB patient
  - Previous TB treatment
  - Smoking status
  - Alcohol use
  - Oxygen saturation (SpO2 %)
- **Smart data preprocessing**: Fills missing values using median (for numerical) and mode (for categorical)
- **Full translations for all UI elements and alerts**
- **In-app and email alerts** for high-risk cases
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
  - genexpert_positive: 29.71%
  - chest_xray_abnormal: 27.23%
  - sputum_positive: 21.41%
  - age: 10.03%
  - has_fever: 3.52%
  - has_weight_loss: 1.73%
  - has_cough: 1.33%
  - has_blood: 1.3%
  - has_fatigue: 1.21%
  - gender_female: 1.05%
  - gender_male: 0.73%
  - has_chest_pain: 0.48%
  - has_night_sweats: 0.27%
  - weight: 0.0%
  - gender_other: 0.0%
  - persistent_cough_duration_weeks: 0.0%
  - contact_with_tb_patient_yes: 0.0%
  - previous_tb_treatment_yes: 0.0%
  - smoking_current: 0.0%
  - smoking_former: 0.0%
  - alcohol_regular: 0.0%
  - oxygen_saturation_spo2: 0.0%
  - hiv_yes: 0.0%
  - diabetes_yes: 0.0%
```

**What does this mean?**

Each feature importance percentage represents how much that factor contributed to the ML model's predictions:
- **Top features (20-30%):** GenXpert test results, chest X-ray abnormalities, and sputum smear results are the strongest predictors of TB status
- **Age (10%):** Age is also a significant factor
- **Symptoms (1-4%):** Fever, weight loss, cough, blood in sputum, and fatigue contribute moderately
- **Other features (<1%):** Gender, lifestyle factors, and other fields have minimal or no impact on the current model with the available training data

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
