from Search import MOMCTS
from typing import List, Dict, Type, Tuple
from Toolchain import InstanceStats
import statistics
import logging
import sys
import pandas as pd
import json
import numpy as np

AVG_APPLIC_KEY = 'AvgApplic'
OVERALL_SOLVING_TIME_REDUCTION_KEY = 'OverallSolvingTimeReduction'
MEAN_REDUCTION_KEY = "MeanReduction"
MEDIAN_REDUCTION_KEY = "MedianReduction"
STD_DEV_KEY = "StandardDeviation"
QUANTILES_KEY = "Quantiles"


class HydraPortfolio:

    def __init__(self, essence_spec: str, base_model_stats, streamliner_model_stats, conf,
                 validation_instances: List[str] = None):
        self._essence_spec = essence_spec
        self._training_results = base_model_stats.results()
        self._streamliner_model_stats = streamliner_model_stats
        self._validation_instances = validation_instances
        self.conf = conf
        self.num_rounds = conf.get('hydra').get('num_rounds')

    def build_portfolio(self):
        cur_round = 0
        best_instance_results: Dict[str, Type[InstanceStats.InstanceStats]] = {}
        overall_portfolio = {}
        while True:
            eval = HydraEval(overall_portfolio, best_instance_results)
            search = MOMCTS.MOMCTS(self._essence_spec, self._training_results,
                                   eval,
                                   self.conf, self._streamliner_model_stats)

            search.search()
            cur_portfolio = eval.portfolio()
            overall_portfolio[str(cur_round)] = cur_portfolio
            cur_round += 1
            # logging.info(overall_portfolio)
            best_instance_results = self.generate_best_instance_stats(overall_portfolio)

            if cur_round == self.num_rounds:
                logging.info(overall_portfolio)
                return

    # Generate the best stats for the instances
    def generate_best_instance_stats(self, overall_portfolio) -> Dict[str, Type[InstanceStats.InstanceStats]]:
        best_instance_stats = {}
        df = self._streamliner_model_stats.results()
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)

        streamliners_in_portfolio = set()
        for round in overall_portfolio.keys():
            [streamliners_in_portfolio.add(streamliner) for streamliner in overall_portfolio[round].keys()]

        # Grab only the satisfiable runs
        df_sat = df[df['Satisfiable']]
        # Grab only the results on our current portfolio
        df_sat = df_sat[df_sat['Streamliner'].isin(streamliners_in_portfolio)]

        # logging.info(df_sat.groupby('Streamliner')['Satisfiable'].sum())
        # logging.info(df_sat.groupby('Instance')['Satisfiable'].sum())

        instance_stats_df = df_sat.groupby('Instance').apply(lambda x: df_sat.loc[x['solver_time'].idxmin()])
        instance_stats_df = instance_stats_df.reset_index(drop=True)

        for index, row in instance_stats_df.iterrows():
            instance = row['Instance']
            best_instance_stats[instance] = InstanceStats.translate_to_instance_stats(row)

        return best_instance_stats


