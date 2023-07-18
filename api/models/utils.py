from datetime import datetime


def parse_date(date_string: str):
    if len(date_string) == 10:
        parse_format = "%Y-%m-%d"
    elif len(date_string) == 7:
        parse_format = "%Y-%m"
    elif len(date_string) == 4:
        parse_format = "%Y"
    else:
        parse_format = "%Y-%m-%dT%H:%M:%SZ"
    try:
        dt = datetime.strptime(date_string, parse_format)
        return dt
    except ValueError:
        return None
