#!/usr/bin/env python3
"""
Password Management Utility for Arthvidya Monopoly
This script helps you manage team passwords securely
"""

import random
import string
import json
import os
from datetime import datetime

def generate_secure_password(length=12):
    """Generate a secure random password"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def generate_team_passwords():
    """Generate secure passwords for all teams"""
    passwords = {}
    
    # Generate passwords
    passwords["Control Center"] = generate_secure_password(16)
    passwords["Team 1"] = generate_secure_password(12)
    passwords["Team 2"] = generate_secure_password(12)
    passwords["Team 3"] = generate_secure_password(12)
    passwords["Team 4"] = generate_secure_password(12)
    passwords["Team 5"] = generate_secure_password(12)
    
    return passwords

def save_passwords_to_file(passwords, filename="team_passwords.json"):
    """Save passwords to a JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(passwords, f, indent=2)
        print(f"✅ Passwords saved to {filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving passwords: {e}")
        return False

def load_passwords_from_file(filename="team_passwords.json"):
    """Load passwords from a JSON file"""
    try:
        with open(filename, 'r') as f:
            passwords = json.load(f)
        print(f"✅ Passwords loaded from {filename}")
        return passwords
    except Exception as e:
        print(f"❌ Error loading passwords: {e}")
        return None

def display_passwords(passwords):
    """Display passwords in a formatted way"""
    print("\n🔑 TEAM PASSWORDS:")
    print("=" * 50)
    
    for team, password in passwords.items():
        print(f"{team:15}: {password}")
    
    print("=" * 50)

def create_password_config(passwords):
    """Create a Python config file with passwords"""
    config_content = f'''# Password Configuration for Arthvidya Monopoly
# Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

TEAM_PASSWORDS = {repr(passwords)}

# Security Notes:
# - These passwords are randomly generated
# - Keep them secure and don't share publicly
# - Each team should only know their own password
# - Control Center password should be kept secret
'''
    
    try:
        with open("password_config.py", 'w') as f:
            f.write(config_content)
        print("✅ Password config file created: password_config.py")
        return True
    except Exception as e:
        print(f"❌ Error creating config file: {e}")
        return False

def main():
    """Main password management function"""
    print("🔐 Password Management Utility")
    print("=" * 40)
    
    while True:
        print("\n📋 Options:")
        print("1. Generate new secure passwords")
        print("2. Load existing passwords")
        print("3. Display current passwords")
        print("4. Save passwords to file")
        print("5. Create password config file")
        print("6. Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == "1":
            print("\n🔄 Generating new secure passwords...")
            passwords = generate_team_passwords()
            display_passwords(passwords)
            
            save_choice = input("\nSave these passwords? (y/n): ").strip().lower()
            if save_choice == 'y':
                save_passwords_to_file(passwords)
                create_password_config(passwords)
        
        elif choice == "2":
            filename = input("Enter filename (default: team_passwords.json): ").strip()
            if not filename:
                filename = "team_passwords.json"
            
            passwords = load_passwords_from_file(filename)
            if passwords:
                display_passwords(passwords)
        
        elif choice == "3":
            # Try to load from default file
            passwords = load_passwords_from_file()
            if passwords:
                display_passwords(passwords)
            else:
                print("❌ No password file found. Generate new passwords first.")
        
        elif choice == "4":
            filename = input("Enter filename (default: team_passwords.json): ").strip()
            if not filename:
                filename = "team_passwords.json"
            
            # Try to load existing passwords
            passwords = load_passwords_from_file()
            if not passwords:
                print("❌ No passwords loaded. Generate new passwords first.")
                continue
            
            save_passwords_to_file(passwords, filename)
        
        elif choice == "5":
            # Try to load existing passwords
            passwords = load_passwords_from_file()
            if not passwords:
                print("❌ No passwords loaded. Generate new passwords first.")
                continue
            
            create_password_config(passwords)
        
        elif choice == "6":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main()
