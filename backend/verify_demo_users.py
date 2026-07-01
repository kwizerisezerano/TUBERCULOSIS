
"""
Verify and seed the 5 demo users
"""
from app import app
from models.models import db, User, Hospital

with app.app_context():
    db.create_all()
    
    # Ensure default hospital exists
    default_hospital = Hospital.query.filter_by(name="Default Hospital").first()
    if not default_hospital:
        default_hospital = Hospital(
            hospital_id="HOSP-0001",
            name="Default Hospital",
            facility_type='Hospital',
            city='Kigali',
            region='Kigali City',
            country='Rwanda',
            bed_capacity=200
        )
        db.session.add(default_hospital)
        db.session.commit()
    
    # Define demo users as per user's request
    demo_users = [
        {
            "username": "divinekageruka",
            "email": "divinekageruka@gmail.com",
            "password": "Admin123!",
            "role": "admin"
        },
        {
            "username": "igiclarisse10",
            "email": "igiclarisse10@gmail.com",
            "password": "Admin123!",
            "role": "hospital_admin"
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
        }
    ]
    
    print("Checking and seeding demo users...")
    added = 0
    verified = 0
    
    for user_data in demo_users:
        existing = User.query.filter_by(email=user_data["email"]).first()
        if existing:
            verified += 1
            print(f"✅ Verified: {user_data['email']} ({user_data['role']})")
            continue
        
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            role=user_data['role'],
            hospital_id=default_hospital.id
        )
        user.set_password(user_data['password'])
        db.session.add(user)
        added += 1
        print(f"➕ Added: {user_data['email']} ({user_data['role']})")
    
    db.session.commit()
    
    print(f"\n📊 Summary: {verified} verified, {added} added.")
    print(f"Total users now in system: {User.query.count()}")
