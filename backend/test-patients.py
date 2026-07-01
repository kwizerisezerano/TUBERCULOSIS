
import sys
print("Python version:", sys.version)
try:
    import os
    os.environ["BOOTSTRAP_RUNNING"] = "1"
    print("Importing app...")
    from app import app
    print("Importing models...")
    from models.models import db, Patient
    print("Setting up app context...")
    with app.app_context():
        print("Querying patients...")
        patient_count = Patient.query.count()
        print(f"Total patients: {patient_count}")
        
        if patient_count >0:
            print("First patient:")
            p = Patient.query.first()
            print(f"  id: {p.id}")
            print(f"  _patient_id: {repr(p._patient_id)}")
            print("Trying to get patient_id:")
            try:
                patient_id_decrypted = p.patient_id
                print(f"  patient_id decrypted: {patient_id_decrypted}")
            except Exception as e:
                print(f"Error decrypting patient_id: {type(e)} - {e}")
                
            print(f"  first_name: {repr(p._first_name)}, decrypted: {p.first_name}")
            print(f"  last_name: {repr(p._last_name)}, decrypted: {p.last_name}")
            
            # Set password
            print("Setting password for all patients...")
            patients = Patient.query.all()
            for patient in patients:
                if not patient.password:
                    patient.set_password("Patient123!")
                    db.session.add(patient)
            db.session.commit()
            print("Passwords set!")
        
        else:
            print("No patients found!")
            
except Exception as e:
    print("ERROR:", type(e))
    print(e)
    import traceback
    traceback.print_exc()
