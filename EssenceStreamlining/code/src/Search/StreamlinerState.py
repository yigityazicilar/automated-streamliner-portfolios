import json
import logging
from typing import AnyStr, Set, List, FrozenSet


class StreamlinerState:

    def __init__(self, streamliner_output: AnyStr):
        self.streamliner_json = json.loads(streamliner_output)
        self.init_groups(self.streamliner_json)
        self.invalid_combinations: Set[FrozenSet[str]] = set()

    def init_groups(self, streamliner_json: dict):
        self.groups = {}
        for val in streamliner_json:
            for group in streamliner_json[val]['groups']:
                if group in self.groups:
                    self.groups[group].add(val)
                else:
                    self.groups[group] = set(val)

    def get_candidate_streamliners(self) -> Set[str]:
        return self.streamliner_json.keys()

    def get_possible_adajacent_streamliners(self, streamliner_combination: Set[str]) -> Set[str]:
        possible_adajacent_streamliners: Set[str] = self.get_candidate_streamliners() - streamliner_combination
        to_remove = set()
        for streamliner in streamliner_combination:
            groups = self.streamliner_json[streamliner]['groups']

            for candidate_streamliner in possible_adajacent_streamliners:
                if not set(groups) - set(self.streamliner_json[candidate_streamliner]['groups']):
                    to_remove.add(candidate_streamliner)

                current_set = set(frozenset(set.union(set(candidate_streamliner), streamliner_combination)))
                if set.intersection(current_set, self.invalid_combinations):
                    to_remove.add(candidate_streamliner)

        possible_adajacent_streamliners.difference_update(to_remove)
        return possible_adajacent_streamliners

    def get_possible_adajacent_combinations(self, current_streamliner_combination: Set[str]) -> Set[str]:
        adjacent_streamliners: Set[str] = self.get_possible_adajacent_streamliners(current_streamliner_combination)
        return set([self.get_streamliner_repr_from_set(current_streamliner_combination.union(set([streamliner])))
                    for streamliner in adjacent_streamliners])

    def get_streamliner_repr_from_set(self, streamliner_combo: Set[str]) -> str:
        return '-'.join(sorted(list(streamliner_combo)))

    def get_streamliner_repr_from_str(self, streamliner_combo: str) -> str:
        return '-'.join(sorted(list(streamliner_combo)))

    def add_invalid_combination(self, combination: Set[str]):
        logging.info("Adding invalid combination")
        self.invalid_combinations.add(frozenset(combination))
