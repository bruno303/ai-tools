from datetime import datetime


def format_date(value):
    return value.strftime("%Y-%m-%d")


def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


def format_datetime(value):
    return value.strftime("%Y-%m-%dT%H:%M:%S")


def parse_datetime(value):
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
