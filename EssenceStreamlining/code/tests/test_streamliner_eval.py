import Toolchain.Pipeline as Pipeline
from Toolchain.InstanceStats import InstanceStats
import Toolchain.Chuffed as Chuffed
import Toolchain.SolverFactory as SolverFactory
import Toolchain.runsolver as runsolver
import pytest
import Toolchain.StageTimeout as StageTimeout

# Test that the pipeline object renders a StageTimeout when RunSolver times out a particular stage
def test_pipeline_call(mocker):
    stage = Pipeline.Stage('test_stage', lambda : 'test', ())
    stats = InstanceStats()
    runsolver_stats = runsolver.RunsolverStats(True, 6.0, 6.0, 6.0, 6.0, 6.0)

    p = Pipeline.Pipeline('model000001.eprime','model.essence', SolverFactory.get_solver('chuffed'), None, 100, stats)
    # Patch the _run_stage method
    mocker.patch.object(Pipeline.Pipeline, '_run_stage', return_value=(None, None))
    mocker.patch.object(runsolver, 'execute', return_value='')
    mocker.patch.object(runsolver, 'grab_runsolver_stats', return_value=runsolver_stats)

    with pytest.raises(StageTimeout.StageTimeout) as e_info:
        p._call(stage, stats)

    # Assert that the total time was decremented
    assert p.total_time == 94
    # Assert that the instance stats is set to Timeout
    assert stats.timeout() == True
    # Assert that the instance stats is unsat
    assert stats.satisfiable() == False
    # with mocker.Ipatch.object(p, '_run_stage', return_value=None) as pipeline:
    #     print(pipeline)
    #     pipeline._call(stage, {})
    # m = mocker.patch("src.Toolchain.Pipeline.Pipeline")
    # m._call({}, {})

# Test that the pipeline object renders a StageTimeout when one of the stages times out
def test_pipeline_execute(mocker):
    stage = Pipeline.Stage('test_stage', lambda : 'test', ())
    # stats = InstanceStats()
    runsolver_stats = runsolver.RunsolverStats(True, 6.0, 6.0, 6.0, 6.0, 6.0)

    p = Pipeline.Pipeline('model000001.eprime','model.essence', SolverFactory.get_solver('chuffed'), None, 100, {})
    # Patch the _run_stage method
    mocker.patch.object(Pipeline.Pipeline, '_run_stage', return_value=(None, None))
    mocker.patch.object(runsolver, 'execute', return_value='')
    mocker.patch.object(runsolver, 'grab_runsolver_stats', return_value=runsolver_stats)

    stats = p.execute()

    # Assert that the total time was decremented
    assert p.total_time == 94
    # Assert that the instance stats is set to Timeout
    assert stats.timeout() == True
    # Assert that the instance stats is unsat
    assert stats.satisfiable() == False
    # with mocker.Ipatch.object(p, '_run_stage', return_value=None) as pipeline:
    #     print(pipeline)
    #     pipeline._call(stage, {})
    # m = mocker.patch("src.Toolchain.Pipeline.Pipeline")
    # m._call({}, {})


def test_pipeline_execute_solver_unsat(mocker):
    stage = Pipeline.Stage('test_stage', lambda : 'test', ())
    # stats = InstanceStats()
    runsolver_stats = runsolver.RunsolverStats(False, 6.0, 6.0, 6.0, 6.0, 6.0)

    p = Pipeline.Pipeline('model000001.eprime','model.essence', SolverFactory.get_solver('chuffed'), None, 100, {})
    # Patch the _run_stage method
    mocker.patch.object(Pipeline.Pipeline, '_call', return_value=(None, None))
    mocker.patch.object(runsolver, 'execute', return_value='')
    mocker.patch.object(runsolver, 'grab_runsolver_stats', return_value=runsolver_stats)


    mocker.patch.object(Chuffed, 'parse_output', return_value={
        'nodes' : 1000,
        'failures' : 10,
        'restarts' : 10,
        'variables' : 10,
        'intVars' : 100,
        'boolVariables' : 100,
        'propagators': 100,
        'propagations' : 1000,
        'peakDepth' : 1000,
        'nogoods' : 1000,
        'backjumps': 100,
        'peakMem': 0.0,
        'time' : 20,
        'initTime' : 1,
        'solveTime' : 6.0,
        'objective' : -1,
        'baseMem': 0.0,
        'trailMem' : 1.0,
        'randomSeed' : 1000,
        'satisfiable' : False
    })

    stats = p.execute()

    # Assert that the instance stats is unsat as the solver is unsat
    assert stats.satisfiable() == False