#!/usr/bin/env bash
# Render build script
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py loaddata helpline/fixtures/helplines.json

# Create superuser automatically if it doesn't exist
# Reads credentials from environment variables set in Render dashboard
python manage.py shell << 'EOF'
import os
from accounts.models import User

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')

if not password:
    print("⚠️  DJANGO_SUPERUSER_PASSWORD not set — skipping superuser creation")
elif User.objects.filter(username=username).exists():
    print(f"✅ Superuser '{username}' already exists — skipping")
else:
    User.objects.create_superuser(
        username=username,
        password=password,
        role='admin'
    )
    print(f"✅ Superuser '{username}' created successfully")
EOF