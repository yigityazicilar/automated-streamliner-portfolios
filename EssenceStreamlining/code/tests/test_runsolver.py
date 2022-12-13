import Toolchain.Pipeline as Pipeline
from Toolchain.InstanceStats import InstanceStats
import Toolchain.Chuffed as Chuffed
import Toolchain.SolverFactory as SolverFactory
import Toolchain.runsolver as runsolver
import pytest
import Toolchain.StageTimeout as StageTimeout


def test_runsolver_parsing(mocker):
    output_file_output = 'WCTIME=4.11755\n' +\
        '# CPUTIME: CPU time in seconds (USERTIME+SYSTEMTIME)\n'+\
        'CPUTIME=5.47083\n' + \
        '# USERTIME: CPU time spent in user mode in seconds\n' +\
        'USERTIME=4.82694\n' + \
        '# SYSTEMTIME: CPU time spent in system mode in seconds\n' +\
        'SYSTEMTIME=0.643888\n' +\
        '# CPUUSAGE: CPUTIME/WCTIME in percent\n' +\
        'CPUUSAGE=132.866\n' +\
        '# MAXVM: maximum virtual memory used in KiB\n' +\
        'MAXVM=11385640\n' +\
        '# TIMEOUT: did the solver exceed the time limit?\n' +\
        'TIMEOUT=true\n' +\
        '# MEMOUT: did the solver exceed the memory limit?\n' +\
        'MEMOUT=false\n'


    mocker.patch.object(runsolver, '_output_file', return_value=output_file_output)
    stats = runsolver.grab_runsolver_stats('test')
    assert stats.time_out() == True
    assert stats.get_cpu_time() == 5.47083
    assert stats.get_real_time() == 4.11755

