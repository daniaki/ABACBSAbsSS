# ABACBSAbsSS
Conference abstract submission and review web application

# Requirements
- django >= 2.0.11
- social-auth-app-django
- factory-boy
- Faker
- mock
- mod_wsgi

# Local Development
Make sure to file in the genenrated secrets file if running on staging/production.

```bash
pip install -r requirements\local.txt
python manage.py createdefaultsecrets
python manage.py populatetables
python manage.py createtestusers
python manage.py migrate
```

# Staging setup
```bash
pip install -r requirements\staging.txt
python manage.py createdefaultsecrets
python manage.py populatetables
python manage.py migrate
```

# Production setup
```bash
pip install -r requirements\production.txt
python manage.py createdefaultsecrets
python manage.py populatetables
python manage.py migrate
```

# Configuration
The project requires that a `settings.json` file exist in the settings folder with
the following format:

```json
{
  "orcid_key": "",
  "orcid_secret": "",
  "secret_key": "",
  "email_host": "localhost",
  "email_port": "1025",
  "email_host_user": "",
  "email_host_password": "",
  "reply_to_email": "",
  "closing_date": "2018-11-07 22:59:59+10:00",
  "grant_closing_date": "2018-09-17 09:00:00+10:00"
}
```

Required settings are `orcid_key`, `orcid_secret`, `secret_key`, `closing_date`
and `grant_closing_date`. The remaining settings are not yet used. 
To create a blank `settings.json` file run:

```bash
python manage.py createdefaultsecrets
```

# Production setup
You will need an [ORCID](https://orcid.org/) account to obtain a key, secret
pair for the application. In your account, navigate to `developer tools`. You
will need to create a new entry by specifying an application `name`, `URL`,
`description` and a `redirect URI`. The redirect uri should be the URL you provided
suffixed by `/oauth2/complete/orcid/`. For example: 

```
URL: https://abacbs.org/conference/
Redirect URI: https:/abacbs.org/conference/oauth2/complete/orcid/
```

Once you have registered the application, copy the `Client ID` to `orcid_key`
and the `Client secret` to `orcid_secret` in `settings.json`.


# User accounts
This step details how to create accounts for staff users.

Create a file called `accounts.csv` in file `data` folder with the following 
format:

```csv
email,name,password,group
john@smith.com,John Smith,1234qwer,conference_chair
```

The group column must be one of `reviewer`, `assigner` or `conference_chair`.
Reviewers are permitted to review abstracts which are assigned to them by
an Assigner. Conference chairs have access to all data including demographic
statistics, the ability to approve submissions, download database dumps etc. 

This command will output the accounts created with passwords and usernames. Pipe
the output into a separate file which you can then email to staff members.


# Closing dates
In `settings.json` modify the two keys `closing_date` (global closing date)
and `grant_closing_date` (closing date for travel grant applications). The values
for these keys should follow the python datetime format:

```
2018-09-17 09:00:00+10:00
```

# Categories
In `data/categories.txt` you can add submission categories. The file is a
tab separated file with the first column being the category name and the second
column being the category closing date. The closing date follows the same format
as above.


# Customisation
You can modify any of the files contained in the folder `data` by
adding/removing rows to customise specific aspects of the submission system. If
you make modifications, be sure to re-run the command:

```bash
python manage.py populatetables
```
