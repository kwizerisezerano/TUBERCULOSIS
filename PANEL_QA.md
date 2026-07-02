# Panel Q&A — Predictive EHR Analytics Dashboard for Tuberculosis

---

## SECTION 1 — PROJECT OVERVIEW

**Q1. In one sentence, what does your system do?**

It is a web-based clinical decision support system that uses machine learning to predict TB status and drug resistance, automates prescription generation, monitors antibiotic stewardship, and enforces role-based access across multiple hospitals — all aligned with WHO treatment guidelines.

---

**Q2. What problem does this project solve?**

TB diagnosis and treatment in resource-limited settings suffers from three main problems: delayed diagnosis due to manual interpretation of test results, inappropriate antibiotic prescribing that drives drug resistance, and fragmented patient records across hospitals. This system addresses all three by providing real-time ML predictions, automated WHO-aligned prescriptions, and a multi-hospital patient record system with consent-based data sharing.

---

**Q3. Who are the intended users of this system?**

There are five roles:
- **System Admin** — manages users and system-wide settings
- **Hospital Admin** — manages their hospital's users and reports
- **Doctor** — creates patient records, submits diagnoses, requests lab tests, views ML predictions
- **Lab Technician** — accesses only lab test requests and uploads results
- **Pharmacist** — views only prescriptions for their hospital, approves or rejects them, manages inventory

Each role sees only what they need — nothing more.

---

**Q4. What technology stack did you use?**

- **Backend:** Python, Flask, Flask-JWT-Extended, SQLAlchemy, Flask-SocketIO
- **Frontend:** Nuxt 3 (Vue 3), Tailwind CSS
- **Machine Learning:** scikit-learn (Random Forest Classifier), pandas, NumPy, joblib
- **Database:** SQLite (default), with support for MySQL and PostgreSQL
- **Security:** Fernet symmetric encryption for PII, bcrypt password hashing, JWT authentication
- **Real-time:** WebSocket via Socket.IO for live patient list updates

---

## SECTION 2 — MACHINE LEARNING

**Q5. What ML models did you build and what do they predict?**

Two Random Forest Classifier models:
1. **TB Status Model** — predicts whether a patient has TB (Yes/No). Accuracy: **99.31%**
2. **Drug Resistance Model** — predicts the drug resistance profile of a TB case. Accuracy: **97.96%**

Both were trained on **28,191 patient records** from the synthetic TB dataset.

---

**Q6. Why did you choose Random Forest over other algorithms?**

Random Forest was chosen for four reasons:
1. It handles mixed data types (numerical like age/weight and categorical like gender/HIV status) without extensive preprocessing
2. It is robust to class imbalance — we used `class_weight='balanced'` to handle the fact that TB-positive cases are a minority
3. It provides feature importance scores, which are clinically meaningful and explainable to doctors
4. It does not overfit easily due to ensemble averaging across 300 trees

We also evaluated Logistic Regression and Decision Trees, but Random Forest gave the highest accuracy on the validation set.

---

**Q7. What are the most important features for TB prediction?**

For TB Status prediction, the top five features by importance are:
1. GeneXpert positive result — **28.48%**
2. Chest X-ray abnormal — **23.02%**
3. Sputum smear positive — **21.78%**
4. Persistent cough duration (weeks) — **6.2%**
5. Age — **5.36%**

For Drug Resistance prediction, the top feature is oxygen saturation (SpO2) at **36.86%**, followed by weight at **14.67%**. This makes clinical sense because low oxygen saturation indicates more severe disease, which correlates with drug-resistant strains.

---

**Q8. How did you handle class imbalance in the training data?**

We used `class_weight='balanced'` in the Random Forest parameters. This automatically adjusts the weight of each class inversely proportional to its frequency, so the model does not simply predict the majority class. We also used stratified train-test splitting to ensure both classes are proportionally represented in training and test sets.

---

**Q9. How does the system use ML predictions in clinical practice?**

When a doctor submits a diagnosis, the system:
1. Runs both ML models on the patient's features
2. If TB is predicted with a risk score ≥ 30, it automatically generates WHO-aligned prescriptions
3. Displays feature importance percentages so the doctor understands which factors drove the prediction
4. Classifies the patient as High, Moderate, Low, or Minimal risk
5. Triggers real-time alerts for high-risk or confirmed TB cases

