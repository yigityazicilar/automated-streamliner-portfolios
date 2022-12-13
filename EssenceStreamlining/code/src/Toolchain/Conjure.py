import logging
import glob
import Executor as Executor
from typing import Set

portfolio_size = 1


def generate_streamliners(essence_spec: str):
    # return ['conjure', 'streamlining', essence_spec, f'--portfolio-size={self.portfolio_size}', f'-o {output_dir}']
    logging.debug(f"Generating candidate streamliners")
    command = ['conjure', 'streamlining', essence_spec]
    (res, time_taken) = Executor.callable(command)
    return res


def generate_streamlined_models(essence_spec: str, streamliner_combination: str, output_dir='conjure-output'):
    # If this is a streamliner combination (- in the combo), translate to ','
    if '-' in streamliner_combination:
        streamliner_combination = ','.join(streamliner_combination.split("-"))
    command = ['conjure', 'modelling', essence_spec, '--generate-streamliners', streamliner_combination,
               f"--portfolio={portfolio_size}", '-o', output_dir]
    logging.debug(f"Building streamlined models for {streamliner_combination}: {command}")
    (res, time_taken) = Executor.callable(command)
    return glob.glob(f'{output_dir}/*.eprime')


def translate_essence_param(eprime_model: str, essence_param: str, output_eprime_param: str):
    return ['conjure', 'translate-parameter', f'--eprime={eprime_model}',
            f'--essence-param=./TrainingParams/{essence_param}',
            f'--eprime-param={output_eprime_param}']
