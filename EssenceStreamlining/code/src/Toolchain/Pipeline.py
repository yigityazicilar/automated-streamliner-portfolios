import logging
import Toolchain.Conjure as Conjure
import Toolchain.runsolver as runsolver
import Toolchain.savilerow as savilerow
from Toolchain.InstanceStats import InstanceStats
from Toolchain.StageTimeout import StageTimeout
import threading
import subprocess
from subprocess import TimeoutExpired


class Stage:

    def __init__(self, name,
                 stage_callable,
                 args):
        logging.info(f"Stagle callable {stage_callable}")
        self.name = name
        self.stage_callable = stage_callable
        self.args = args

    def parse_std_out(self, outs):
        pass

    def parse_std_err(self, outs):
        pass

    def get_name(self):
        return self.name


class Pipeline:

    def __init__(self, eprime_model, essence_param_file, solver, event, total_time, stats):
        self.eprime_model = eprime_model
        raw_eprime_model = eprime_model.split(".")[0]
        self.total_time = total_time
        self.essence_param_file = essence_param_file
        self.raw_instance = self.essence_param_file.split("/")[-1].split(".")[0]
        self.event = event
        self.output_eprime_param = f"{raw_eprime_model}-{self.raw_instance}.eprime-param"
        self.solver = solver
        self.conjure_stage = Stage('conjure', Conjure.translate_essence_param,
                                   (eprime_model, essence_param_file, self.output_eprime_param,))
        self.savilerow_stage = Stage('savilerow', savilerow.formulate,
                                     (self.eprime_model, self.output_eprime_param, solver, self.raw_instance,))
        self.solver_stage = Stage(solver.get_solver_name(), solver.execute,
                                  (solver.get_savilerow_output_file(self.eprime_model, self.raw_instance), stats,))

    def _run_stage(self, stage, runsolver_command, instance_stats):
        logging.debug(f"Running stage {stage.get_name()}")
        process = subprocess.Popen(runsolver_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            try:
                outs, errs = process.communicate(timeout=5)

                if outs:
                    stage.parse_std_out(outs)
                    # logging.info(outs)
                if errs:
                    stage.parse_std_err(errs)
                    # logging.info(errs)

                return outs, errs
            except TimeoutExpired:
                logging.debug("Process still running.")

            if self.event.is_set():
                logging.debug(f"Flag is set, killing current command {runsolver_command}")
                # instance_stats['killed'] = True
                instance_stats.set_killed()
                # Kill Process
                process.kill()
                # Clear out any last buffers
                outs, errs = process.communicate()
                return outs, errs

    def _call(self, stage, instance_stats):
        command = stage.stage_callable(*stage.args)
        runsolver_command = runsolver.execute(command, int(self.total_time), threading.get_ident(), stage.get_name())
        logging.debug(f"Executing {runsolver_command} on thread {threading.get_ident()}")

        outs, errs = self._run_stage(stage, runsolver_command, instance_stats)

        # Grab runsolver related stats
        runsolver_stats = runsolver.grab_runsolver_stats(
            runsolver.get_output_file(threading.get_ident(), stage.get_name()))
        instance_stats.add_stage_stats(stage.get_name(), runsolver_stats)

        self.total_time -= runsolver_stats.get_real_time()

        if runsolver_stats.time_out():
            logging.debug("Stage timed out")
            instance_stats.set_timeout()
            raise StageTimeout(f"{stage.get_name()} ran out of time")

        logging.debug(f"Total time left {self.total_time}")
        return outs, errs

    def execute(self):
        logging.debug(f"Executing pipeline {self.raw_instance} with model {self.eprime_model}")

        instance_stats = InstanceStats()

        try:
            # Translate Parameter file
            self._call(self.conjure_stage, instance_stats)
            # Savilerow
            self._call(self.savilerow_stage, instance_stats)
            # Solver
            outs, errs = self._call(self.solver_stage, instance_stats)

            solver_output = self.solver.parse_output(outs)
            instance_stats.add_solver_output(solver_output)
            instance_stats.set_solver_name(self.solver_stage.get_name())
            if not solver_output['satisfiable'] or instance_stats.timeout():
                # logging.debug("Solver is unsat")
                instance_stats.set_satisfiable(False)
            # logging.info("Returning instance_stats")
        except StageTimeout as e:
            instance_stats.set_satisfiable(False)
        return instance_stats
