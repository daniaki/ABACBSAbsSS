from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.conf import settings


def get_local_closing_date():
    return parse_datetime(
        settings.CLOSING_DATE).astimezone(tz=timezone.get_current_timezone())


def get_local_scholarship_closing_date():
    return parse_datetime(
        settings.SCHOLARSHIP_CLOSING_DATE).astimezone(
        tz=timezone.get_current_timezone())
