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

print(f"DEBUG: username='{username}'")
print(f"DEBUG: email='{email}'")
print(f"DEBUG: password set={'YES' if password else 'NO'}")

if not password:
    print("WARNING: DJANGO_SUPERUSER_PASSWORD not set - skipping")
else:
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.role = 'admin'
        user.save()
        # Verify saved correctly
        user.refresh_from_db()
        print(f"DEBUG: is_staff={user.is_staff}")
        print(f"DEBUG: is_superuser={user.is_superuser}")
        print(f"DEBUG: is_active={user.is_active}")
        print(f"DEBUG: password_check={user.check_password(password)}")
        print(f"SUCCESS: Superuser '{username}' updated")
    else:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.role = 'admin'
        user.save()
        print(f"DEBUG: is_staff={user.is_staff}")
        print(f"DEBUG: is_superuser={user.is_superuser}")
        print(f"DEBUG: is_active={user.is_active}")
        print(f"DEBUG: password_check={user.check_password(password)}")
        print(f"SUCCESS: Superuser '{username}' created")
EOF
