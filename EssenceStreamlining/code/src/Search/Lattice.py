import networkx as nx
from Search.LatticeNode import LatticeNode
from typing import Set
import logging


class Lattice:

    def __init__(self):
        self.__graph = nx.DiGraph('')
        # Add the root node of the lattice (the unstreamlined model)
        self.add_node('')

    def streamliner_combo_str_repr(self, streamliner_combo: Set[str]):
        return ','.join(sorted([candidate_streamliner for candidate_streamliner in streamliner_combo]))

    def add_node(self, node_combination):
        logging.info(f"Adding node {node_combination}")
        self.__graph.add_node(node_combination, visited_count=0, last_visited=None, score=0)

    def add_edge(self, current_combo_str, streamliner_combo):
        self.__graph.add_edge(current_combo_str, streamliner_combo)

    def get_graph(self):
        return self.__graph
