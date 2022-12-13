import logging
import pandas as pd
import Toolchain.Conjure as Conjure
from SingleModelStreamlinerEvaluation import SingleModelStreamlinerEvaluation
import os
from functools import partial
import glob


class StreamlinerModelStats:

    def __init__(self, streamliner_model_stats_file, solver):
        self.streamliner_model_stats_file = streamliner_model_stats_file
        self.streamliner_model_stats = self._load_base_streamliner_stats(streamliner_model_stats_file, solver)
        self.solver = solver

    def callback(self, streamliner, instance, result):
        instance_stages = result.get_stages()
        combined_keys = {'Streamliner': str(streamliner), 'Instance': instance, 'TotalTime': result.total_time(),
                         'Satisfiable': result.satisfiable(), 'Killed': result.killed(), 'TimeOut': result.timeout(),
                         'Solver': self.solver.get_solver_name()}
        for stage_name, stage in instance_stages.items():
            for key, value in stage.keys().items():
                combined_keys[f'{stage_name}_{key}'] = value

        for key, value in result.solver_stats().items():
            combined_keys[f"solver_{key}"] = value
        self.streamliner_model_stats = self.streamliner_model_stats.append(combined_keys, ignore_index=True)
        self.streamliner_model_stats.to_csv(f'{self.streamliner_model_stats_file}.bak', index=False)
        os.rename(f'{self.streamliner_model_stats_file}.bak', self.streamliner_model_stats_file)

    def _load_base_streamliner_stats(self, output_file, solver):
        if os.path.exists(output_file):
            self.training_df = pd.read_csv(output_file)
            self.training_df['Streamliner'] = self.training_df['Streamliner'].astype(str)
            return self.training_df
        else:
            return pd.DataFrame(columns=['Streamliner', 'Instance', 'TotalTime', 'Satisfiable', 'Killed', 'TimeOut',
                                         'Solver', 'conjure_RealTime', 'conjure_CPUTime',
                                         'conjure_CPUUserTime', 'conjure_CPUSystemTime', 'conjure_CPUUsage',
                                         'conjure_Timeout', 'savilerow_RealTime',
                                         'savilerow_CPUTime', 'savilerow_CPUUserTime', 'savilerow_CPUSystemTime',
                                         'savilerow_CPUUsage',
                                         'savilerow_Timeout'] + [f'{solver.get_solver_name()}_{x}' for x in
                                                                 ['RealTime', 'CPUTime', 'CPUUserTime',
                                                                  'CPUSystemTime', 'CPUUsage',
                                                                  'Timeout']] + solver.get_stat_names())

    def results(self):
        return self.streamliner_model_stats
