"""
Test HDEV SMS Gateway directly
"""
import os
os.environ["BOOTSTRAP_RUNNING"] = "1"
from sms.hdev_sms import HdevSMS

# Test with a real Rwandan phone number
test_phone = "+250790989830"
test_message = "This is a test message from TB Diagnostic System"

print(f"Testing HDEV SMS Gateway...")
print(f"Phone: {test_phone}")
print(f"Message: {test_message}")
print("-" * 50)

result = HdevSMS.send_sms(test_phone, test_message)

print(f"Success: {result.get('success')}")
print(f"Message: {result.get('message')}")
if not result.get('success'):
    print(f"Error: {result.get('error')}")
print(f"Full Response: {result.get('response')}")
