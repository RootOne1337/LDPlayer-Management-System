"""
Password Encryption Helper

This script encrypts passwords using Fernet (AES-128) encryption
for secure storage in config.json

Usage:
    python encrypt_password.py
    Enter password when prompted
    Copy encrypted string to config.json
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.security import SecurityManager
import getpass

def main():
    print("\n" + "="*60)
    print("  🔐 Password Encryption Helper")
    print("="*60)
    
    print("\nThis tool encrypts passwords for secure storage in config.json")
    print("Using Fernet (AES-128 + HMAC) encryption\n")
    
    try:
        # Get password
        password = getpass.getpass("Enter password to encrypt: ")
        
        if not password:
            print("❌ Error: Password cannot be empty")
            return 1
        
        # Confirm password
        password_confirm = getpass.getpass("Confirm password: ")
        
        if password != password_confirm:
            print("❌ Error: Passwords don't match")
            return 1
        
        # Initialize security manager
        print("\n⏳ Encrypting password...")
        security = SecurityManager()
        
        # Encrypt password
        encrypted = security.encrypt_password(password)
        
        # Display results
        print("\n✅ Password encrypted successfully!")
        print("\n" + "="*60)
        print("Encrypted Password:")
        print("="*60)
        print(encrypted)
        print("="*60)
        
        print("\n📋 Usage in config.json:")
        print('-'*60)
        print('''{
  "workstations": [
    {
      "id": "ws-production-1",
      "name": "Production Workstation 1",
      "host": "192.168.1.101",
      "protocol": "winrm",
      "auth": {
        "username": "admin",
        "password": "''' + encrypted + '''"
      },
      "enabled": true
    }
  ]
}''')
        print('-'*60)
        
        print("\n💡 Next Steps:")
        print("   1. Copy encrypted password above")
        print("   2. Update Server/config.json")
        print("   3. Replace 'password' field with encrypted string")
        print("   4. Save config.json")
        print("   5. Restart server")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
