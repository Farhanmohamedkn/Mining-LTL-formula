from dagSATencoding import DagSATEncoding
from z3 import *
depth=int(input("Enter the depth of the formula "))
fg = DagSATEncoding(depth)
fg.encodeFormula()
solverRes = fg.solver.check()
solverModel = fg.solver.model()
formula = fg.reconstructWholeFormula(solverModel)
print(formula)