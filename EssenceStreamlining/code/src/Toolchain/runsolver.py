import re
import logging
from typing import Dict


def get_output_file(thread_id, stage_name):
    return f'{stage_name}_{thread_id}.txt'


# -w /dev/null redirects the watcher output to /dev/null to prevent it filling up memory buffers
def execute(command, total_time, thread_id, stage_name):
    output_file = get_output_file(thread_id, stage_name)
    return ['runsolver', '-v', output_file, '-d 0', f'-W {total_time}', '-w /dev/null'] + command


pattern = re.compile(r'runsolver used ([0-9].[0-9]*)')

'''
# WCTIME: wall clock time in seconds
WCTIME=0.023697
# CPUTIME: CPU time in seconds (USERTIME+SYSTEMTIME)
CPUTIME=0.021245
# USERTIME: CPU time spent in user mode in seconds
USERTIME=0.015175
# SYSTEMTIME: CPU time spent in system mode in seconds
SYSTEMTIME=0.00607
# CPUUSAGE: CPUTIME/WCTIME in percent
CPUUSAGE=89.6528
# MAXVM: maximum virtual memory used in KiB
MAXVM=0
# TIMEOUT: did the solver exceed the time limit?
TIMEOUT=false
# MEMOUT: did the solver exceed the memory limit?
MEMOUT=false
'''

patterns = [
    ('WallClockTime', re.compile(r'WCTIME=([0-9]*.[0-9]*|0|[0-9]*)')),
    ('CPUTime', re.compile(r'CPUTIME=([0-9]*.[0-9]*|0|[0-9]*)')),
    ('UserTime', re.compile(r'USERTIME=([0-9]*.[0-9]*|0|[0-9]*)')),
    ('SystemTime', re.compile(r'SYSTEMTIME=([0-9]*.[0-9]*|0|[0-9]*)')),
    ('CPUUsage', re.compile(r'CPUUSAGE=([0-9]*.[0-9]*|0|[0-9]*)')),
    ('Timeout', re.compile(r'TIMEOUT=(false|true)'))
]


class RunsolverStats:

    def __init__(self,
                 time_out,
                 real_time,
                 cpu_time,
                 cpu_user_time,
                 cpu_system_time,
                 cpu_usage):
        self._time_out = time_out
        self._real_time = real_time
        self._cpu_time = cpu_time
        self._cpu_user_time = cpu_user_time
        self._cpu_system_time = cpu_system_time
        self._cpu_usage = cpu_usage

    def time_out(self):
        return self._time_out

    def get_real_time(self):
        return self._real_time

    def get_cpu_time(self):
        return self._cpu_time

    def __str__(self):
        return f'''
            'RealTime' : {self._real_time},
            'CPUTime' : {self._cpu_time},
            'CPUUserTime' : {self._cpu_user_time},
            'CPUSystemTime' : {self._cpu_system_time},
            'CPUUsage' : {self._cpu_usage},
            'Timeout' : {self._time_out}
        '''

    def keys(self):
        return {
            'RealTime': self._real_time,
            'CPUTime': self._cpu_time,
            'CPUUserTime': self._cpu_user_time,
            'CPUSystemTime': self._cpu_system_time,
            'CPUUsage': self._cpu_usage,
            'Timeout': self._time_out
        }


def _output_file(output_file):
    with open(output_file, 'r') as output_file:
        # output = output.decode('ascii')
        return output_file.read()


def grab_runsolver_stats(output_file):
    # logging.info(f"Output file {output_file}")
    output = _output_file(output_file)
    # logging.info(f"Output {output}")
    matches = {}
    for line in output.splitlines():
        # if 'Maximum wall clock time exceeded' in line:
        #     matches['time_out'] = True

        for matcher in patterns:
            if matcher[1].match(line):
                match = matcher[1].match(line)
                matches[matcher[0]] = match.group(1)
                break
    try:
        return RunsolverStats(matches['Timeout'] == 'true', float(matches['WallClockTime']), float(matches['CPUTime']),
                              float(matches['UserTime']), float(matches['SystemTime']), float(matches['CPUUsage']))
    except Exception as e:
        print(e)
        logging.info(f"output {output}")
        logging.info(f"matches {matches}")
        logging.info(e)
        raise Exception()


def _translate_to_runsolver_stats(result: Dict[str, str], prefix: str):
    return RunsolverStats(
        result[f'{prefix}_Timeout'],
        result[f'{prefix}_RealTime'],
        result[f'{prefix}_CPUTime'],
        result[f'{prefix}_CPUUserTime'],
        result[f'{prefix}_CPUSystemTime'],
        result[f'{prefix}_CPUUsage'],
    )
