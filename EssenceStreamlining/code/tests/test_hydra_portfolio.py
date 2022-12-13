import Portfolio.HydraPortfolio as HydraPortfolio
import Toolchain.InstanceStats as InstanceStats
from Toolchain.runsolver import RunsolverStats
import pandas as pd

"""
    Test that a streamliner is not dominated by itself 
"""
def test_non_dominated():
    cur_portfolio = {
        '1': {
            HydraPortfolio.AVG_APPLIC_KEY: 1.0,
            HydraPortfolio.OVERALL_SOLVING_TIME_REDUCTION_KEY: 0.5,
            HydraPortfolio.MEAN_REDUCTION_KEY: 0.5,
            HydraPortfolio.MEDIAN_REDUCTION_KEY: 0.5,
            HydraPortfolio.STD_DEV_KEY: 0.5,
            HydraPortfolio.QUANTILES_KEY: [0.5, 0.5, 0.5]
        }
    }
    best_instance_stats = {}
    overall_portfolio = {}
    hydraEval = HydraPortfolio.HydraEval(overall_portfolio, best_instance_stats)
    x = {HydraPortfolio.AVG_APPLIC_KEY: 1.0,
         HydraPortfolio.OVERALL_SOLVING_TIME_REDUCTION_KEY: 0.5,
         HydraPortfolio.MEAN_REDUCTION_KEY: 0.5,
         HydraPortfolio.MEDIAN_REDUCTION_KEY: 0.5,
         HydraPortfolio.STD_DEV_KEY: 0.5,
         HydraPortfolio.QUANTILES_KEY: [0.5, 0.5, 0.5]}
    assert hydraEval._non_dominated(x, cur_portfolio) is True


def test_dominated():
    cur_portfolio = {
        '1': {
            HydraPortfolio.AVG_APPLIC_KEY: 1.0,
            HydraPortfolio.OVERALL_SOLVING_TIME_REDUCTION_KEY: 0.5,
            HydraPortfolio.MEAN_REDUCTION_KEY: 0.8,
            HydraPortfolio.MEDIAN_REDUCTION_KEY: 0.5,
            HydraPortfolio.STD_DEV_KEY: 0.5,
            HydraPortfolio.QUANTILES_KEY: [0.5, 0.5, 0.5]
        }
    }
    best_instance_stats = {}
    overall_portfolio = {}
    hydraEval = HydraPortfolio.HydraEval(overall_portfolio, best_instance_stats)
    x = {HydraPortfolio.AVG_APPLIC_KEY: 1.0,
         HydraPortfolio.OVERALL_SOLVING_TIME_REDUCTION_KEY: 0.5,
         HydraPortfolio.MEAN_REDUCTION_KEY: 0.5,
         HydraPortfolio.MEDIAN_REDUCTION_KEY: 0.5,
         HydraPortfolio.STD_DEV_KEY: 0.5,
         HydraPortfolio.QUANTILES_KEY: [0.5, 0.5, 0.5]}
    assert hydraEval._non_dominated(x, cur_portfolio) is False


