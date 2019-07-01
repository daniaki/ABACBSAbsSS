import json
import os
import random
import string
import sys

from pathlib import Path

from django.core.management.base import BaseCommand

BASE_DIR = Path(str(Path(__file__))).parents[3]
SETTINGS_DIR = str(BASE_DIR / "settings")


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        secrets = {
            "orcid_key": "",
            "orcid_secret": "",
            "secret_key": "".join(
                [random.choice(
                    string.digits + string.ascii_letters + string.punctuation)
                    for _ in range(256)
                ]
            ),
            "email_host": "localhost",
            "email_port": "1025",
            "email_host_user": "",
            "email_host_password": "",
            "reply_to_email": "",
            "closing_date": "2018-11-07 22:59:59+10:00",
            "grant_closing_date": "2018-11-07 22:59:59+10:00",
        }

        path = os.path.join(SETTINGS_DIR, 'secrets.json')
        if os.path.isfile(path):
            while True:
                overwrite = input(
                    "An existing secrets file exists. "
                    "Would you like to overwrite this file? [y/N]")
                if overwrite == 'y':
                    with open(path, 'w') as fp:
                        json.dump(secrets, fp, sort_keys=True, indent=2)
                        sys.stdout.write("Created secrets file %s\n" % path)
                        return
                elif overwrite == 'N':
                    sys.stdout.write("Fine then.\n")
                    return
                else:
                    sys.stdout.write("Enter y or N.\n")
        else:
            with open(path, 'w') as fp:
                json.dump(secrets, fp, sort_keys=True, indent=2)
                sys.stdout.write("Created secrets file %s\n" % path)