---

**Q10. What is the risk score and how is it calculated?**

The risk score is a continuous 0–100 value calculated from clinical indicators:
- TB status label = Yes → +10 points
- GeneXpert positive → +8 points
- Sputum smear positive → +6 points
- Chest X-ray abnormal → +4 points
- Hemoptysis → +2 points
- Each WHO symptom (fever, cough, weight loss, night sweats, chest pain) → +1 point each

Scores ≥ 8 = High Risk, 4–7 = Medium Risk, below 4 = Low Risk. The risk score is recalculated automatically whenever a new diagnosis, prescription, or lab result is added.

---

## SECTION 3 — ANTIMICROBIAL STEWARDSHIP

**Q11. What is antimicrobial stewardship and how does your system implement it?**

Antimicrobial stewardship is the coordinated effort to improve how antibiotics are prescribed to slow the development of drug resistance. The system implements it through:
1. **Prescription Guard** — validates every prescription against the patient's antibiogram, ATC/DDD dosage standards, and pharmacy inventory before approval
2. **Misuse detection** — flags patients with 3 or more antibiotic prescriptions in 90 days, or documented self-medication
3. **Pharmacist approval workflow** — no prescription is dispensed without pharmacist review
4. **ATC/DDD tracking** — monitors antibiotic consumption in Defined Daily Doses per 100 bed-days, the WHO standard metric

---

**Q12. What is the ATC/DDD standard and why is it important?**

ATC stands for Anatomical Therapeutic Chemical classification — a WHO system that assigns every drug a unique 5-level code based on the organ it acts on and its therapeutic use. DDD (Defined Daily Dose) is the assumed average maintenance dose per day for a drug used for its main indication.

The system uses DDD to:
- Calculate how many standard doses a patient is receiving
- Compare antibiotic consumption across hospitals using a standardised unit
- Detect over-prescribing when a patient's prescribed dose exceeds 2× the DDD
- Track consumption trends over time in the dashboard

The database contains **6,996 WHO ATC/DDD drug classifications** (2026 edition).

---

**Q13. What is the cumulative antibiogram and how is it generated?**

A cumulative antibiogram is a summary of the susceptibility of bacterial isolates to antibiotics in a specific hospital or region. The system generates it automatically by:
1. Mining the **1,500 detailed multi-hospital lab results** and **10,710 antibiotic resistance records**
2. Grouping results by bacterial species and antibiotic
3. Calculating the percentage of isolates that are Susceptible (S), Intermediate (I), or Resistant (R)
4. Displaying the results as a colour-coded table in the dashboard

This helps doctors choose the most effective empirical antibiotic based on local resistance patterns before culture results are available.

---

## SECTION 4 — SYSTEM DESIGN & ARCHITECTURE

**Q14. How does the multi-hospital architecture work?**

Each user belongs to exactly one hospital. Patient records use a many-to-many relationship — a patient can be associated with multiple hospitals. Access control works as follows:
- A pharmacist at Hospital 2 sees only prescriptions with `hospital_id = Hospital 2`
- A lab technician at Hospital 2 sees only lab tests with `hospital_id = Hospital 2`
- Cross-hospital access requires OTP verification — the doctor requests an OTP, it is sent to the patient's phone via SMS, and once verified, the patient is associated with the new hospital and a consent record is created

---

**Q15. How is patient data protected?**

Three layers of protection:
1. **Encryption at rest** — all PII fields (name, phone, patient ID, symptoms, drug resistance, HIV status, diabetes) are encrypted using Fernet symmetric encryption before being stored in the database
2. **Password hashing** — all passwords are hashed with bcrypt, never stored in plain text
3. **JWT authentication** — every API request requires a valid JSON Web Token. Tokens expire after 24 hours
4. **Audit logs** — every clinical action (login, diagnosis, prescription, lab result, approval) is recorded in an immutable audit log with SHA-256 hash chaining to detect tampering

---

**Q16. What is the role-based access control (RBAC) and how is it enforced?**

