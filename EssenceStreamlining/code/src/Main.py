import argparse
import yaml
import logging
import Toolchain.SolverFactory as SolverFactory
from SingleModelStreamlinerEvaluation import SingleModelStreamlinerEvaluation
from Search.BaseModelStats import BaseModelStats
from Search.StreamlinerModelStats import StreamlinerModelStats
import Toolchain.Conjure as Conjure
import glob
import sys
import pandas as pd
import os
from Portfolio.DominatingStreamlinerPortfolio import DominatingStreamlinerPortfolio
from Portfolio.HydraPortfolio import HydraPortfolio

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

parser = argparse.ArgumentParser(description='Streamlining an Essence Spec')
parser.add_argument('working_directory', type=str,
                    help='Working Directory')
parser.add_argument('instance_dir', type=str,
                    help='Directory containing instances for streamliner evaluation')

args = parser.parse_args()
working_directory = args.working_directory
instance_dir = args.instance_dir
essence_spec = f'{working_directory}/model.essence'

with open(f'{working_directory}/conf.yaml', 'r') as conf_file:
    conf = yaml.safe_load(conf_file)
    conf['working_directory'] = working_directory
    conf['instance_directory'] = instance_dir

# Parse out the training stats based upon the selected training instances
baseModelStats = BaseModelStats(f"{working_directory}/BaseModelResults.csv", working_directory, instance_dir,
                                SolverFactory.get_solver(conf.get('solver')))
baseModelStats.evaluate_training_instances(f'{working_directory}/model.essence', conf)

streamlinerModelStats = StreamlinerModelStats(f"{working_directory}/StreamlinerModelStats.csv",
                                              SolverFactory.get_solver(conf.get('solver')))

portfolio_builder = HydraPortfolio(essence_spec, baseModelStats, streamlinerModelStats, conf)
portfolio_builder.build_portfolio()
