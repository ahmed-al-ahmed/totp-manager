## Installation
```shell
python -m venv venv .
source ./venv/bin/activate
pip install -r requirements.txt
```

#### Add a new secret
```shell
python totp_manager.py add john@example.com JBSWY3DPEHPK3PXP
```

#### Get TOTP by exact email
```shell
python totp_manager.py get john@example.com
```

#### Search for partial email (shows matches to select from)
```shell
python totp_manager.py get example
````

#### List all emails and select one
```shell
python totp_manager.py list
```

#### Update a secret
```shell
python totp_manager.py update john@example.com NEWBASE32SECRET
```

#### Delete a secret
```shell
python totp_manager.py delete john@example.com
```
