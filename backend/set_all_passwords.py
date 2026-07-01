
import os
os.environ["BOOTSTRAP_RUNNING"] = "1"
print("Starting password reset script...", flush=True)

# Add some simple error catching
try:
    from app import app
    print("Imported app successfully", flush=True)

    from models.models import db, Patient
    print("Imported Patient model successfully", flush=True)

    with app.app_context():
        print("App context created", flush=True)
        
        db.create_all()
        print("DB create_all() done", flush=True)
        
        all_patients = Patient.query.all()
        print(f"Found {len(all_patients)} patients!", flush=True)
        
        for i, patient in enumerate(all_patients):
            patient.set_password("Patient123!")
            db.session.add(patient)
            
            if (i + 1) % 1000 == 0:
                print(f"Processed {i+1} patients...", flush=True)
                
        db.session.commit()
        print("ALL PATIENTS DONE! All passwords set to Patient123!", flush=True)
        
except Exception as e:
    print(f"ERROR: {e}", flush=True)
    import traceback
    print(traceback.format_exc(), flush=True)
