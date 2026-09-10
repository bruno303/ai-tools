from helpers import format_date, parse_datetime


def date_label(value):
    return format_date(value)


def read_timestamp(value):
    return parse_datetime(value)
