# ABACBSAbsSS
Conference abstract submission and review web application

# Requirements
- django>=2.0
- djangorestframework>=3.8.2
- djangorestframework-filters>=0.10.2
- social-auth-app-django>=1.2.0
- factory-boy>=2.9.2
- Faker>=0.7.18
- mod_wsgi

# Local Development
Make sure to file in the genenrated secrets file if running on staging/production.

```bash
pip install -r requirements\local.txt
python manage.py createdefaultsecrets
python manage.py migrate
```

# Staging setup
```bash
pip install -r requirements\staging.txt
python manage.py createdefaultsecrets
python manage.py migrate
```

# Production setup
```bash
pip install -r requirements\production.txt
python manage.py createdefaultsecrets
python manage.py migrate
```

