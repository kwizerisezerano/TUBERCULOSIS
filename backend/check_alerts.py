
import sys

original_name = __name__
__name__ = 'not_main'

from app import app, db
from models.models import Alert

__name__ = original_name

with app.app_context():
    total_alerts = Alert.query.count()
    print(f'Total alerts in database: {total_alerts}')
    
    if total_alerts > 0:
        print("\nFirst 10 alerts:")
        alerts = Alert.query.limit(10).all()
        for a in alerts:
            print(f'  ID: {a.id}, Hospital: {a.hospital_id}, Type: {a.alert_type}, Severity: {a.severity}, Read: {a.is_read}')
    else:
        print("\nNo alerts found in the database.")
