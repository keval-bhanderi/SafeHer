# ── Stage 1: Builder ──────────────────────────────────────────────────────────
# Install dependencies in a separate stage so final image stays small
FROM python:3.12-slim AS builder

# Prevent .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies needed to compile psycopg2 / mysqlclient / Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libmariadb-dev-compat \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages into a local directory (not system-wide)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt


# ── Stage 2: Runtime ──────────────────────────────────────────────────────────
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=safeher.settings \
    PORT=8000

WORKDIR /app

# Only the runtime libraries needed (no gcc/dev headers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libmariadb3 \
    libjpeg62-turbo \
    zlib1g \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

# Copy project source code
COPY . .

# Create a non-root user with a proper home directory
RUN addgroup --system django && \
    adduser --system --ingroup django --home /home/django --shell /bin/bash django && \
    mkdir -p /home/django && \
    chown -R django:django /app /home/django

USER django

# Set home directory explicitly so Gunicorn can write temp files
ENV HOME=/home/django

# Collect static files at build time
RUN python manage.py collectstatic --no-input

# Expose the port Gunicorn will listen on
EXPOSE 8000

# Healthcheck — Docker will mark container unhealthy if /accounts/login/ stops responding
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/accounts/login/')" || exit 1

# Run migrations, load fixtures, create superuser, start Gunicorn
CMD ["sh", "-c", "python manage.py migrate && python manage.py loaddata helpline/fixtures/helplines.json || true && python manage.py shell -c \"\nimport os\nfrom accounts.models import User\nusername = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')\nemail = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@safeher.com')\npassword = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')\nif password:\n    user, created = User.objects.get_or_create(username=username, defaults={'email': email})\n    user.set_password(password)\n    user.is_staff = True\n    user.is_superuser = True\n    user.is_active = True\n    user.role = 'admin'\n    user.save()\n    print('Superuser ready:', username)\n\" && gunicorn safeher.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --worker-tmp-dir /tmp"]
