
import sys

original_name = __name__
__name__ = 'not_main'

from app import app, db
from models.models import LabTest

__name__ = original_name

with app.app_context():
    total_tests = LabTest.query.count()
    completed_tests = LabTest.query.filter_by(status='completed').count()
    requested_tests = LabTest.query.filter_by(status='requested').count()
    in_progress_tests = LabTest.query.filter_by(status='in_progress').count()
    
    print(f'Total lab tests in database: {total_tests}')
    print(f'Completed lab tests: {completed_tests}')
    print(f'Requested lab tests: {requested_tests}')
    print(f'In progress lab tests: {in_progress_tests}')
    
    if completed_tests > 0:
        print("\nFirst 5 completed lab tests:")
        tests = LabTest.query.filter_by(status='completed').limit(5).all()
        for t in tests:
            print(f'  ID: {t.id}, Type: {t.test_type}, Result: {t.results}, Patient: {t.patient_id}')
