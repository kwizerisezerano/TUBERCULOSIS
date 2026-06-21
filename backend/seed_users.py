
"""
Seed the database with users and roles
"""
from app import app
from models.models import db, User

users = [
    {
        "username": "divinekageruka",
        "email": "divinekageruka@gmail.com",
        "password": "Admin123!",
        "role": "system_admin"
    },
    {
        "username": "igiranezac459",
        "email": "igiranezac459@gmail.com",
        "password": "Doctor123!",
        "role": "doctor"
    },
    {
        "username": "clarisseigiraneza56",
        "email": "clarisseigiraneza56@gmail.com",
        "password": "LabTech123!",
        "role": "lab_technician"
    },
    {
        "username": "clarisseigiraneza915",
        "email": "clarisseigiraneza915@gmail.com",
        "password": "Pharm123!",
        "role": "pharmacist"
    },
    {
        "username": "igiclarisse10",
        "email": "igiclarisse10@gmail.com",
        "password": "Admin123!",
        "role": "hospital_admin"
    }
]

def seed_users():
    with app.app_context():
        db.create_all()
        
        added = 0
        
        for user_data in users:
            existing = None
            for u in User.query.all():
                if u.email == user_data["email"]:
                    existing = u
                    break
            if existing:
                continue
            
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                role=user_data['role']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            added += 1
        
        db.session.commit()
        return {"added": added, "total": User.query.count()}
        
if __name__ == "__main__":
    result = seed_users()
    print(result)
