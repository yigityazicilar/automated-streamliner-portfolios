from typing import AnyStr, Set, List, FrozenSet


def get_streamliner_repr_from_set(streamliner_combo: Set[str]) -> str:
    return '-'.join(sorted(list(streamliner_combo)))


def get_streamliner_repr_from_str(streamliner_combo: str) -> str:
    return '-'.join(sorted(list(streamliner_combo)))
