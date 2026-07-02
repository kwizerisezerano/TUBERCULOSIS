"""
HDEV SMS Gateway Integration for Rwanda
https://sms-api.hdev.rw
Following the official Python documentation
"""
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

HDEV_API_ID = os.getenv("HDEV_API_ID")
HDEV_API_KEY = os.getenv("HDEV_API_KEY")


class HdevSMS:
    @staticmethod
    def send_sms(to: str, message: str, sender_id: str = "N-SMS") -> dict:
        """
        Send SMS via HDEV API - following official Python documentation
        
        Args:
            to: Recipient phone number (with country code, e.g., +250780219351)
            message: SMS content
            sender_id: Sender ID (default: INFO)
            
        Returns:
            Dictionary with response status
        """
        try:
            # Clean phone number (remove spaces, ensure + prefix)
            cleaned_to = to.replace(" ", "").replace("-", "")
            if not cleaned_to.startswith("+"):
                cleaned_to = "+" + cleaned_to

            # Remove the + for HDEV API (they expect format like 250780219351)
            cleaned_to = cleaned_to.replace("+", "")

            # Try the api_pay endpoint from PHP documentation (might have different sender ID requirements)
            url = f"https://sms-api.hdev.rw/api_pay/api/{HDEV_API_ID}/{HDEV_API_KEY}"
            
            payload = {
                'sender_id': sender_id,
                'ref': 'sms',
                'message': message,
                'tel': cleaned_to
            }

            response = requests.post(url, data=payload, timeout=30)

            # Parse response
            try:
                response_data = response.json()
                # Check if response has status field
                if isinstance(response_data, dict):
                    if response_data.get('status') == 'success':
                        return {
                            "success": True,
                            "message": "SMS sent successfully",
                            "response": response_data
                        }
                    else:
                        return {
                            "success": False,
                            "error": response_data.get('message', 'Unknown error'),
                            "response": response_data
                        }
                else:
                    return {
                        "success": False,
                        "error": "Invalid response format",
                        "response": response_data
                    }
            except:
                # If JSON parsing fails, check status code
                if response.status_code == 200:
                    return {
                        "success": True,
                        "message": "SMS sent successfully",
                        "response": response.text
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text}"
                    }

        except requests.exceptions.RequestException as e:
            print(f"Failed to send SMS via HDEV: {e}")
            return {
                "success": False,
                "error": str(e)
            }
