from typing import Dict
import sys

def get_solver_name():
    return 'chuffed'


def get_savilerow_flag():
    return 'chuffed'


def get_savilerow_output_flag():
    return "-out-chuffed"


def get_savilerow_output_file(eprime_model, raw_instance):
    raw_eprime_model = eprime_model.split(".")[0]
    return f'{raw_eprime_model}-{raw_instance}.fzn'


def execute(output_file, stats):
    random_seed = None
    if 'configurationSeed' in stats:
        random_seed = str(stats['configurationSeed'].values[0])
    elif 'solver_randomSeed' in stats:
        random_seed = str(stats['solver_randomSeed'].values[0])
    else:
        raise Exception("Missing random seed")

    return ['fzn-chuffed', '-v', '-f', '--rnd-seed', random_seed, output_file]


def parse_std_out(out, instance_stats) -> Dict[str, str]:
    output = out.decode('ascii')
    stats = {
        'satisfiable': True
    }
    if not output:
        stats['satisfiable'] = False
    else:
        for line in output.splitlines():
            if '%%%mzn-stat' in line:
                line_split = line.split(": ")[1].split("=")
                stats[line_split[0]] = line_split[1]

            if '=====UNSATISFIABLE=====' in line:
                stats['satisfiable'] = False

    instance_stats.add_solver_output(stats)
    instance_stats.set_solver_name(get_solver_name())
    instance_stats.set_satisfiable(stats['satisfiable'])

    return stats

def parse_std_err(out, instance_stats):
    return

def get_stat_names():
    return ['solver_satisfiable', 'solver_backjumps', 'solver_baseMem',
            'solver_boolVariables', 'solver_failures', 'solver_initTime', 'solver_intVars', 'solver_nodes',
            'solver_nogoods',
            'solver_objective', 'solver_peakDepth', 'solver_peakMem', 'solver_propagations', 'solver_propagators',
            'solver_randomSeed', 'solver_restarts', 'solver_solveTime', 'solver_time', 'solver_trailMem',
            'solver_variables']


'''
%%%mzn-stat: nodes=163
%%%mzn-stat: failures=0
%%%mzn-stat: restarts=0
%%%mzn-stat: variables=109382
%%%mzn-stat: intVars=11763
%%%mzn-stat: boolVariables=97617
%%%mzn-stat: propagators=6364
%%%mzn-stat: propagations=17443
%%%mzn-stat: peakDepth=162
%%%mzn-stat: nogoods=0
%%%mzn-stat: backjumps=0
%%%mzn-stat: peakMem=0.00
%%%mzn-stat: time=0.468
%%%mzn-stat: initTime=0.445
%%%mzn-stat: solveTime=0.023
%%%mzn-stat: baseMem=0.00
%%%mzn-stat: trailMem=0.28
%%%mzn-stat: randomSeed=1624217437

'''
