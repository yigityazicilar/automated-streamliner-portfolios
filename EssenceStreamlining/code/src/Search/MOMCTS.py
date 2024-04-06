import Toolchain.Conjure as Conjure
import Toolchain.InstanceStats as InstanceStats
from Toolchain.runsolver import RunsolverStats
from Search.StreamlinerState import StreamlinerState
from SingleModelStreamlinerEvaluation import SingleModelStreamlinerEvaluation
from Search.Lattice import Lattice
import logging
import random
from typing import List, Set, Type, Tuple, Dict
import pandas as pd
from functools import partial
import sys
import math
from Search.Selection import RandomSelection, UCTSelection


class MOMCTS:

    def __init__(self, essence_spec, training_results: Type[pd.DataFrame], eval,
                 conf, streamliner_model_stats):
        self.essence_spec = essence_spec
        self.working_directory = conf.get('working_directory')
        self.instance_dir = conf.get('instance_directory')
        self.training_results = training_results
        self.eval = eval
        # Generate the set of streamliners for the essence spec
        result = Conjure.generate_streamliners(essence_spec)
        # Generate the streamliner state
        self._streamliner_state = StreamlinerState(result.stdout)
        self._lattice = Lattice()
        self.conf = conf
        self.streamliner_model_stats = streamliner_model_stats
        self.selection_class = UCTSelection()

    '''
    We have the lattice now, the next component is actually searching and building the lattice
    using our MCTS
    '''

    def search(self):
        iteration = 0
        while True:
            current_combination, possible_adjacent_streamliners = self.selection()
            new_combination_added: str = self.expansion(current_combination, list(possible_adjacent_streamliners))

            try:
                results, cached = self.simulation(new_combination_added)
            except Exception as e:
                self._streamliner_state.add_invalid_combination(current_combination)
                logging.error(e)
                logging.error("Simulation failed")
                continue
            back_prop_value = self.eval.eval_streamliner(new_combination_added, results, self.training_results)
            self.eval.save_portfolio()

            self.backprop(new_combination_added, back_prop_value, iteration)

            if cached:
                logging.info("Cached result")
            else:
                iteration += 1
                print(f"ON ITERATION {iteration} OUT OF {self.conf.get('mcts').get('num_iterations')}")
            logging.info(iteration)
            if iteration >= self.conf.get('mcts').get('num_iterations'):
                return

    def selection(self) -> Tuple[Set[str], Set[str]]:
        logging.debug("------SELECTION-----")
        current_combination: Set[str] = set()

        while True:
            # Get streamliners that we can combine with our current combination
            possible_adjacent_combinations: Set[str] = self._streamliner_state.get_possible_adajacent_combinations(
                current_combination)
            # print(possible_adjacent_combinations)

            combination_str_repr: str = self._streamliner_state.get_streamliner_repr_from_set(current_combination)

            # Find the adjacent nodes in the Lattice to our current combination
            adjacent_nodes: List[str] = list(self._lattice.get_graph().neighbors(combination_str_repr))

            # Calculate if all possible children exist in the Lattice
            set_diff = set(possible_adjacent_combinations) - set(adjacent_nodes)

            # If not all children have been created, stop and expand this node
            if len(set_diff) > 0:
                logging.debug(f"Not all children have been created. Returning {current_combination}")
                return current_combination, set_diff
            # Else move down the Lattice and continue to select
            else:
                node = self.selection_class.select(self._lattice, current_combination, adjacent_nodes)
                current_combination.add(node)

    def expansion(self, current_node_combination: Set[str], possible_adjacent_nodes: List[str]) -> str:
        new_streamliner_combo: str = possible_adjacent_nodes[random.randint(0, len(possible_adjacent_nodes) - 1)]

        current_combo_str = self._streamliner_state.get_streamliner_repr_from_set(current_node_combination)

        # Add the new streamliner combination into the lattice
        self._lattice.add_node(new_streamliner_combo)
        # Add an edge between the selected node and the newly expanded node
        self._lattice.add_edge(current_combo_str, new_streamliner_combo)
        return new_streamliner_combo

    def simulation(self, new_combination: str):
        streamliner_results_df = self.streamliner_model_stats.results()
        logging.info(f"New combo {new_combination}")
        # Check to see if we have already encountered this streamliner before
        if new_combination in streamliner_results_df['Streamliner'].unique():
            logging.info(f"{new_combination} has already been seen. Using cached results")
            results = streamliner_results_df[streamliner_results_df['Streamliner'] == new_combination]
            base_results = {}
            for index, row in results.iterrows():
                base_results[row['Instance']] = InstanceStats.translate_to_instance_stats(row)

            if len(results) >= len(self.training_results['Instance']):
                return base_results, True

        generated_models = Conjure.generate_streamlined_models(self.essence_spec, new_combination,
                                                               output_dir=f"{self.working_directory}/conjure-output")
        if len(generated_models) == 1:
            logging.info(generated_models)
            streamlinerEval = SingleModelStreamlinerEvaluation(generated_models[0], self.working_directory,
                                                               self.instance_dir,
                                                               self.training_results['Instance'],
                                                               self.conf.get('solver'),
                                                               self.training_results,
                                                               self.conf.get('executor').get('num_cores'), None)
            callback = partial(self.streamliner_model_stats.callback, new_combination)
            # We now need to parse these results into some format that we can use as a reference point
            base_results = streamlinerEval.execute(callback=callback)

            # for _, result in base_results.items():
            #     print(result.total_time())

            return base_results, False

    def backprop(self, streamliner_combo: str, back_prop_value: int, iteration: int):
        logging.debug("------BACKPROP-----")

        '''
        Back prop up the lattice structure to the root node 
        '''

        node_attributes = self._lattice.get_graph().nodes[streamliner_combo]
        if node_attributes['last_visited'] != iteration:
            node_attributes['visited_count'] = node_attributes['visited_count'] + 1
            node_attributes['score'] += back_prop_value

        predecessor_nodes = self._lattice.get_graph().predecessors(streamliner_combo)
        for node in predecessor_nodes:
            self.backprop(node, back_prop_value, iteration)
