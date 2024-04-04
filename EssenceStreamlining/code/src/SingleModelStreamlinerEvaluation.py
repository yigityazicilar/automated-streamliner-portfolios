import logging

import Toolchain.Pipeline as Pipeline
import Toolchain.InstanceStats as InstanceStats
import Toolchain.SolverFactory as SolverFactory
import concurrent.futures
from threading import Event
from typing import Dict, Type
import sys
import time


class SingleModelStreamlinerEvaluation:

    def __init__(self, model, working_directory, instance_dir, training_instances, solver, training_stats, num_cores, total_time):
        self.model = model
        self.working_directory = working_directory
        self.instance_dir = instance_dir
        self.training_instances = training_instances
        self.solver = SolverFactory.get_solver(solver)
        self.training_stats = training_stats
        self.num_cores = num_cores
        self.total_time = total_time

    def generate_pipeline(self, training_instance, eprime_model, total_time, stats):
        logging.debug(f"Generating pipeline for {training_instance} and model {eprime_model}")

        if not total_time:
            total_time = self.training_stats[self.training_stats['Instance'] == training_instance]['TotalTime'] * 1.5
        return Pipeline.Pipeline(eprime_model, self.working_directory, self.instance_dir, training_instance, self.solver, Event(), total_time, stats)

    def _default_callback(self, instance, data):
        logging.info(instance, data)

    def _default_err_callback(self, instance, err):
        logging.exception(err)

    def execute(self, callback=_default_callback, error_callback=_default_err_callback) -> Dict[str, Type[InstanceStats.InstanceStats]]:
        mappings = {}
        for instance in self.training_instances:
            mappings[instance] = self.generate_pipeline(instance, self.model, self.total_time,
                                                        self.training_stats[
                                                            self.training_stats['Instance'] == instance])

        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_cores) as executor:
            futures = {executor.submit(mappings[instance].execute): instance for instance in mappings.keys()}
            for future in concurrent.futures.as_completed(futures):
                instance = futures[future]
                try:
                    data = future.result()
                    results[instance] = data
                    # Call the callback method passed in
                    callback(instance, data)
                except Exception as exc:
                    error_callback(instance, exc)

        return results
