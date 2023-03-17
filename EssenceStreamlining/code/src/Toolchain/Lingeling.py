from typing import Dict
import re
import logging

patterns = [
    ('conflicts', re.compile('([0-9]*) conflicts')),
    ('ternaries', re.compile('([0-9]*) ternaries')),
    ('binaries', re.compile('([0-9]*) binaries')),
    ('iterations', re.compile('([0-9]*) iterations')),
    ('reductions', re.compile('([0-9]*) reductions')),
    ('restarts', re.compile('([0-9]*) restarts')),
    ('decisions', re.compile('([0-9]*) decisions')),
    ('propagations', re.compile('([0-9]*) propagations')),
    ('percentageSimplifying', re.compile('([0-9]*)% simplifying')),
    ('percentageSearch', re.compile('([0-9]*)% search')),
    ('time', re.compile('([0-9]*.[0-9]*|0|0.0) seconds')),
    ('randomSeed', re.compile('--seed=([0-9]*)'))
]


def get_solver_name():
    return 'lingeling'


def get_savilerow_flag():
    return 'sat'


def get_savilerow_output_flag():
    return "-out-sat"


def get_savilerow_output_file(eprime_model, raw_instance):
    raw_eprime_model = eprime_model.split(".")[0]
    return f'{raw_eprime_model}-{raw_instance}.dimacs'


def execute(output_file, stats):
    random_seed = None
    if 'configurationSeed' in stats:
        random_seed = str(stats['configurationSeed'].values[0])
    elif 'solver_randomSeed' in stats:
        random_seed = str(int(stats['solver_randomSeed'].values[0]))
    else:
        raise Exception("Missing Random Seed")

    return ['lingeling', '-v', f'--seed={random_seed}', output_file]


def parse_std_out(out, instance_stats) -> Dict[str, str]:
    output = out.decode('ascii')
    stats = {
        'satisfiable': False
    }
    for line in output.splitlines():
        for matcher in patterns:
            if matcher[1].search(line):
                match = matcher[1].search(line)
                stats[matcher[0]] = match.group(1)
                break

        if 's SATISFIABLE' in line:
            stats['satisfiable'] = True

        if 's UNSATISFIABLE' in line:
            stats['satisfiable'] = False

    instance_stats.add_solver_output(stats)
    instance_stats.set_solver_name(get_solver_name())
    instance_stats.set_satisfiable(stats['satisfiable'])
    return stats

def parse_std_err(out, instance_stats):
    return

def get_stat_names():
    return ['solver_satisfiable', 'solver_conflicts', 'solver_ternaries', 'solver_binaries',
            'solver_iterations', 'solver_reductions', 'solver_restarts', 'solver_decisions',
            'solver_propagations', 'solver_percentageSimplifying', 'solver_percentageSearch',
            'solver_randomSeed', 'solver_time']


'''
s UNSATISFIABLE
c
c    0.000   3% simplifying
c    0.000   0% search
c ==================================
c    0.000 100% all
c
c             0 conflicts,           0.0 confs/sec
c             0 ternaries,           0.0 confs/ternary
c             0 binaries,            0.0 confs/binary
c             0 iterations,          0.0 confs/iteration
c
c             0 reductions,          0.0 redus/sec,      0.0 confs/reduction
c             0 restarts,            0.0 rests/sec,      0.0 confs/restart
c             0 decisions,           0.0 decis/sec,      0.0 decis/conflict
c             0 propagations,        0.0 props/sec,      0.0 props/decision
c

'''