class HydraEval():
    '''
    With the inputted portfolio we need to know how well each streamliner did on each instance as with Hydra
    you take the performance of the portfolio and you union this with the
    '''

    def __init__(self, overall_portfolio, best_instance_results: Dict[str, Type[InstanceStats.InstanceStats]]):
        self.__overall_portfolio = overall_portfolio
        self.__best_instance_results = best_instance_results
        self.__cur_portfolio = {}

    def _test(self, current_result: Type[InstanceStats.InstanceStats], best_result: Type[InstanceStats.InstanceStats]):
        """
        Test whether our current result is superior to any of the streamliners in our portfolio on this given instance
        :param current_result: The result attained from StreamlinerEval
        :param best_result: The best result from our current portfolio
        :return: True if our current result dominates, False otherwise
        """
        # If there is no streamliner in the portfolio that is satisfiable on this instance, the best result will be None
        if best_result == None:
            return True

        if current_result.satisfiable() and best_result.satisfiable() \
                and current_result.total_time() <= best_result.total_time():
            return True
        elif current_result.satisfiable() and not best_result.satisfiable():
            return True
        else:
            return False

    def _dominated(self, x, y):
        """
        Test whether x dominates y on Average Applicability and Mean Reduction
        :param x: Dict of objective values
        :param y: Dict of objective values
        :return: 1 if x dominates, 0 otherwise
        """
        return int((x[AVG_APPLIC_KEY] > y[AVG_APPLIC_KEY] and x[MEAN_REDUCTION_KEY] >= y[
            MEAN_REDUCTION_KEY])
                   or (x[AVG_APPLIC_KEY] >= y[AVG_APPLIC_KEY] and x[MEAN_REDUCTION_KEY] > y[
            MEAN_REDUCTION_KEY]))

    def _non_dominated(self, objective_values, cur_portfolio):
        """
        Test whether the objective values of the current streamliner are dominated by the portfolio
        :param objective_values: Objective values of current streamliner evaluated
        :param cur_portfolio: Current non-dominated portfolio of streamliners
        :return: sum of the number of streamliners in the portfolio that dominate our current streamliner
        """
        if not cur_portfolio:
            return True
        else:
            return sum(map(lambda x: self._dominated(x, objective_values), cur_portfolio.values())) == 0

    def _remove_dominated_combinations(self, objective_values, cur_portfolio):
        return dict(filter(lambda x: not self._dominated(objective_values, x[1]), cur_portfolio.items()))

    def combine_results(self, results: Dict[str, Type[InstanceStats.InstanceStats]]):
        combined_results = {}
        for x in results:
            if self._test(results[x], self.__best_instance_results.get(x)):
                combined_results[x] = results[x]
            else:
                combined_results[x] = self.__best_instance_results.get(x)

        return combined_results

    def eval_streamliner(self, streamliner_combo: str, results: Dict[str, Type[InstanceStats.InstanceStats]],
                         training_results: Type[pd.DataFrame]) -> int:
        logging.info("Hydra: Evaluating Streamliner")
        # Combine the results of the current portfolio with the new streamliner
        combined_results = self.combine_results(results)
        # logging.debug(f"Combined Results: {combined_results}")
        objective_values = self._objective_values(combined_results, training_results)

        logging.info(f"{streamliner_combo} has results: {objective_values}")
        if not self.exists_in_portfolio(streamliner_combo) and self._non_dominated(objective_values,
                                                                                   self.__cur_portfolio):
            logging.info(f"Streamliner {streamliner_combo} is non-dominated in the portfolio so adding")
            self.__cur_portfolio[streamliner_combo] = objective_values
            self.__cur_portfolio = self._remove_dominated_combinations(objective_values, self.__cur_portfolio)
            return 1
        else:
            logging.info(f"Streamliner {streamliner_combo} is dominated. Not adding to portfolio")
            return 0

    def exists_in_portfolio(self, streamliner_combo):
        for round in self.__overall_portfolio:
            if streamliner_combo in self.__overall_portfolio[round].keys():
                return True
        return False

    def save_portfolio(self):
        logging.info(json.dumps(self.__cur_portfolio))
        with open("Portfolio.json", 'w') as portfolio:
            portfolio.write(json.dumps(self.__cur_portfolio))

    def portfolio(self):
        return self.__cur_portfolio

    def _objective_values(self, results: Dict[str, Type[InstanceStats.InstanceStats]],
                          training_results: Type[pd.DataFrame]) -> Dict[str, object]:
        applicability = sum([int(results[x].satisfiable()) for x in results]) / len(results)
        print(f"Applicability: {applicability}")

        total_solving_time = sum([results[x].solver_time() for x in results if results[x].satisfiable()])
        print(f"Total Solving Time: {total_solving_time}")
        print(f"Training Results:\n{training_results}")
        print(f"Results:\n{results}")

        reductions = [
            (float(training_results[training_results['Instance'] == x]['solver_time'].values[0]) - results[x].solver_time()) /
            float(training_results[training_results['Instance'] == x]['solver_time'].values[0]) for x in results if
            results[x].satisfiable()
        ]
        print(f"Reductions: {reductions}")
        satisfiable_instances = set([x for x in results if results[x].satisfiable()])
        base_total_time = training_results[training_results['Instance'].isin(satisfiable_instances)][
            'solver_time'].sum()

        # This is calculating an overall reduction in cumulative time on all sat instances based upon total time of the pipeline (Conjure + SR + Solver)
        if applicability > 0:
            overall_solving_time_reduction = (base_total_time - total_solving_time) / base_total_time
            mean_reduction = np.mean(reductions)
            median_reduction = np.median(reductions)
            std_dev = np.std(reductions)
            quantiles = np.quantile(reductions, [0.25, 0.5, 0.75]).tolist()

        else:
            mean_reduction = 0
            median_reduction = 0
            std_dev = 0
            overall_solving_time_reduction = 0
            quantiles = []
        return {
            AVG_APPLIC_KEY: applicability,
            OVERALL_SOLVING_TIME_REDUCTION_KEY: overall_solving_time_reduction,
            MEAN_REDUCTION_KEY: mean_reduction,
            MEDIAN_REDUCTION_KEY: median_reduction,
            STD_DEV_KEY: std_dev,
            QUANTILES_KEY: quantiles}
