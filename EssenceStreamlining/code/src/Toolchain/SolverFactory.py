import Toolchain.Chuffed as Chuffed
import Toolchain.Lingeling as Lingeling
import Toolchain.Cadical as Cadical


def get_solver(solver):
    if solver == 'lingeling':
        return Lingeling
    elif solver == 'chuffed':
        return Chuffed
    elif solver == 'cadical':
        return Cadical
    else:
        raise Exception("Unsupported Solver")
