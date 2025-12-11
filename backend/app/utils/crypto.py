# backend/app/utils/crypto.py

import os
from cryptography.fernet import Fernet
from fastapi import HTTPException

# --- Initialization ---

# 1. Load the Fernet encryption key from the environment
# NOTE: The key must be a 32-byte URL-safe base64 encoded string.
FERNET_KEY = os.getenv("FERNET_KEY")

if not FERNET_KEY:
    # This ensures the application fails fast if the key is missing on startup
    raise RuntimeError("FERNET_KEY environment variable must be set for encryption utilities.")

try:
    # 2. Initialize the Fernet cipher object
    fernet = Fernet(FERNET_KEY.encode())
except Exception as e:
    raise RuntimeError(f"Failed to initialize Fernet cipher: {e}")

# --- Encryption/Decryption Functions ---

def encrypt(data: str) -> str:
    """Encrypts a string using the Fernet cipher."""
    try:
        # data is a string, needs to be encoded to bytes before encryption
        return fernet.encrypt(data.encode()).decode()
    except Exception as e:
        # Log the actual error, but raise a generic one
        print(f"Encryption failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to encrypt data.")

def decrypt(data: str) -> str:
    """Decrypts a Fernet-encrypted string."""
    try:
        # data is an encrypted string (base64), needs to be encoded to bytes for decryption
        return fernet.decrypt(data.encode()).decode()
    except Exception as e:
        # Log the actual error, which might be a bad key or corrupted token
        print(f"Decryption failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to decrypt data.")

# --- End of backend/app/utils/crypto.py ---