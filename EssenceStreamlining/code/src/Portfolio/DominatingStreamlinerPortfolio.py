from Search import MOMCTS
from typing import List, Dict, Type
from Toolchain import InstanceStats

'''
Build a portfolio containing the Single Best Streamliner combination found during search
'''


class DominatingStreamlinerPortfolio:

    def __init__(self, essence_spec: str, training_instances: List[str], validation_instances: List[str] = None):
        self._essence_spec = essence_spec
        self._training_instances = training_instances
        self._validation_instances = validation_instances

    def build_portfolio(self):
        search = MOMCTS.MOMCTS(self._essence_spec, self._training_instances, Eval())
        search.search()


class Eval:

    def __init__(self):
        self.__current_best_streamliner = None
        self.__current_num_sat = 0

    '''
        Return whether or not the currently evaluated streamliner is dominating 
    '''

    def eval_streamliner(self, streamliner_combo: str, results: Dict[str, Type[InstanceStats.InstanceStats]]) -> int:
        num_sat = sum(map(lambda x: int(x.satisfiable()), results.values()))

        if not self.__current_best_streamliner:
            self.__current_best_streamliner = streamliner_combo
            self.__current_num_sat = num_sat
            return 1

        for key, value in results.items():
            print(key, value)

        num_sat = sum(map(lambda x: int(x.satisfiable()), results.values()))
        if num_sat > self.__current_num_sat:
            self.__current_num_sat = num_sat
            self.__current_best_streamliner = streamliner_combo
            return 1
        else:
            return 0
