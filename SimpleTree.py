import pdb
import re
symmetric_operators = ["&", "|"]
binary_operators = ["&", "|", "U","->"]
unary_operators = ["X", "F", "G", "!"]
class SimpleTree:
    def __init__(self, label = "dummy"):
        self.left = None
        self.right = None
        self.label = label
    
    def __hash__(self):
        return hash((self.label, self.left, self.right))
    
    def __eq__(self, other):
        if other == None:
            return False
        else:
            return self.label == other.label and self.left == other.left and self.right == other.right
    
    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        if self.left == None and self.right == None:
            return self.label
        
        # the (not enforced assumption) is that if a node has only one child, that is the left one
        elif self.left != None and self.right == None:
            return self.label + '(' + self.left.__repr__() + ')'
        
        elif self.left != None and self.right != None:
            return self.label + '(' + self.left.__repr__() + ',' + self.right.__repr__() + ')'


class Formula(SimpleTree):
    
    def __init__(self, formulaArg = "dummyF"):
        
        if not isinstance(formulaArg, str):
            self.label = formulaArg[0]
            self.left = formulaArg[1]
            try:
                self.right = formulaArg[2]
            except:
                self.right = None
        else:
            super().__init__(formulaArg)
        
        