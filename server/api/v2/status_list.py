from typing import List, Dict


def _parse_parameter(list_str: str) -> List[int]:
    try:
        return list(map(int, list_str.split(',')))
    except ValueError:
        raise ValueError(f'error: failed to parse request parameter')


def get_status_list(status_id_list_str: str, user: Dict):
    status_id_list = _parse_parameter(status_id_list_str)
