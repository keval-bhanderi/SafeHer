# 🛡️ SafeHer — Women Safety Alert System
> A full-stack Django web app + REST API for women's safety

---

## 🚀 Quick Start

### 1. Clone & Setup Environment
```bash
git clone <your-repo>
cd safeher
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Apply Migrations
```bash
python manage.py migrate
python manage.py loaddata helpline/fixtures/helplines.json
```

### 3. Create Superuser
```bash
python manage.py createsuperuser
```

### 4. Run Server
```bash
python manage.py runserver
```

Open: http://127.0.0.1:8000

---

## 🔑 Default Admin Login
- URL: http://127.0.0.1:8000/admin/
- Username: `admin`
- Password: `admin123`

---

## 📦 Features

| Feature | Web | API |
|---|---|---|
| User Registration & Login | ✅ | ✅ |
| Emergency Contacts (up to 5) | ✅ | ✅ |
| One-Click SOS Alert | ✅ | ✅ |
| GPS Location Sharing | ✅ | ✅ |
| Email Notifications | ✅ | ✅ |
| SMS Notifications | ⚠️ See note | ⚠️ See note |
| Live Map (Leaflet.js) | ✅ | — |
| Nearby Police / NGO Finder | ✅ | ✅ |
| Helplines Directory | ✅ | ✅ |
| Alert History | ✅ | ✅ |
| Admin/NGO Dashboard | ✅ | — |
| JWT Auth for Mobile | — | ✅ |

> **SMS note:** The full SMS pipeline is implemented (Fast2SMS integration, message formatting, delivery logging). However, Fast2SMS's free tier restricts the default "Quick SMS" route to the account holder's own verified number — sending to arbitrary emergency contacts requires **DLT registration** (a telecom compliance process mandatory in India for transactional SMS). Without a DLT-approved sender ID, SMS calls will fail with a 400 error while email notifications continue working normally. See [SMS Configuration](#-sms-configuration--known-limitation) below for details.

---

## 🌐 API Endpoints

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/api/v1/auth/register/` | POST | No | Register user |
| `/api/v1/auth/login/` | POST | No | Login, get JWT |
| `/api/v1/auth/refresh/` | POST | No | Refresh token |
| `/api/v1/auth/profile/` | GET/PUT | JWT | View/update profile |
| `/api/v1/contacts/` | GET/POST | JWT | List/add contacts |
| `/api/v1/contacts/<id>/` | PUT/DELETE | JWT | Edit/delete contact |
| `/api/v1/alerts/trigger/` | POST | JWT | Trigger SOS alert |
| `/api/v1/alerts/history/` | GET | JWT | Alert history |
| `/api/v1/alerts/<id>/resolve/` | POST | JWT | Resolve alert |
| `/api/v1/alerts/<id>/location/` | POST | JWT | Update live location |
| `/api/v1/nearby/` | GET | JWT | Nearby police/NGO |
| `/api/v1/helplines/` | GET | JWT | Helplines list |

### Example: Trigger SOS via API
```bash
curl -X POST http://localhost:8000/api/v1/alerts/trigger/ \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"latitude": 23.0225, "longitude": 72.5714, "message": "Need help!"}'
```

---

## 📲 SMS Configuration & Known Limitation

SafeHer sends two types of SOS notifications: **Email** (fully functional out of the box) and **SMS** (functional in code, but gated by a third-party compliance requirement).

### Current behavior

| Scenario | What happens |
|---|---|
| `FAST2SMS_API_KEY` left as default placeholder | SMS runs in **mock mode** — logs the message to console instead of sending, so the flow can still be tested/demoed without cost |
| Real Fast2SMS API key set, sending to your own verified number | ✅ Works on the free "Quick SMS" route |
| Real Fast2SMS API key set, sending to **any other number** (e.g. a real emergency contact) | ❌ Fails with `HTTP 400 Bad Request` |

### Why this happens

