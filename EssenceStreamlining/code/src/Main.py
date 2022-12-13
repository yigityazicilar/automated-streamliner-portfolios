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
parser.add_argument('essence_spec', type=str,
                    help='Essence Specification file')
parser.add_argument('training_instance_dir', type=str,
                    help='Directory containing instances for streamliner evaluation')
parser.add_argument('info_full_file', type=str,
                    help='File containing info on training instances')
parser.add_argument('configuration', type=str,
                    help='Yaml configuration')

args = parser.parse_args()
essence_spec = args.essence_spec
working_directory = args.working_directory

with open(args.configuration, 'r') as conf_file:
    conf = yaml.safe_load(conf_file)

# Parse out the training stats based upon the selected training instances
baseModelStats = BaseModelStats(f"{working_directory}/BaseModelResults.csv", args.training_instance_dir,
                                args.info_full_file, SolverFactory.get_solver(conf.get('solver')))
baseModelStats.evaluate_training_instances(essence_spec, conf)

streamlinerModelStats = StreamlinerModelStats(f"{working_directory}/StreamlinerModelStats.csv",
                                              SolverFactory.get_solver(conf.get('solver')))

portfolio_builder = HydraPortfolio(essence_spec, baseModelStats, streamlinerModelStats, conf)
portfolio_builder.build_portfolio()
