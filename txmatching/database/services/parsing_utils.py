import datetime
from typing import Optional

from txmatching.auth.exceptions import InvalidArgumentException
from txmatching.utils.hla_system.hla_transformations import parse_hla_raw_code


def parse_date_to_datetime(date: Optional[str]) -> Optional[datetime.datetime]:
    if date is None:
        return None
    try:
        return datetime.datetime.strptime(date, '%Y-%m-%d')
    except (ValueError, TypeError) as ex:
        raise InvalidArgumentException(f'Invalid date "{date}". It must be in format "YYYY-MM-DD", e.g.,'
                                       ' "2020-12-31".') from ex


def get_hla_code(code: Optional[str], raw_code: str) -> Optional[str]:
    return code if code is not None else parse_hla_raw_code(raw_code)
