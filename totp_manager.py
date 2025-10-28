#!/usr/bin/env python3
"""
TOTP Manager - A command-line tool for managing TOTP secrets
"""

import sqlite3
import sys
import os
import pyotp
from pathlib import Path
import getpass

# Database path
DB_PATH = Path.home() / '.totp_manager.db'


class TOTPManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the database and create table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS totp_secrets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                secret TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def add_secret(self, email, secret):
        """Add a new TOTP secret"""
        try:
            # Validate secret format
            secret = secret.replace(' ', '').upper()
            pyotp.TOTP(secret).now()  # Test if secret is valid
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO totp_secrets (email, secret) VALUES (?, ?)',
                (email, secret)
            )
            conn.commit()
            conn.close()
            print(f"✓ Successfully added TOTP secret for {email}")
            return True
        except sqlite3.IntegrityError:
            print(f"✗ Error: Email {email} already exists")
            return False
        except Exception as e:
            print(f"✗ Error: Invalid secret format - {e}")
            return False
    
    def update_secret(self, email, new_secret):
        """Update an existing TOTP secret"""
        try:
            # Validate secret format
            new_secret = new_secret.replace(' ', '').upper()
            pyotp.TOTP(new_secret).now()  # Test if secret is valid
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE totp_secrets SET secret = ?, updated_at = CURRENT_TIMESTAMP WHERE email = ?',
                (new_secret, email)
            )
            if cursor.rowcount == 0:
                print(f"✗ Error: Email {email} not found")
                conn.close()
                return False
            conn.commit()
            conn.close()
            print(f"✓ Successfully updated TOTP secret for {email}")
            return True
        except Exception as e:
            print(f"✗ Error: Invalid secret format - {e}")
            return False
    
    def delete_secret(self, email):
        """Delete a TOTP secret"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM totp_secrets WHERE email = ?', (email,))
        if cursor.rowcount == 0:
            print(f"✗ Error: Email {email} not found")
            conn.close()
            return False
        conn.commit()
        conn.close()
        print(f"✓ Successfully deleted TOTP secret for {email}")
        return True
    
    def search_emails(self, search_term):
        """Search for emails containing the search term"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, email, secret FROM totp_secrets WHERE email LIKE ? ORDER BY email',
            (f'%{search_term}%',)
        )
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_all_emails(self):
        """Get all emails from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, email, secret FROM totp_secrets ORDER BY email')
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_totp(self, secret):
        """Generate TOTP code from secret"""
        totp = pyotp.TOTP(secret)
        return totp.now()
    
    def display_results(self, results):
        """Display search results and return them for selection"""
        if not results:
            print("No matching emails found.")
            return None
        
        print("\nFound emails:")
        print("-" * 60)
        for idx, (db_id, email, secret) in enumerate(results, 1):
            print(f"{idx}. {email}")
        print("-" * 60)
        return results


def print_usage():
    """Print usage information"""
    print("""
TOTP Manager - Manage your TOTP secrets securely

Usage:
    python totp_manager.py <command> [arguments]

Commands:
    get <email|search_term>    Get TOTP code by exact email or search term
    list                       List all emails and select one to get TOTP
    add <email> <secret>       Add a new TOTP secret
    update <email> <secret>    Update an existing TOTP secret
    delete <email>             Delete a TOTP secret
    help                       Show this help message

Examples:
    python totp_manager.py get john@example.com
    python totp_manager.py get example
    python totp_manager.py list
    python totp_manager.py add john@example.com JBSWY3DPEHPK3PXP
    python totp_manager.py update john@example.com NEWBASE32SECRET
    python totp_manager.py delete john@example.com
    """)


def main():
    manager = TOTPManager()
    
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'help':
        print_usage()
    
    elif command == 'add':
        if len(sys.argv) != 4:
            print("Usage: python totp_manager.py add <email> <secret>")
            sys.exit(1)
        email = sys.argv[2]
        secret = sys.argv[3]
        manager.add_secret(email, secret)
    
    elif command == 'update':
        if len(sys.argv) != 4:
            print("Usage: python totp_manager.py update <email> <secret>")
            sys.exit(1)
        email = sys.argv[2]
        secret = sys.argv[3]
        manager.update_secret(email, secret)
    
    elif command == 'delete':
        if len(sys.argv) != 3:
            print("Usage: python totp_manager.py delete <email>")
            sys.exit(1)
        email = sys.argv[2]
        # Confirm deletion
        confirm = input(f"Are you sure you want to delete {email}? (yes/no): ")
        if confirm.lower() == 'yes':
            manager.delete_secret(email)
        else:
            print("Deletion cancelled.")
    
    elif command == 'get':
        if len(sys.argv) != 3:
            print("Usage: python totp_manager.py get <email|search_term>")
            sys.exit(1)
        search_term = sys.argv[2]
        results = manager.search_emails(search_term)
        
        if not results:
            print(f"No emails found matching '{search_term}'")
            sys.exit(1)
        
        if len(results) == 1:
            # Exact match or single result
            db_id, email, secret = results[0]
            totp_code = manager.get_totp(secret)
            print(f"\nTOTP code for {email}:")
            print(f"  {totp_code}")
        else:
            # Multiple matches, let user choose
            displayed = manager.display_results(results)
            try:
                choice = input("\nSelect email number (or press Enter to cancel): ").strip()
                if not choice:
                    print("Cancelled.")
                    sys.exit(0)
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(displayed):
                    db_id, email, secret = displayed[choice_idx]
                    totp_code = manager.get_totp(secret)
                    print(f"\nTOTP code for {email}:")
                    print(f"  {totp_code}")
                else:
                    print("Invalid selection.")
                    sys.exit(1)
            except ValueError:
                print("Invalid input.")
                sys.exit(1)
    
    elif command == 'list':
        results = manager.get_all_emails()
        if not results:
            print("No TOTP secrets stored yet.")
            sys.exit(0)
        
        displayed = manager.display_results(results)
        try:
            choice = input("\nSelect email number to get TOTP (or press Enter to cancel): ").strip()
            if not choice:
                print("Cancelled.")
                sys.exit(0)
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(displayed):
                db_id, email, secret = displayed[choice_idx]
                totp_code = manager.get_totp(secret)
                print(f"\nTOTP code for {email}:")
                print(f"  {totp_code}")
            else:
                print("Invalid selection.")
                sys.exit(1)
        except ValueError:
            print("Invalid input.")
            sys.exit(1)
    
    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)


if __name__ == '__main__':
    main()
