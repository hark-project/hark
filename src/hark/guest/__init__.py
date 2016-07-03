from typing import List

_guests = {
    'Debian-8': None,
}


def guests() -> List[str]:
    return list(_guests.keys())
