"""
Hubtel SMS Gateway Integration
"""
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

HUBTEL_API_ID = os.getenv("HUBTEL_API_ID")
HUBTEL_API_KEY = os.getenv("HUBTEL_API_KEY")
HUBTEL_BASE_URL = "https://sms.hubtel.com/v1/messages"


class HubtelSMS:
    @staticmethod
    def send_sms(to: str, message: str, sender_id: str = "TB-SYSTEM") -> dict:
        """
        Send SMS via Hubtel API
        
        Args:
            to: Recipient phone number (with country code, e.g., +250780219351)
            message: SMS content
            sender_id: Sender ID (optional)
            
        Returns:
            Dictionary with response status
        """
        try:
            # Clean phone number (remove spaces, ensure + prefix)
            cleaned_to = to.replace(" ", "").replace("-", "")
            if not cleaned_to.startswith("+"):
                cleaned_to = "+" + cleaned_to

            payload = {
                "from": sender_id,
                "to": cleaned_to,
                "content": message
            }

            response = requests.post(
                HUBTEL_BASE_URL,
                json=payload,
                auth=(HUBTEL_API_ID, HUBTEL_API_KEY),
                timeout=30
            )

            response.raise_for_status()

            return {
                "success": True,
                "message": "SMS sent successfully",
                "response": response.json()
            }

        except requests.exceptions.RequestException as e:
            print(f"Failed to send SMS: {e}")
            return {
                "success": False,
                "error": str(e)
            }
