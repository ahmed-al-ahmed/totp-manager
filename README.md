# Add a new secret
python totp_manager.py add john@example.com JBSWY3DPEHPK3PXP

# Get TOTP by exact email
python totp_manager.py get john@example.com

# Search for partial email (shows matches to select from)
python totp_manager.py get example

# List all emails and select one
python totp_manager.py list

# Update a secret
python totp_manager.py update john@example.com NEWBASE32SECRET

# Delete a secret
python totp_manager.py delete john@example.com
