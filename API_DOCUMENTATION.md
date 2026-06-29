# TB Predictive EHR - API Documentation

## Role-Based Healthcare Workflows

### Pharmacist Workflow

#### 1. Pharmacy Inventory Management

**GET /api/pharmacy-inventory**
- **Description:** Get all pharmacy inventory items
- **Roles:** pharmacist, admin, hospital_admin
- **Query Params:** `hospital_id` (optional) - Filter by hospital
- **Response:**
```json
{
  "inventory": [
    {
      "id": 1,
      "hospital_id": 1,
      "atc_drug_id": 5,
      "atc_drug": {
        "id": 5,
        "drug_name": "Isoniazid",
        "atc_code": "J01AC01"
      },
      "stock_quantity": 500,
      "unit_type": "tablets",
      "batch_number": "BATCH-001",
      "expiry_date": "2026-12-31",
      "location": "Shelf A1",
      "minimum_stock_level": 10,
      "last_restocked": "2026-06-29T10:00:00"
    }
  ],
  "total": 1
}
```

**POST /api/pharmacy-inventory**
- **Description:** Create new inventory item
- **Roles:** pharmacist, admin, hospital_admin
- **Request Body:**
```json
{
  "hospital_id": 1,
  "atc_drug_id": 5,
  "stock_quantity": 500,
  "unit_type": "tablets",
  "batch_number": "BATCH-001",
  "expiry_date": "2026-12-31",
  "location": "Shelf A1",
  "minimum_stock_level": 10
}
```

**PUT /api/pharmacy-inventory/<inventory_id>**
- **Description:** Update inventory item
- **Roles:** pharmacist, admin, hospital_admin
- **Request Body:**
```json
{
  "stock_quantity": 450,
  "location": "Shelf A2"
}
```

**DELETE /api/pharmacy-inventory/<inventory_id>**
- **Description:** Delete inventory item
- **Roles:** admin only

---

#### 2. Prescription Stock Check

**GET /api/prescriptions/<presc_id>/check-stock**
- **Description:** Check if medication is available in stock
- **Roles:** pharmacist, admin, hospital_admin
- **Response:**
```json
{
  "available": true,
  "stock_quantity": 500,
  "required_quantity": 30,
  "drug_name": "Isoniazid",
  "below_minimum": false
}
```

---

#### 3. Prescription Approval & Dispensing

**PUT /api/prescriptions/<presc_id>**
- **Description:** Update prescription status (approve/reject)
- **Roles:** pharmacist, admin, hospital_admin
- **Request Body:**
```json
{
  "status": "approved",
  "rejection_reason": "Drug not available"
}
```

**POST /api/prescriptions/<presc_id>/dispense**
- **Description:** Dispense medication to patient (auto-updates stock)
- **Roles:** pharmacist only
- **Response:**
```json
{
  "id": 1,
  "status": "dispensed",
  "dispensed_by": 3,
  "dispensed_at": "2026-06-29T12:00:00",
  "stock_updated": true
}
```

---

### Lab Technician Workflow

#### 1. View Pending Tests

**GET /api/lab-tests/pending**
- **Description:** Get all pending lab test requests
- **Roles:** lab_technician only
- **Response:**
```json
{
  "pending_tests": [
    {
      "id": 1,
      "patient_id": 5,
      "test_type": "Sputum Smear Microscopy",
      "status": "requested",
      "requested_by": 2,
      "created_at": "2026-06-29T08:00:00"
    }
  ],
  "total": 1
}
```

---

#### 2. Submit Lab Results

**POST /api/lab-tests/<test_id>/submit-result**
- **Description:** Submit completed lab test results
- **Roles:** lab_technician only
- **Request Body:**
```json
{
  "results": "Positive",
  "notes": "AFB detected in sputum sample"
}
```
- **Response:**
```json
{
  "id": 1,
  "status": "completed",
  "results": "Positive",
  "notes": "AFB detected in sputum sample",
  "completed_by": 4,
  "completed_at": "2026-06-29T10:30:00"
}
```

---

### Doctor Workflow

#### 1. View Patient Lab Results

**GET /api/lab-tests?patient_id=<patient_id>**
- **Description:** Get all lab tests for a patient
- **Roles:** doctor, admin, hospital_admin, lab_technician
- **Response:**
```json
{
  "lab_tests": [
    {
      "id": 1,
      "patient_id": 5,
      "test_type": "Sputum Smear Microscopy",
      "status": "completed",
      "results": "Positive",
      "completed_by": 4,
      "completed_at": "2026-06-29T10:30:00"
    }
  ]
}
```

---

#### 2. Diagnosis with Lab Results

**POST /api/diagnose**
- **Description:** Run diagnosis with patient data
- **Roles:** doctor, admin, hospital_admin
- **Request Body:**
```json
{
  "patient": {
    "patient_id": "P001",
    "age": 35,
    "gender": "male",
    "sputum_smear_test": "Positive",
    "genexpert_test": "Positive",
    "chest_xray": "Abnormal",
    "has_fever": "Yes",
    "has_cough": "Yes"
  }
}
```

---

## Authentication

All endpoints require JWT authentication. Include token in header:

```
Authorization: Bearer <your_jwt_token>
```

---

## Error Responses

**403 Forbidden**
```json
{
  "msg": "Access denied"
}
```

**400 Bad Request**
```json
{
  "error": "Prescription must be approved before dispensing"
}
```

**404 Not Found**
```json
{
  "error": "Resource not found"
}
```

---

## Frontend Routes

- **Pharmacist Dashboard:** `/pharmacist`
- **Lab Technician Dashboard:** `/lab-technician`
- **Doctor Diagnosis:** `/diagnose`
- **Healthcare Facilities:** `/hospitals`

---

## Role-Based Access

| Endpoint | Admin | Doctor | Pharmacist | Lab Tech | Hospital Admin |
|----------|-------|--------|------------|----------|----------------|
| /api/pharmacy-inventory | ✅ | ❌ | ✅ | ❌ | ✅ |
| /api/prescriptions/*/check-stock | ✅ | ❌ | ✅ | ❌ | ✅ |
| /api/prescriptions/*/dispense | ❌ | ❌ | ✅ | ❌ | ❌ |
| /api/lab-tests/pending | ❌ | ❌ | ❌ | ✅ | ❌ |
| /api/lab-tests/*/submit-result | ❌ | ❌ | ❌ | ✅ | ❌ |
| /api/diagnose | ✅ | ✅ | ❌ | ❌ | ✅ |
