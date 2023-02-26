from dagSATencoding import DagSATEncoding
from z3 import *
fg = DagSATEncoding(5)
fg.encodeFormula()
solverRes = fg.solver.check()
solverModel = fg.solver.model()
formula = fg.reconstructWholeFormula(solverModel)
print(formula)