def test_remove_dominated_combinations():
    """
    Ensure that dominated combinations are removed from the portfolio
    """
    cur_portfolio = {
        '1': {
            HydraPortfolio.AVG_APPLIC_KEY: 0.5,
            HydraPortfolio.OVERALL_SOLVING_TIME_REDUCTION_KEY: 0.5,
            HydraPortfolio.MEAN_REDUCTION_KEY: 0.3,
            HydraPortfolio.MEDIAN_REDUCTION_KEY: 0.5,
            HydraPortfolio.STD_DEV_KEY: 0.5,
            HydraPortfolio.QUANTILES_KEY: [0.5, 0.5, 0.5]
        }, '2': {
            HydraPortfolio.AVG_APPLIC_KEY: 0.4,
            HydraPortfolio.OVERALL_SOLVING_TIME_REDUCTION_KEY: 0.5,
            HydraPortfolio.MEAN_REDUCTION_KEY: 0.3,
            HydraPortfolio.MEDIAN_REDUCTION_KEY: 0.5,
            HydraPortfolio.STD_DEV_KEY: 0.5,
            HydraPortfolio.QUANTILES_KEY: [0.5, 0.5, 0.5]
        },
        '3' : {
            HydraPortfolio.AVG_APPLIC_KEY: 1.0,
            HydraPortfolio.OVERALL_SOLVING_TIME_REDUCTION_KEY: 0.5,
            HydraPortfolio.MEAN_REDUCTION_KEY: 0.5,
            HydraPortfolio.MEDIAN_REDUCTION_KEY: 0.5,
            HydraPortfolio.STD_DEV_KEY: 0.5,
            HydraPortfolio.QUANTILES_KEY: [0.5, 0.5, 0.5]
        }

    }
    best_instance_stats = {}
    overall_portfolio = {}
    hydraEval = HydraPortfolio.HydraEval(overall_portfolio, best_instance_stats)
    x = {HydraPortfolio.AVG_APPLIC_KEY: 1.0,
         HydraPortfolio.OVERALL_SOLVING_TIME_REDUCTION_KEY: 0.5,
         HydraPortfolio.MEAN_REDUCTION_KEY: 0.5,
         HydraPortfolio.MEDIAN_REDUCTION_KEY: 0.5,
         HydraPortfolio.STD_DEV_KEY: 0.5,
         HydraPortfolio.QUANTILES_KEY: [0.5, 0.5, 0.5]}
    new_portfolio = hydraEval._remove_dominated_combinations(x, cur_portfolio)
    assert len(new_portfolio) == 1



def test_objective_values():

    instanceStats = InstanceStats.InstanceStats()
    instanceStats.add_solver_output({
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
        'randomSeed' : 1000
    })
    instanceStats.set_solver_name('chuffed')
    results = {'d02a86e7b42bb3f97f70d61c1daa73bf.param': instanceStats}

    runsolverStats = RunsolverStats(False, 6.0, 6.0, 6.0, 6.0, 6.0)
    instanceStats.add_stage_stats('chuffed', runsolverStats)

    # test_df = pd.read_csv('./tests/BaseModelResults.csv')

    test_df = pd.DataFrame()
    test_df[['Instance', 'solver_time']] = [['d02a86e7b42bb3f97f70d61c1daa73bf.param', 6.0]]
    cur_portfolio = {}
    best_instance_stats = {}
    overall_portfolio = {}
    hydraEval = HydraPortfolio.HydraEval(overall_portfolio, best_instance_stats)
    objectiveValues = (hydraEval._objective_values(results, test_df))
    assert(objectiveValues['MeanReduction'] == 0)
    assert(objectiveValues['OverallSolvingTimeReduction'] == 0)

    test_df = pd.DataFrame()
    test_df[['Instance', 'solver_time']] = [['d02a86e7b42bb3f97f70d61c1daa73bf.param', 12.0]]
    hydraEval = HydraPortfolio.HydraEval(overall_portfolio, best_instance_stats)
    objectiveValues = (hydraEval._objective_values(results, test_df))
    assert(objectiveValues['MeanReduction'] == 0.5)
    assert(objectiveValues['OverallSolvingTimeReduction'] == 0.5)


