"""
Add Workstation to Configuration

This script helps add a new workstation to config.json
with proper structure and encrypted password.

Usage:
    python add_workstation.py
    Follow the prompts
"""

import sys
import os
import json
import getpass
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.security import SecurityManager

def print_header(text):
    """Print section header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def get_input(prompt, default=None):
    """Get user input with optional default"""
    if default:
        value = input(f"{prompt} [{default}]: ").strip()
        return value if value else default
    else:
        value = input(f"{prompt}: ").strip()
        return value

def main():
    print_header("➕ Add Workstation to Configuration")
    
    print("\nThis tool will guide you through adding a new workstation")
    print("to your config.json file.\n")
    
    # Check if config.json exists
    config_path = "config.json"
    if not os.path.exists(config_path):
        print(f"❌ Error: {config_path} not found in current directory")
        print(f"   Current directory: {os.getcwd()}")
        print("\n💡 Tip: Run this script from the Server directory:")
        print("   cd Server")
        print("   python add_workstation.py")
        return 1
    
    try:
        # Load existing config
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"✅ Loaded existing config from {config_path}")
        
        # Get workstation count
        existing_count = len(config.get('workstations', []))
        print(f"ℹ️  Currently {existing_count} workstation(s) configured")
        
        # Gather workstation information
        print_header("📝 Workstation Information")
        
        ws_id = get_input("Workstation ID", f"ws-prod-{existing_count + 1}")
        ws_name = get_input("Workstation Name", f"Production Workstation {existing_count + 1}")
        ws_host = get_input("Workstation IP/Hostname", "192.168.1.101")
        ws_protocol = get_input("Protocol (winrm/ssh)", "winrm").lower()
        
        if ws_protocol not in ['winrm', 'ssh']:
            print(f"❌ Error: Invalid protocol '{ws_protocol}'. Must be 'winrm' or 'ssh'")
            return 1
        
        # Get LDPlayer path
        default_ldplayer = "C:\\Program Files\\LDPlayer\\LDPlayer4.0"
        ws_ldplayer = get_input("LDPlayer Path", default_ldplayer)
        
        # Get credentials
        print_header("🔐 Credentials")
        ws_username = get_input("Username", "admin")
        ws_password = getpass.getpass("Password: ")
        
        if not ws_password:
            print("❌ Error: Password cannot be empty")
            return 1
        
        # Confirm password
        ws_password_confirm = getpass.getpass("Confirm Password: ")
        
        if ws_password != ws_password_confirm:
            print("❌ Error: Passwords don't match")
            return 1
        
        # Encrypt password
        print("\n⏳ Encrypting password...")
        security = SecurityManager()
        encrypted_password = security.encrypt_password(ws_password)
        print("✅ Password encrypted")
        
        # Create workstation object
        new_workstation = {
            "id": ws_id,
            "name": ws_name,
            "host": ws_host,
            "protocol": ws_protocol,
            "ldplayer_path": ws_ldplayer,
            "auth": {
                "username": ws_username,
                "password": encrypted_password
            },
            "enabled": True,
            "added_at": datetime.utcnow().isoformat() + "Z"
        }
        
        # Preview
        print_header("👀 Preview")
        print(json.dumps(new_workstation, indent=2))
        
        # Confirm
        print("\n❓ Add this workstation to config.json? (y/n): ", end='')
        response = input().strip().lower()
        
        if response != 'y':
            print("⚠️  Operation cancelled")
            return 0
        
        # Add to config
        if 'workstations' not in config:
            config['workstations'] = []
        
        config['workstations'].append(new_workstation)
        
        # Backup existing config
        backup_path = f"config.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✅ Backup created: {backup_path}")
        
        # Save updated config
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Workstation added to {config_path}")
        
        # Summary
        print_header("🎉 Success!")
        print(f"\nWorkstation '{ws_name}' added successfully!")
        print(f"Total workstations: {len(config['workstations'])}")
        
        print("\n📋 Next Steps:")
        print(f"   1. Verify WinRM is enabled on {ws_host}")
        print("   2. Test connection:")
        print("      python test_winrm_connection.py")
        print("   3. Start server in production mode:")
        print("      python run_server_stable.py")
        print("   4. Check UI for real emulators!")
        print("      http://localhost:3000")
        
        return 0
        
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {config_path}")
        print(f"   {str(e)}")
        return 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