RBAC is enforced at the API level using a `role_required()` decorator on every endpoint. For example:
- `POST /api/diagnose` — doctors and hospital admins only
- `GET /api/lab-tests` — lab technicians, doctors, admins (pharmacists are explicitly excluded)
- `GET /api/prescriptions` — pharmacists, doctors, admins (lab technicians are explicitly excluded)
- `POST /api/train-model` — system admin only

The frontend also hides UI elements based on role, but the backend enforces the rules independently so the restriction cannot be bypassed by manipulating the frontend.

---

**Q17. How does the real-time feature work?**

The system uses WebSocket connections via Socket.IO. When a patient record is created or updated, the server emits a `patients_update` event to all connected clients. The frontend subscribes to this event and updates the patient list without requiring a page refresh. This means if a doctor adds a new patient, all other logged-in users at the same hospital see the update immediately.

---

## SECTION 5 — WHO ALIGNMENT & CLINICAL LOGIC

**Q18. How does the system follow WHO TB treatment guidelines?**

The system implements a five-step WHO decision chain:
1. **TB detection** — classifies the patient as Confirmed PTB, Clinically Diagnosed PTB, Presumptive TB, LTBI, or No Evidence of TB based on GeneXpert, sputum smear, chest X-ray, and symptoms
2. **Bacteria assessment** — estimates the most likely MTBC species from exposure history, geography, and test results
3. **Infection assessment** — classifies pulmonary, extrapulmonary (lymph node, bone/joint, meningitis, pleural, abdominal, genitourinary), miliary, or latent TB
4. **Resistance classification** — determines DS-TB, RR-TB, MDR-TB, or XDR-TB from GeneXpert and DST results
5. **Treatment engine** — selects the correct WHO regimen (e.g., 2HRZE/4HR for DS-TB, BDQ+LZD+CFZ for MDR-TB) with correct duration, intensive phase, and continuation phase

---

**Q19. What TB bacteria species does the system support?**

The system supports all eight members of the Mycobacterium tuberculosis complex (MTBC):
- M. tuberculosis (most common, default)
- M. bovis (pyrazinamide-resistant — the system automatically removes PZA from the regimen)
- M. africanum (West Africa linkage)
- M. canettii (Horn of Africa)
- M. microti (rodent exposure)
- M. caprae (livestock exposure)
- M. pinnipedii (marine mammal exposure)
- M. orygis (South Asian linkage)

Species inference uses a combination of clinician input, exposure history keywords, geographic clues, and matching against the owner-curated species dataset.

---

**Q20. How does the system handle M. bovis differently from M. tuberculosis?**

M. bovis is naturally resistant to pyrazinamide (PZA). When the system detects M. bovis (either from clinician selection or inference from cattle/dairy exposure history), it automatically:
1. Switches the regimen from the standard 2HRZE/4HR to a pyrazinamide-sparing 2HRE/7HR regimen
2. Adds a species-specific warning in the prescription notes
3. Recommends zoonotic exposure review and reference laboratory confirmation

---

## SECTION 6 — DATA & DATASETS

**Q21. What datasets did you use and where did they come from?**

The system uses multiple datasets:
- **28,191 synthetic TB patient records** — generated to represent realistic TB clinical presentations
- **1,500 multi-hospital lab results** — detailed laboratory data across multiple facilities
- **10,710 antibiotic resistance records** — bacterial susceptibility patterns (S/I/R) for 15 antibiotics
- **6,996 WHO ATC/DDD drug classifications** — from the WHO ATC/DDD 2026 edition
- **Owner-curated species dataset** — manually labelled dataset with MTBC species, exposure history, and geographic data used for species inference
- **WHO global TB burden data** — incidence, mortality, MDR/XDR estimates by country

---

**Q22. How did you handle missing data in the patient records?**

Missing numerical values (age, weight, SpO2) are filled using the **median** of the column. Missing categorical values (gender, HIV status, smoking) are filled using the **mode** (most frequent value). This is done during the data import pipeline before records are stored in the database, ensuring the ML models always receive complete feature vectors.

---

## SECTION 7 — SECURITY & COMPLIANCE

**Q23. How does the OTP cross-hospital access work?**