def test_hydra_combination():

    instanceStats = InstanceStats.InstanceStats()
    instanceStats.add_solver_output({
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
        'randomSeed' : 1000
    })
    instanceStats.set_solver_name('chuffed')
    instanceStats.set_satisfiable(False)
    results = {'d02a86e7b42bb3f97f70d61c1daa73bf.param': instanceStats}

    bestInstanceStats = InstanceStats.InstanceStats()
    bestInstanceStats.add_solver_output({
        'nodes': 1000,
        'failures': 10,
        'restarts': 10,
        'variables': 10,
        'intVars': 100,
        'boolVariables': 100,
        'propagators': 100,
        'propagations': 1000,
        'peakDepth': 1000,
        'nogoods': 1000,
        'backjumps': 100,
        'peakMem': 0.0,
        'time': 20,
        'initTime': 1,
        'solveTime': 3.0,
        'objective': -1,
        'baseMem': 0.0,
        'trailMem': 1.0,
        'randomSeed': 1000
    })
    bestInstanceStats.set_solver_name('chuffed')
    bestInstanceStats.set_satisfiable(False)

    runsolverStats = RunsolverStats(False, 6.0, 6.0, 6.0, 6.0, 6.0)
    instanceStats.add_stage_stats('chuffed', runsolverStats)
    bestInstanceStats.add_stage_stats('chuffed', runsolverStats)

    # test_df = pd.read_csv('./tests/BaseModelResults.csv')

    test_df = pd.DataFrame()
    test_df[['Instance', 'solver_time', 'Satisfiable']] = [['d02a86e7b42bb3f97f70d61c1daa73bf.param', 6.0, True]]
    overall_portfolio = {}
    best_instance_stats = {'d02a86e7b42bb3f97f70d61c1daa73bf.param': bestInstanceStats}
    hydraEval = HydraPortfolio.HydraEval(overall_portfolio, best_instance_stats)
    test_result = hydraEval._test(instanceStats, best_instance_stats.get('d02a86e7b42bb3f97f70d61c1daa73bf.param'))


    assert not test_result


def test_combined_stats():
    instance = 'd02a86e7b42bb3f97f70d61c1daa73bf.param'
    instanceStats = InstanceStats.InstanceStats()
    instanceStats.add_solver_output({
        'nodes': 1000,
        'failures': 10,
        'restarts': 10,
        'variables': 10,
        'intVars': 100,
        'boolVariables': 100,
        'propagators': 100,
        'propagations': 1000,
        'peakDepth': 1000,
        'nogoods': 1000,
        'backjumps': 100,
        'peakMem': 0.0,
        'time': 20,
        'initTime': 1,
        'solveTime': 6.0,
        'objective': -1,
        'baseMem': 0.0,
        'trailMem': 1.0,
        'randomSeed': 1000
    })
    instanceStats.set_solver_name('chuffed')
    instanceStats.set_satisfiable(False)

    bestInstanceStats = InstanceStats.InstanceStats()
    bestInstanceStats.add_solver_output({
        'nodes': 1000,
        'failures': 10,
        'restarts': 10,
        'variables': 10,
        'intVars': 100,
        'boolVariables': 100,
        'propagators': 100,
        'propagations': 1000,
        'peakDepth': 1000,
        'nogoods': 1000,
        'backjumps': 100,
        'peakMem': 0.0,
        'time': 20,
        'initTime': 1,
        'solveTime': 3.0,
        'objective': -1,
        'baseMem': 0.0,
        'trailMem': 1.0,
        'randomSeed': 1000
    })
    bestInstanceStats.set_solver_name('chuffed')
    bestInstanceStats.set_satisfiable(True)

    runsolverStats = RunsolverStats(False, 6.0, 6.0, 6.0, 6.0, 6.0)
    bestRunsolverStats = RunsolverStats(False, 3.0, 3.0, 3.0, 3.0, 3.0)
    instanceStats.add_stage_stats('chuffed', runsolverStats)
    bestInstanceStats.add_stage_stats('chuffed', bestRunsolverStats)

    test_df = pd.DataFrame()
    test_df[['Instance', 'solver_time', 'Satisfiable']] = [[instance, 6.0, True]]
    best_instance_stats = {instance : bestInstanceStats}
    overall_portfolio = {}
    hydraEval = HydraPortfolio.HydraEval(overall_portfolio, best_instance_stats)

    results = {instance: instanceStats}
    combined_results = hydraEval.combine_results(results)

    objectiveValuesPreCombination = (hydraEval._objective_values(results, test_df))
    objectiveValues = (hydraEval._objective_values(combined_results, test_df))

    assert (objectiveValues['MeanReduction'] == 0.5)
    assert (objectiveValues['OverallSolvingTimeReduction'] == 0.5)
    assert (objectiveValues['AvgApplic'] == 1.0)
    assert (objectiveValuesPreCombination['AvgApplic'] == 0.0)
    assert combined_results[instance].satisfiable()
    assert combined_results[instance] is bestInstanceStats
    assert combined_results[instance].solver_time() == 3.0

