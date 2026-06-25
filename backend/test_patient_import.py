
from app import app
from models.models import db, Patient

with app.app_context():
    db.create_all()
    print("Patient table has", Patient.query.count(), "patients")

    # Create a test patient
    test_patient = Patient(
        patient_id="TEST_PAT_001",
        first_name="John",
        last_name="Doe",
        age=30,
        gender="Male",
        symptoms="Test symptoms"
    )
    db.session.add(test_patient)
    db.session.commit()

    print("After adding test patient, count is", Patient.query.count())

    # Check if it's there
    p = Patient.query.filter_by(patient_id="TEST_PAT_001").first()
    print("Found patient:", p)
