# Airbnb Automation
A Django-based end-to-end web automation project that uses Playwright to interact with Airbnb, simulate a real user search and store results in a database.

# Project Structure
```bash
airbnb-e2e-django-automation/      # Root Directory
├── manage.py
├── core/                          # Project Folder
│   ├── settings.py
│   └── urls.py
├── tracker/                       # App folder
│   ├── models.py                  # Single Result model
│   ├── services.py                # save_result, take_screenshot, set_state, get_state
│   ├── admin.py
│   ├── monitor.py                 # Console and network listeners
│   ├── steps/
│   │   ├── step01.py              # Homepage load + location search + suggestion selection
│   │   ├── step02.py              # (Handled inside step01)
│   │   ├── step03.py              # Date picker interaction
│   │   ├── step04.py              # Guest picker + search trigger
│   │   ├── step05.py              # Results page validation + listing scraping
│   │   └── step06.py              # Listing detail page verification
│   └── management/
│       └── commands/
│           └── run_automation.py  # Django management command entry point
└── screenshots/                   # Auto-created, stores step screenshots
```

# Requirements
- Python 3.12+
- Django 4+
- Playwright (Chromium)

# Installation
### 1. Clone the project
```bash
git clone https://github.com/emon51/airbnb-e2e-django-automation.git
```
### 2. Change directory
```bash
cd airbnb-e2e-django-automation
```

### 3. Create and activate virtual environment
```bash
python3 -m venv venv
```
### 4. Activate virtual environment
```bash
source venv/bin/activate
```

### 5. Install dependencies
```bash
pip install -r requirements.txt
```

### 6. Apply migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create superuser (for admin access)
```bash
python manage.py createsuperuser
```
### 8. Create a **.env** file in the root directory and paste the bellow code inside it
```bash
SECRET_KEY=your-django-secret-key-here
DEBUG=True
AIRBNB_URL=https://www.airbnb.com/
DJANGO_ALLOW_ASYNC_UNSAFE=true
```
### 9. Run automatoion server
```bash
python manage.py run_automation.py
```

### 9. Run the server
```bash
python manage.py runserver
```

### 10. Visit the admin page
```bash
http://127.0.0.1:8000/admin
```

# License
This project is created for educational purposes