When a doctor searches for a patient not registered at their hospital:
1. The doctor enters the patient's ID and clicks "Request OTP"
2. The system generates a 6-digit OTP, stores it encrypted in the database with a 5-minute expiry, and sends it to the patient's registered phone via SMS (using the HDEV Rwanda SMS gateway)
3. The patient shares the OTP with the doctor
4. The doctor enters the OTP — if valid and not expired, the patient is associated with the doctor's hospital and a `PatientConsent` record is created with `status='granted'`
5. From that point, the patient appears in the doctor's hospital's patient list

---

**Q24. What is the immutable audit log and why is it important?**

Every clinical action generates an audit log entry containing: user ID, action type, entity type, entity ID, details, timestamp, client IP, and user agent. Each entry is hashed with SHA-256 and chained to the previous entry's hash (similar to a blockchain). This means:
- If any log entry is modified, its hash will no longer match, and the chain is broken
- The system can detect tampering by verifying the hash chain
- This provides a complete, tamper-evident trail for regulatory compliance and clinical accountability

---

## SECTION 8 — CHALLENGES & LIMITATIONS

**Q25. What was the most technically challenging part of building this system?**

The most challenging part was the multi-hospital data isolation. Every query — patients, prescriptions, lab tests, diagnoses — must be filtered by `hospital_id` to prevent data leakage between hospitals. This required careful design of the hospital-scoped access control at every API endpoint, combined with the OTP consent mechanism for legitimate cross-hospital access. Getting the prescription `hospital_id` to propagate correctly through the automated diagnosis-to-prescription pipeline required several iterations.

---

**Q26. What are the current limitations of the system?**

1. **Offline capability** — the system requires an internet connection; there is no offline mode for field use
2. **SMS dependency** — the OTP cross-hospital access relies on the patient having a registered phone number and SMS delivery working
3. **Species inference accuracy** — the bacteria species inference is heuristic-based; definitive speciation requires reference laboratory culture, which the system recommends but cannot perform
4. **Training data** — the ML models were trained on synthetic data; real-world performance may differ and models should be retrained on local clinical data before deployment

---

**Q27. How would you improve the system if you had more time?**

1. **Retrain models on real clinical data** from Rwandan hospitals to improve local accuracy
2. **Add FHIR R4 full compliance** for interoperability with national health information systems
3. **Offline-first PWA** so lab technicians in remote facilities can upload results without constant connectivity
4. **Automated DST integration** — direct import of GeneXpert XML result files to eliminate manual data entry
5. **Predictive treatment outcome model** — a third ML model to predict treatment success or failure probability based on patient profile and regimen

---

## SECTION 9 — DEMONSTRATION QUESTIONS

**Q28. Can you walk us through what happens when a doctor submits a diagnosis?**

1. The doctor selects or creates a patient record with symptoms, test results, and exposure history
2. The system runs the TB Status ML model and Drug Resistance ML model
3. The WHO decision engine classifies the TB type, estimates the bacteria species, and selects the appropriate treatment regimen
4. If ML predicts TB with risk score ≥ 30, prescriptions are automatically created for each drug in the regimen with correct dosages, frequencies, and durations — all with `hospital_id` set to the doctor's hospital
5. A diagnosis record is saved, an alert is created for high-risk cases, and the patient's risk score is recalculated
6. The pharmacist at the same hospital immediately sees the new prescriptions in their pending queue

---

**Q29. What happens when a pharmacist approves a prescription?**

1. The pharmacist sees the prescription in their pending queue with stock availability shown
2. They click Approve — the system first calls the Prescription Guard to validate against resistance patterns and DDD standards
3. If warnings exist, the pharmacist is shown them and asked to confirm
4. On approval, the prescription status changes to `approved`
5. The pharmacist then clicks Dispense — the system deducts the required tablet count from the pharmacy inventory and records who dispensed it and when
6. The prescription moves to the dispense history tab

---

**Q30. How does the system support multiple languages?**

All UI text, clinical alerts, WHO recommendations, and error messages are stored in a four-language dictionary (English, French, Swahili, Kinyarwanda). The backend detects the preferred language from the `X-UI-Language` request header or the `Accept-Language` browser header and returns all text in the appropriate language. The frontend allows users to switch language from the settings panel.

---

*Total: 30 questions across 9 sections covering overview, ML, stewardship, architecture, WHO alignment, data, security, limitations, and demonstration.*
