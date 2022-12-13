import Toolchain.Chuffed as Chuffed
import Toolchain.Lingeling as Lingeling


def get_solver(solver):
    if solver == 'lingeling':
        return Lingeling
    elif solver == 'chuffed':
        return Chuffed
    else:
        raise Exception("Unsupported Solver")