India regulates transactional/promotional SMS through **DLT (Distributed Ledger Technology) registration** — a mandatory telecom compliance process for any sender wanting to message numbers other than their own. Fast2SMS's free "Quick SMS" route intentionally restricts delivery to the account holder's own verified number to prevent spam abuse without DLT registration.

### How to enable real SMS delivery to any contact

1. Complete **DLT registration** as an entity/individual via your telecom's DLT portal (Jio/Airtel/Vodafone) or through Fast2SMS's partnered DLT service — typically takes a few business days
2. Get your SMS message template pre-approved under DLT
3. Add wallet balance to your Fast2SMS account (the free Quick route no longer applies once you're on the Transactional route)
4. In `notifications/utils.py`, change the route from `"q"` (Quick) to `"t"` (Transactional) and include your DLT-approved `sender_id` and `template_id` in the payload — see [Fast2SMS DLT docs](https://www.fast2sms.com/docs) for the exact payload format required for the Transactional route

### Recommended approach for demos/portfolios

Given the compliance overhead, email is the recommended primary channel for demoing this project. The SMS code path is complete and production-ready architecturally — it's the external registration requirement, not application code, that gates full delivery to arbitrary numbers.

---

## 🗄️ Database Configuration

By default, the project uses **SQLite** — zero setup needed.

To use **PostgreSQL**, **MySQL**, or any other database:

1. Copy `.env.example` to `.env`
2. Uncomment/edit the `DATABASE_URL` line for your database:

```env
# PostgreSQL
DATABASE_URL=postgres://USER:PASSWORD@HOST:5432/safeher_db

# MySQL
DATABASE_URL=mysql://USER:PASSWORD@HOST:3306/safeher_db
```

3. Install the matching driver:
```bash
pip install psycopg2-binary   # for PostgreSQL
pip install mysqlclient       # for MySQL
```

4. Re-run migrations:
```bash
python manage.py migrate
python manage.py loaddata helpline/fixtures/helplines.json
python manage.py createsuperuser
```

No code changes needed — `settings.py` reads `DATABASE_URL` automatically via `django-environ`, falling back to SQLite if not set.

---

## ⚙️ Configuration (.env file)

Copy `.env.example` → `.env` and fill in:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
FAST2SMS_API_KEY=your-fast2sms-api-key
```



## 📁 Project Structure

```
safeher/
├── accounts/        # Custom user model, auth views
├── alerts/          # SOS alert trigger, history, resolve
├── contacts/        # Emergency contacts CRUD
├── nearby/          # Police/NGO/Hospital finder with map
├── helpline/        # National helplines directory
├── notifications/   # SMS + Email notification engine
├── dashboard/       # User dashboard + Admin panel
├── api/             # Full Django REST Framework API
├── templates/       # All HTML templates
└── safeher/         # Project settings and URLs
```

---

## 📱 REST API Usage (for Mobile App)

### Login and store JWT:
```javascript
const res = await fetch('/api/v1/auth/login/', {
  method: 'POST',
  body: JSON.stringify({ username: 'user', password: 'pass' })
});
const { access, refresh } = await res.json();
```

### Trigger SOS with location:
```javascript
navigator.geolocation.getCurrentPosition(async (pos) => {
  await fetch('/api/v1/alerts/trigger/', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${access}` },
    body: JSON.stringify({
      latitude: pos.coords.latitude,
      longitude: pos.coords.longitude
    })
  });
});
```

---

## 🛠️ Tech Stack

- **Backend:** Django 6.x + Django REST Framework
- **Auth:** JWT (djangorestframework-simplejwt)
- **Maps:** Leaflet.js + OpenStreetMap (free, no API key)
- **SMS:** Fast2SMS (India free tier)
- **Email:** Gmail SMTP
- **Frontend:** Bootstrap 5 + Font Awesome
- **DB:** SQLite (dev) → PostgreSQL (production)

---

## 🚢 Deploy to Render

### Option A: One-Click Blueprint (Recommended)

1. Push this project to a GitHub repository
2. Go to [render.com](https://render.com) → New → **Blueprint**
3. Connect your GitHub repo — Render detects `render.yaml` automatically
4. It will provision:
   - A **Web Service** (Django app, free tier)
   - A **PostgreSQL Database** (free tier)
5. Add your secret env vars when prompted: `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `FAST2SMS_API_KEY`
6. Click **Apply** — Render builds and deploys automatically

### Option B: Manual Setup

1. **Create a PostgreSQL database** on Render → New → PostgreSQL → copy the "Internal Database URL"

2. **Create a Web Service** → New → Web Service → connect your repo
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn safeher.wsgi:application`

3. **Add Environment Variables** in the Render dashboard:
   ```
   SECRET_KEY=<generate a random secret>
   DEBUG=False
   DATABASE_URL=<paste internal database URL from step 1>
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-gmail-app-password
   FAST2SMS_API_KEY=your-fast2sms-key
   ```
   Render auto-sets `RENDER_EXTERNAL_HOSTNAME`, which `settings.py` uses to whitelist your live domain automatically.

4. Click **Create Web Service** — Render runs `build.sh` (installs deps, collects static, migrates, loads helpline fixtures) then starts Gunicorn.

5. Visit your live URL: `https://safeher.onrender.com` (or your chosen name)

6. Create a superuser on the live server via Render's **Shell** tab:
   ```bash
   python manage.py createsuperuser
   ```

### Notes
- Free tier Render web services **spin down after 15 min of inactivity** — first request after idle takes ~30-50 seconds to wake up.
- Free PostgreSQL databases on Render expire after 90 days unless upgraded.
- Static files are served via **Whitenoise** — no separate CDN/S3 needed for this project size.

---

## 🐍 Deploy to PythonAnywhere

PythonAnywhere doesn't auto-deploy from GitHub pushes like Render — you'll pull code via their console and configure the web app manually through their dashboard. It uses **MySQL** (free tier) instead of PostgreSQL.

### Step 1: Sign up
Go to [pythonanywhere.com](https://www.pythonanywhere.com) → create a **free "Beginner" account**.

### Step 2: Open a Bash console
From your PythonAnywhere dashboard → **Consoles** tab → **Start a new console** → Bash

### Step 3: Clone your repo
```bash
git clone https://github.com/yourusername/SafeHer.git
cd SafeHer
```

### Step 4: Create a virtual environment
```bash
mkvirtualenv --python=python3.10 safeher-env
pip install -r requirements.txt
pip install mysqlclient
```

### Step 5: Create a MySQL database
1. Go to the **Databases** tab on PythonAnywhere
2. Set a MySQL password
3. Create a database, e.g. `yourusername$safeher`
4. Note the full connection details shown (host, username, database name)

### Step 6: Create your `.env` file
```bash
nano .env
```
Add:
```env
SECRET_KEY=your-random-secret-key
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com
PYTHONANYWHERE_HOSTNAME=yourusername.pythonanywhere.com
DATABASE_URL=mysql://yourusername:yourmysqlpassword@yourusername.mysql.pythonanywhere-services.com/yourusername$safeher
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
FAST2SMS_API_KEY=your-fast2sms-api-key
```
Save with `Ctrl+O`, `Enter`, then `Ctrl+X` to exit.

### Step 7: Run migrations
```bash
python manage.py migrate
python manage.py loaddata helpline/fixtures/helplines.json
python manage.py createsuperuser
python manage.py collectstatic --no-input
```

### Step 8: Configure the Web App
1. Go to the **Web** tab → **Add a new web app**
2. Choose **Manual configuration** (not the "Django" preset, since we need our custom virtualenv) → select the Python version matching your venv
3. Set **Virtualenv** path: `/home/yourusername/.virtualenvs/safeher-env`
4. Edit the **WSGI configuration file** (link shown on the Web tab) — replace its contents with:

```python
import os
import sys

path = '/home/yourusername/SafeHer'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safeher.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

5. Under the **Static files** section on the Web tab, add:

   | URL | Directory |
   |---|---|
   | `/static/` | `/home/yourusername/SafeHer/staticfiles` |
   | `/media/` | `/home/yourusername/SafeHer/media` |

6. Click the big green **Reload** button at the top of the Web tab

### Step 9: Visit your live site
```
https://yourusername.pythonanywhere.com
```

### Notes
- Free tier apps **go to sleep after a period of inactivity** and need a visit to wake up (similar to Render's free tier)
- Free tier only allows **outbound HTTPS requests to a limited allowlist of sites** — this can block Fast2SMS API calls unless you request access via **Account → Whitelisted sites**, or upgrade to a paid plan. Gmail SMTP (`smtp.gmail.com`) is allowed by default in most cases — verify under your account if email fails
- After any future `git pull` to update code, re-run `collectstatic` and click **Reload** on the Web tab

---

## 🚂 Deploy to Railway

Railway works similarly to Render — it auto-deploys from your GitHub repo and provisions a managed PostgreSQL database. This project includes `railway.json`, `nixpacks.toml`, and `Procfile` so Railway's build/start commands are pre-configured.

### Step 1: Sign up
Go to [railway.app](https://railway.app) → **Login with GitHub**

### Step 2: Create a new project
1. Click **New Project** → **Deploy from GitHub repo**
2. Authorize Railway to access your repos if prompted
3. Select your **SafeHer** repository

### Step 3: Add a PostgreSQL database
1. In your new project, click **+ New** → **Database** → **Add PostgreSQL**
2. Railway provisions it automatically and creates a `DATABASE_URL` variable you can reference

### Step 4: Link the database URL to your web service
1. Click on your **web service** (the SafeHer app, not the database)
2. Go to the **Variables** tab
3. Click **+ New Variable** → **Add Reference** → select the Postgres service's `DATABASE_URL`
   (This keeps it in sync automatically if Railway ever rotates credentials)

### Step 5: Add the remaining environment variables
Still in the **Variables** tab, add:
```
SECRET_KEY=your-random-secret-key
DEBUG=False
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
FAST2SMS_API_KEY=your-fast2sms-api-key
```

### Step 6: Generate a public domain
1. Go to your web service → **Settings** tab → **Networking**
2. Click **Generate Domain**
3. Railway gives you a URL like `safeher-production.up.railway.app` and auto-sets `RAILWAY_PUBLIC_DOMAIN`, which `settings.py` already reads to whitelist itself

### Step 7: Deploy
Railway builds automatically once GitHub is connected. Watch progress in the **Deployments** tab. Behind the scenes:
- `nixpacks.toml` runs `collectstatic` during the build phase
- `Procfile`'s `release` line runs migrations + loads helpline fixtures before each deploy
- `Procfile`'s `web` line starts Gunicorn

### Step 8: Create a superuser
1. Go to your web service → click the **⋮** menu → **Open Shell** (or use Railway CLI: `railway run python manage.py createsuperuser`)
2. Run:
```bash
python manage.py createsuperuser
```

### Step 9: Visit your live site
```
https://safeher-production.up.railway.app
```

### Notes
- Railway's free trial gives **$5/month in usage credit** shared across all your services (web + database) — once exhausted, the app pauses until the next billing cycle or you add a payment method
- No "1 database per account" wall like Render's free tier — you can run this alongside other projects more easily
- Future `git push` to your connected branch triggers an automatic redeploy

---

## 📞 Emergency Numbers (Pre-loaded)
- 112 — Emergency (All Services)
- 100 — Police
- 1091 — Women Helpline
- 181 — Domestic Violence
- 108 — Ambulance
- 1098 — Child Helpline