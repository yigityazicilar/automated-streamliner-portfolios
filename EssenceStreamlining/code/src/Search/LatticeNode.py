from typing import Set


class LatticeNode:

    def __eq__(self, o: object) -> bool:
        return isinstance(o, LatticeNode) and o.streamliner_combination() == self._streamliner_combination

    def __str__(self) -> str:
        return ','.join(sorted([x for x in self._streamliner_combination]))

    ''' Return the hash of the sorted individual streamliners'''

    def __hash__(self) -> int:
        return self._streamliner_combination.__hash__()

    def __init__(self, streamliner_combination: Set):
        self.children = {}
        self._streamliner_combination = frozenset(streamliner_combination)

    def streamliner_combination(self):
        return self._streamliner_combination
