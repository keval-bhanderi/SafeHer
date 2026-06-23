#!/usr/bin/env bash
# Render build script
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py loaddata helpline/fixtures/helplines.json

# Create OR update superuser from environment variables
python manage.py shell << 'EOF'
import os
from accounts.models import User

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@safeher.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')

if not password:
    print("WARNING: DJANGO_SUPERUSER_PASSWORD not set - skipping")
else:
    if User.objects.filter(username=username).exists():
        # Update existing user - reset password and ensure is_staff/is_superuser
        user = User.objects.get(username=username)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.role = 'admin'
        user.save()
        print(f"SUCCESS: Superuser '{username}' password reset and permissions updated")
    else:
        # Create new superuser
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        user.role = 'admin'
        user.save()
        print(f"SUCCESS: Superuser '{username}' created successfully")
EOF
