from typing import Dict
import re
import logging, os

patterns = [
    ('chronological', re.compile(r'chronological:\s+([0-9]*)')),
    ('conflicts', re.compile(r'conflicts:\s+([0-9]*)')),
    ('decisions', re.compile(r'decisions:\s+([0-9]*)')),
    ('learned', re.compile(r'learned:\s+([0-9]*)')),
    ('learned_lits', re.compile(r'learned_lits:\s+([0-9]*)')),
    ('minimized', re.compile(r'minimized:\s+([0-9]*)')),
    ('shrunken', re.compile(r'shrunken:\s+([0-9]*)')),
    ('minishrunken', re.compile(r'minishrunken:\s+([0-9]*)')),
    ('ofts', re.compile(r'otfs:\s+([0-9]*)')),
    ('propagations', re.compile(r'propagations:\s+([0-9]*)')),
    ('reduced', re.compile(r'reduced:\s+([0-9]*)')),
    ('rephased', re.compile(r'rephased:\s+([0-9]*)')),
    ('restarts', re.compile(r'restarts:\s+([0-9]*)')),
    ('stabilizing', re.compile(r'stabilizing:\s+([0-9]*)')),
    ('subsumed', re.compile(r'subsumed:\s+([0-9]*)')),
    ('strengthened', re.compile(r'strengthened:\s+([0-9]*)')),
    ('trail_reuses', re.compile(r'trail reuses:\s+([0-9]*)')),
    ('time', re.compile(r'total process time since initialization:\s+([0-9]*.[0-9]*|0|0.0)'))
]


def get_solver_name():
    return 'cadical'


def get_savilerow_flag():
    return 'sat'


def get_savilerow_output_flag():
    return "-out-sat"


def get_savilerow_output_file(eprime_model, raw_instance):
    raw_eprime_model = os.path.basename(eprime_model).split(".")[0]
    return f'{raw_eprime_model}-{raw_instance}.dimacs'


def execute(output_file, stats):
    random_seed = 42
    return ['cadical', '-v', f'--seed={random_seed}', output_file]


def parse_std_out(out, instance_stats) -> Dict[str, str]:
    output = out.decode('ascii')
    # output = out
    stats = {
        'satisfiable': False
    }
    for line in output.splitlines():
        for matcher in patterns:
            if matcher[1].search(line):
                match = matcher[1].search(line)
                if "total process time since" in line:
                    stats["time"] = match.group(1)
                elif "trail reuses" in line:
                    stats["trail_reuses"] = match.group(1)
                else:
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
    return ['solver_satisfiable', *[f"solver_{p[0]}" for p in patterns],
            'solver_randomSeed', 'solver_time']

'''
s SATISFIABLE
c --- [ statistics ] ---------------------------------------------------------
c 
c chronological:              1164        40.12 %  of conflicts
c conflicts:                  2901      6685.92    per second
c decisions:                 19664     45319.51    per second
c learned:                    2671        92.07 %  per conflict
c learned_lits:             582374       100.00 %  learned literals
c minimized:                     0         0.00 %  learned literals
c shrunken:                 326276        56.03 %  learned literals
c minishrunken:              15729         2.70 %  learned literals
c otfs:                         12         0.41 %  of conflict
c propagations:            1097474         2.53 M  per second
c reduced:                     128         4.41 %  per conflict
c rephased:                      1      2901.00    interval
c restarts:                      5       580.20    interval
c stabilizing:                   1        65.53 %  of conflicts
c subsumed:                    508         0.04 %  of all clauses
c strengthened:                 12         0.00 %  of all clauses
c trail reuses:                  0         0.00 %  of incremental calls

'''
