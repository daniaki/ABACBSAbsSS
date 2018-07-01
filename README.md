# ABACBSAbsSS
Conference abstract submission and review web application

# Requirements
- django==2.0
- djangorestframework
- djangorestframework-filters
- social-auth-app-django
- factory-boy
- Faker
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

