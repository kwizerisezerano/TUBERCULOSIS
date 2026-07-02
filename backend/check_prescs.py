from app import app
from models.models import db, Prescription, User, Hospital
app.app_context().push()
for p in Prescription.query.all():
    creator = User.query.filter_by(id=p.created_by).first()
    h = Hospital.query.filter_by(id=p.hospital_id).first()
    print(f'presc id={p.id} {p.medication} hospital_id={p.hospital_id} ({h.name if h else "?"}) created_by={p.created_by} ({creator.username if creator else "?"} hospital_id={creator.hospital_id if creator else "?"})')
