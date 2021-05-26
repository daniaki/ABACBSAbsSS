# ABACBSAbsSS
Conference abstract submission and review web application

# Requirements
- django==2.0.13
- social-auth-app-django
- factory-boy
- Faker
- mock
- gunicorn


# Initial configuration
The project requires that a `secrets.json` file exist in the `./settings` folder with
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
and `grant_closing_date`. The remaining settings are not yet used. Copy and paste
the above into a new `secrets.json` file.


# ORCID setup
You will need an [ORCID](https://orcid.org/) account to obtain a key, secret
pair for the application. In your account, navigate to `developer tools`. You
will need to create a new entry by specifying an application `name`, `URL`,
`description` and a `redirect URI`. The redirect uri should be the URL you provided
suffixed by `/oauth/complete/orcid/`. For example: 

```
URL: https://abacbs.org/conference/
Redirect URI: https:/abacbs.org/conference/oauth/complete/orcid/
```

Once you have registered the application, copy the `Client ID` to `orcid_key`
and the `Client secret` to `orcid_secret` in `secrets.json`.


# Customisation
## User accounts
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


## Closing dates
In `secrets.json` modify the two keys `closing_date` (global closing date)
and `grant_closing_date` (closing date for travel grant applications). The values
for these keys should follow the python datetime format:

```
2018-09-17 09:00:00+10:00
```

## Categories
In `data/categories.txt` you can add submission categories. The file is a
tab separated file with the first column being the category name, and the second
column being the category closing date. The closing date follows the same format
as above.


## Customisation
You can modify any of the files contained in the folder `data` by
adding/removing rows to customise specific aspects of the submission system. If
you make modifications, be sure to re-run the command:

```bash
python manage.py populatetables
```

## Additional notes:
Any time you make changes to the data directory, re-run the command:

```bash
python manage.py populatetables
```

# Local Development
```bash
pip install -r requirements\local.txt
python manage.py migrate
python manage.py populatetables
python manage.py createtestusers 
```

# Production setup
## Option 1: Managed by you
If managing your own environment, set up a production server using Nginx and Gunicorn. Consult the documentation found 
[here](https://docs.gunicorn.org/en/stable/deploy.html). Initialize the Django application using:

```bash
pip install -r requirements\production.txt
python manage.py migrate
python manage.py populatetables
```

## Option 2: Manged by Docker
Alternatively if you want to run this application in Docker and skip the above steps, make sure to have Docker and 
Docker-compose installed. Place you SSL certificates in `docker/nginx/ssl` and make sure  they are labelled `app.cert` 
and `app.key` for your certificate file and key file respectively. In the `docker/nginx/nginx.conf` file, modify the 
field `server_name` to your registered domain name.

You are responsible for performing your own scheduled database backups if needed. You can do this by executing a shell
session in the running docker-compose container and copying the `db.sqlite3` file to your host file system.

The dockerized application works by accepting HTTP traffic on port 80, redirecting to HTTPS on port 443. You will need
to make sure your host system is accepting traffic on these ports.

Finally, run the following command in the application directory:

```shell
docker-compose up -d
```

If you decide that you want to add new customised data entries while the docker-compose service is already running, 
you will need to start a shell session into the running container:

```shell
docker exec -it <container-name> /bin/bash
```

Once inside, modify the desired file in the `data/` directory and then re-run `python manage.py populatetables` in that
same shell session. If you are unsure of how to find your container's name, in your host system run `docker ps`. You 
should see something similar to `<project-root-folder-name>_app_1`, for example `abacbsabsss_app_1`.