import re


def to_dashdate(date: str, format=r'^(\d\d\d\d)(\d\d)(\d\d)$'):
    m = re.match(format, date)
    if m:
        return '-'.join(m.groups())
    raise Exception(f'Invalid date format ({format})')