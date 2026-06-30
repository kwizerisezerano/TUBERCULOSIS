
import sys

original_name = __name__
__name__ = 'not_main'

from app import app, db
from models.models import Hospital, User

__name__ = original_name

with app.app_context():
    print('=== ASSIGNING USERS TO HOSPITALS ===')
    
    # Get all hospitals
    hospitals = Hospital.query.all()
    print(f'Total hospitals: {len(hospitals)}')
    
    # Get all users
    users = User.query.all()
    print(f'Total users: {len(users)}')
    
    # Assign each user to a hospital
    for i, user in enumerate(users):
        # Pick a hospital (cycle through them)
        hospital = hospitals[i % len(hospitals)]
        user.hospital_id = hospital.id
        db.session.add(user)
        print(f'  {user.username} ({user.role}) → {hospital.name}')
    
    db.session.commit()
    
    print('\n✅ Done! All users assigned to hospitals.')
