from z3 import *

from SimpleTree import Formula

from lark import Lark, Transformer


class DagSATEncoding:
    def __init__(self, D):

        defaultOperators = ['&', 'F', 'G', '!', 'U', '|', '->', 'X']
        unary = ['G', 'F', '!', 'X']
        binary = ['&', '|', 'U', '->']
        numOfVariables = 4
        startOfFormula = '->var0&var1'
        result = []

        # print(result)
        # self.result = result
        self.result = ['!', 'F', '&', 1]
        # except for the operators, the nodes of the "syntax table" are additionally the propositional variables

        self.listOfOperators = defaultOperators

        self.unaryOperators = unary

        self.binaryOperators = binary

        self.solver = Solver()

        self.numOfVariables = numOfVariables  # p,q,r,s..etc
        self.formulaDepth = D

        self.listOfVariables = [i for i in range(
            self.numOfVariables)]  # propositions

    """
    the working variables are
        - x[i][o]: i is a subformula (row) identifier, o is an operator or a propositional variable. Meaning is "subformula i is an operator (variable) o"
        - l[i][j]:  "left operand of subformula i is subformula j"
        - r[i][j]: "right operand of subformula i is subformula j"
    """

    def encodeFormula(self, unsatCore=True):
        self.operatorsAndVariables = self.listOfOperators + self.listOfVariables

        self.x = {(i, o): Bool('x_' + str(i) + '_' + str(o))
                  for i in range(self.formulaDepth)
                  for o in self.operatorsAndVariables}
        self.l = {(parentOperator, childOperator): Bool('l_' + str(parentOperator) + '_' + str(childOperator))
                  for parentOperator in range(1, self.formulaDepth)
                  for childOperator in range(parentOperator)}
        self.r = {(parentOperator, childOperator): Bool('r_' + str(parentOperator) + '_' + str(childOperator))
                  for parentOperator in range(1, self.formulaDepth)
                  for childOperator in range(parentOperator)}
        # for m, j in zip(range(self.formulaDepth-1, 0, -1), range(len(self.result))):
        #     self.x[(m, self.result[j])] = True

        self.solver.set(unsat_core=unsatCore)

        self.exactlyOneOperator()
        self.firstOperatorVariable()
        self.noDanglingVariables()
        self.completingSketch()

    def completingSketch(self):
        for m, j in zip(range(self.formulaDepth-1, 0, -1), range(len(self.result))):
            self.solver.add(Or([self.x[(m, self.result[j])]]))

    def firstOperatorVariable(self):
        self.solver.add(
            Or([self.x[k] for k in self.x if k[0] == 0 and k[1] in self.listOfVariables]))

    def exactlyOneOperator(self):

        self.solver.assert_and_track(And([
            AtMost([self.x[k] for k in self.x if k[0] == i] + [1])
            for i in range(self.formulaDepth)
        ]),
            "at most one operator per subformula"
        )

        self.solver.assert_and_track(And([
            AtLeast([self.x[k] for k in self.x if k[0] == i] + [1])
            for i in range(self.formulaDepth)
        ]),
            "at least one operator per subformula"
        )

        if (self.formulaDepth > 0):
            self.solver.assert_and_track(And([
                Implies(
                    Or(
                        [self.x[(
                            i, op)] for op in self.binaryOperators + self.unaryOperators]
                    ),
                    AtMost([self.l[k] for k in self.l if k[0] == i] + [1])
                )
                for i in range(1, self.formulaDepth)
            ]),
                "at most one left operator for binary and unary operators"
            )

        if (self.formulaDepth > 0):
            self.solver.assert_and_track(And([
                Implies(
                    Or(
                        [self.x[(i, op)] for op in
                         self.binaryOperators + self.unaryOperators]
                    ),
                    AtLeast([self.l[k] for k in self.l if k[0] == i] + [1])
                )
                for i in range(1, self.formulaDepth)
            ]),
                "at least one left operator for binary and unary operators"
            )

        if (self.formulaDepth > 0):
            self.solver.assert_and_track(And([
                Implies(
                    Or(
                        [self.x[(i, op)] for op in self.binaryOperators]
                    ),
                    AtMost([self.r[k] for k in self.r if k[0] == i] + [1])
                )
                for i in range(1, self.formulaDepth)
            ]),
                "at most one right operator for binary"
            )

        if (self.formulaDepth > 0):
            self.solver.assert_and_track(And([
                Implies(
                    Or(
                        [self.x[(i, op)] for op in
                         self.binaryOperators]
                    ),
                    AtLeast([self.r[k] for k in self.r if k[0] == i] + [1])
                )
                for i in range(1, self.formulaDepth)
            ]),
                "at least one right operator for binary"
            )

        if (self.formulaDepth > 0):
            self.solver.assert_and_track(And([
                Implies(
                    Or(
                        [self.x[(i, op)] for op in
                         self.unaryOperators]
                    ),
                    Not(
                        Or([self.r[k] for k in self.r if k[0] == i])
                    )
                )
                for i in range(1, self.formulaDepth)
            ]),
                "no right operators for unary"
            )

        if (self.formulaDepth > 0):
            self.solver.assert_and_track(And([
                Implies(
                    Or(
                        [self.x[(i, op)] for op in
                         self.listOfVariables]
                    ),
                    Not(
                        Or(
                            Or([self.r[k] for k in self.r if k[0] == i]),
                            Or([self.l[k] for k in self.l if k[0] == i])
                        )

                    )
                )
                for i in range(1, self.formulaDepth)
            ]),
                "no left or right children for variables"
            )

    def noDanglingVariables(self):
        if self.formulaDepth > 0:
            self.solver.assert_and_track(
                And([
                    Or(
                        AtLeast([self.l[(rowId, i)] for rowId in range(
                            i + 1, self.formulaDepth)] + [1]),
                        AtLeast([self.r[(rowId, i)]
                                for rowId in range(i + 1, self.formulaDepth)] + [1])
                    )
                    for i in range(self.formulaDepth - 1)]
                    ),
                "no dangling variables"
            )

    def reconstructWholeFormula(self, model):
        return self.reconstructFormula(self.formulaDepth - 1, model)

    def reconstructFormula(self, rowId, model):
        # for m, j in zip(range(self.formulaDepth-1, 0, -1),range(len(self.result))):
        #     model[self.x[(m, self.result[j])]]=True

        def getValue(row, vars):
            # try:
            tt = [k[1]
                for k in vars if k[0] == row and model[vars[k]] == True]
            # except:
            #     tt = [k[1]
            #           for k in vars if k[0] == row and vars[k] == True]

            if len(tt) > 1:
                raise Exception("more than one true value")
            else:
                return tt[0]

        operator = getValue(rowId, self.x)
        if operator in self.listOfVariables:
            return Formula('var' + str(operator))
        elif operator in self.unaryOperators:
            leftChild = getValue(rowId, self.l)
            return Formula([operator, self.reconstructFormula(leftChild, model)])
        elif operator in self.binaryOperators:
            leftChild = getValue(rowId, self.l)
            rightChild = getValue(rowId, self.r)
            return Formula([operator, self.reconstructFormula(leftChild, model), self.reconstructFormula(rightChild, model)])
