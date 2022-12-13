import logging
import pandas as pd
import Toolchain.Conjure as Conjure
from SingleModelStreamlinerEvaluation import SingleModelStreamlinerEvaluation
import os
from functools import partial
import glob
import sys


class BaseModelStats:

    def __init__(self, base_stats_file, training_instance_dir, info_full_file, solver):
        self.base_stats_file = base_stats_file
        self.training_instances = [instance.split("/")[-1] for instance in
                                   glob.glob(f'{training_instance_dir}/*.param')]
        self.info_full = pd.read_csv(info_full_file)
        self.training_df = self._load_base_stats(base_stats_file, solver)
        self.solver = solver

    def _callback(self, instance, result):
        instance_stages = result.get_stages()
        combined_keys = {'Instance': instance.split("/")[-1], 'TotalTime': result.total_time(),
                         'Satisfiable': result.satisfiable(), 'Killed': result.killed(),
                         'TimeOut': result.timeout(), 'Solver': self.solver.get_solver_name()}
        for stage_name, stage in instance_stages.items():
            for key, value in stage.keys().items():
                combined_keys[f'{stage_name}_{key}'] = value

        for key, value in result.solver_stats().items():
            combined_keys[f"solver_{key}"] = value
        self.training_df = self.training_df.append(combined_keys, ignore_index=True)
        # logging.info("Callback:", combined_keys)
        self.training_df.to_csv(self.base_stats_file, index=False)

    def _load_base_stats(self, output_file, solver):
        print(output_file)
        if os.path.exists(output_file):
            self.training_df = pd.read_csv(output_file)
            self.training_df = self.training_df[self.training_df['Instance'].isin(self.training_instances)]
            return self.training_df
        else:
            return pd.DataFrame(
                columns=['Instance', 'TotalTime', 'Satisfiable', 'Killed', 'TimeOut',
                         'Solver', 'conjure_RealTime', 'conjure_CPUTime',
                         'conjure_CPUUserTime', 'conjure_CPUSystemTime', 'conjure_CPUUsage', 'conjure_Timeout',
                         'savilerow_RealTime',
                         'savilerow_CPUTime', 'savilerow_CPUUserTime', 'savilerow_CPUSystemTime', 'savilerow_CPUUsage',
                         'savilerow_Timeout'] + [f'{solver.get_solver_name()}_{x}' for x in
                                                 ['RealTime', 'CPUTime', 'CPUUserTime',
                                                  'CPUSystemTime', 'CPUUsage', 'Timeout']] + solver.get_stat_names()
            )

    def evaluate_training_instances(self, essence_spec, conf):
        # Evaluate the base specification across the training instances
        base_combination = ''
        self.info_full['md5checksum'] = self.info_full['md5checksum'].map('{}.param'.format)
        training_stats = self.info_full[self.info_full['md5checksum'].isin([x for x in self.training_instances])]
        training_stats = training_stats.rename(columns={'md5checksum': 'Instance'})
        training_stats['TotalTime'] = 4000
        instances_to_eval = set(self.training_instances) - set([x.split("/")[-1] for x in self.training_df['Instance']])
        if not instances_to_eval:
            return self.training_df

        generated_models = Conjure.generate_streamlined_models(essence_spec, base_combination)
        streamlinerEval = SingleModelStreamlinerEvaluation(generated_models[0], instances_to_eval, conf.get('solver'),
                                                           training_stats, conf.get('executor').get('num_cores'), 900)
        streamlinerEval.execute(self._callback, lambda instance, err: logging.exception(err))

        if len(self.training_df['Instance'].unique()) != len(self.training_instances):
            logging.error("Length of base training dir does not match number of training instances")
            sys.exit(1)

        return self.training_df

    def results(self):
        return self.training_df
