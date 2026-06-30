
"""
Security utilities for encryption and password hashing
"""
import os
import bcrypt
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

# Generate or load encryption key
def get_or_create_key():
    key_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'encryption_key.key')
    if os.path.exists(key_path):
        with open(key_path, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(key_path, 'wb') as f:
            f.write(key)
        return key

ENCRYPTION_KEY = get_or_create_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

def encrypt_data(data):
    """Encrypt sensitive data"""
    if not data:
        return None
    data_bytes = data.encode('utf-8')
    encrypted = cipher_suite.encrypt(data_bytes)
    return encrypted.decode('utf-8')

def decrypt_data(encrypted_data):
    """Decrypt sensitive data"""
    if not encrypted_data:
        return None
    try:
        encrypted_bytes = encrypted_data.encode('utf-8')
        decrypted = cipher_suite.decrypt(encrypted_bytes)
        return decrypted.decode('utf-8')
    except Exception:
        # If decryption fails (data is plaintext or invalid), return it as-is
        return encrypted_data

def hash_password(password):
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password, hashed_password):
    """Verify a password against a bcrypt hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
