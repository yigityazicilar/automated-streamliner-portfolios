from typing import List, Set, Type, Tuple, Dict
import random
import math
import Util


class RandomSelection:

    def select(self, current_combination: Set[str], adjacent_nodes: List[str]) -> str:
        return adjacent_nodes[random.randint(0, len(adjacent_nodes) - 1)]


class UCTSelection:
    exploration_constant = 0.1

    def select(self, lattice, current_combination: Set[str], adjacent_nodes: List[str]) -> str:
        uct_values = self.uct_values(lattice, current_combination, adjacent_nodes)
        return sorted(uct_values.keys(), key=lambda x: uct_values[x], reverse=True)[0]

    def uct_values(self, lattice, current_combination: Set[str], adjacent_nodes: List[str]):
        uct_values = {}
        combination_str_repr: str = Util.get_streamliner_repr_from_set(current_combination)
        parent_node_attributes = lattice.get_graph().nodes[combination_str_repr]

        for node in adjacent_nodes:
            current_combination.add(node)
            streamliner_combo: str = Util.get_streamliner_repr_from_set(current_combination)
            cur_attributes = lattice.get_graph().nodes[streamliner_combo]
            if cur_attributes['visited_count'] > 0:
                uct_values[node] = (cur_attributes['score'] / cur_attributes[
                    'visited_count']) + self.exploration_constant \
                                   * math.sqrt(
                    math.log(parent_node_attributes['visited_count']) / cur_attributes['visited_count'])
            else:
                uct_values[node] = self.exploration_constant \
                                   * math.sqrt(
                    math.log(parent_node_attributes['visited_count']) / cur_attributes['visited_count'])

            current_combination.remove(node)

        return uct_values
