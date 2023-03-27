import pdb
import re
from lark import Lark, Transformer
from lark.tree import Tree
from lark.lexer import Token
from collections import deque
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
    
    def _isLeaf(self):
        return self.right == None and self.left == None
    
    def _addLeftChild(self, child):
        if child == None:
            return
        if type(child) is str:
            child = SimpleTree(child)
        self.left = child

    def _addRightChild(self, child):
        if type(child) is str:
            child = SimpleTree(child)
        self.right = child

    def addChildren(self, leftChild = None, rightChild = None): 
        self._addLeftChild(leftChild)
        self._addRightChild(rightChild)

    def addChild(self, child):
        self._addLeftChild(child)
    
    def getAllNodes(self):
        leftNodes = []
        rightNodes = []
        
        if self.left != None:
            leftNodes = self.left.getAllNodes()
        if self.right != None:
            rightNodes = self.right.getAllNodes()
        return [self] + leftNodes + rightNodes
    
    def getAllLabels(self):
        if self.left != None:
            leftLabels = self.left.getAllLabels()
        else:
            leftLabels = []
            
        if self.right != None:
            rightLabels = self.right.getAllLabels()
        else:
            rightLabels = []
        return [self.label] + leftLabels + rightLabels
    

    def __repr__(self):
        if self.left == None and self.right == None:
            return self.label
        
        # the (not enforced assumption) is that if a node has only one child, that is the left one
        elif self.left != None and self.right == None:
            return self.label + '(' + self.left.__repr__() + ')'
        
        elif self.left != None and self.right != None:
            return self.label + '(' + self.left.__repr__() + ',' + self.right.__repr__() + ')'


class Formula(SimpleTree):
    index=1
    indexArray=[5,4,3,2,1]

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

    def __lt__(self, other):

        if self.getDepth() < other.getDepth():
            return True
        elif self.getDepth() > other.getDepth():
            return False
        else:
            if self._isLeaf() and other._isLeaf():
                return self.label < other.label

            if self.left != other.left:
                return self.left < other.left

            if self.right is None:
                return False
            if other.right is None:
                return True
            if self.right != other.right:
                return self.right < other.right

            else:
                return self.label < other.label
            
    def pop_one(arr):
        if arr:
            return arr.pop(0)
        else:
            return None
    
    def label_nodes(root, label): 
        if(root):
            if(root.label):
                print(root.label, label)
                Formula.pop_one(Formula.indexArray)
            if(root.left):
                if(hasattr(root.left,'label')):
                    print(root.left.label, Formula.indexArray[0])
                    
                    # Formula.label_nodes(root.left, Formula.indexArray[0])
                     
                else:
                    print(root.left.data, Formula.indexArray[0])
                Formula.pop_one(Formula.indexArray)
            if(root.right):
                if(hasattr(root.right,'label')):
                    print(root.right.label, Formula.indexArray[0])
                    
                    # Formula.label_nodes(root.right, Formula.indexArray[0])
                else:
                    print(root.right.data, Formula.indexArray[0]) 
                Formula.pop_one(Formula.indexArray)
            
        return label

    def printLevelOrder(root):
        h = Formula.height(root)
        array=[]
        for i in range(1, h+1):
            Formula.printCurrentLevel(root, i, array)
        return array
    
    
    # Print nodes at a current level
    def printCurrentLevel(root, level, array):
        if root is None:
            return
        if level == 1:
            if(hasattr(root,'label')):
                array.append(root.label) 
            if(hasattr(root,'data')):
                array.append(root.data) 
        elif level > 1:
            if(hasattr(root,'left')):
                Formula.printCurrentLevel(root.left, level-1, array)
            if(hasattr(root,'right')):
                Formula.printCurrentLevel(root.right, level-1, array)
 

 
 
    def height(node):
        if node is None:
            return 0
        else:
            lheight=rheight=1
            # Compute the height of each subtree
            if(hasattr(node,'left')):
                lheight = Formula.height(node.left)
            if(hasattr(node,'right')):
                rheight = Formula.height(node.right)
    
            # Use the larger one
            if lheight > rheight:
                return lheight+1
            else:
                return rheight+1
    def bfs_traversal(root):
        if not root:
            return []
        queue = deque([root])
        res = []
        while queue:
            node = queue.popleft()
            if(hasattr(node,'label')):
                res.append(node.label)
                if (hasattr(node,'left')):
                    queue.append(node.left)
                if (hasattr(node,'right')):
                    queue.append(node.right)
        return res
    @classmethod
    def convertTextToFormula(cls, formulaText):
        
        f = Formula()
        try:
            formula_parser = Lark(r"""
                ?formula: _binary_expression
                        |_unary_expression
                        | constant
                        | variable
                        | unknown
                !constant: "true"
                        | "false"
                _binary_expression: binary_operator "(" formula "," formula ")"
                _unary_expression: unary_operator "(" formula ")"
                variable: /var[0-9]*/
                unknown:  /\?[0-9]*/
                !binary_operator: "&" | "|" | "->" | "U"
                !unary_operator: "F" | "G" | "!" | "X"
                
                %import common.SIGNED_NUMBER
                %import common.WS
                %ignore WS 
             """, start = 'formula')
        
            
            tree = formula_parser.parse(formulaText)
            print(f"tree= {tree.pretty()}")
            
            
        except Exception as e:
            print("can't parse formula %s" %formulaText)
            print("error: %s" %e)
            
        
        f = TreeToFormula().transform(tree)
        # print(f"fromula= {f.getAllLabels()}")
        # print(f"Available nodes= {f.getAllNodes()}")
        # print(f"Available variables= {f.getAllVariables()}")
        # print(f"Available subformula= {f.getNumberOfSubformulas()}")
        # print(f"Available setsubformula= {f.getSetOfSubformulas()}")
        # labels = Formula.label_nodes(f,Formula.indexArray[0])
        test = Formula.printLevelOrder(f)
        print(test)
        return test

    





    def prettyPrint(self, top=False):
        if top is True:
            lb = ""
            rb = ""
        else:
            lb = "("
            rb = ")"
        if self._isLeaf():
            return self.label
        if self.label in unary_operators:
            return lb + self.label +" "+ self.left.prettyPrint() + rb
        if self.label in binary_operators:
            return lb + self.left.prettyPrint() +" "+  self.label +" "+ self.right.prettyPrint() + rb
        
    def getAllVariables(self):
        allNodes = list(set(self.getAllNodes()))
        return [ node for node in allNodes if node._isLeaf() == True ]
    
    def getDepth(self):
        if self.left == None and self.right == None:
            return 0
        leftValue = -1
        rightValue = -1
        if self.left != None:
            leftValue = self.left.getDepth()
        if self.right != None:
            rightValue = self.right.getDepth()
        return 1 + max(leftValue, rightValue)
    
    def getNumberOfSubformulas(self):
        return len(self.getSetOfSubformulas())
    
    def getSetOfSubformulas(self):
        if self.left == None and self.right == None:
            return [repr(self)]
        leftValue = []
        rightValue = []
        if self.left != None:
            leftValue = self.left.getSetOfSubformulas()
        if self.right != None:
            rightValue = self.right.getSetOfSubformulas()
        return list(set([repr(self)] + leftValue + rightValue))
    
class TreeToFormula(Transformer):
        def formula(self, formulaArgs):
            
            return Formula(formulaArgs)
        def variable(self, varName):
            return Formula([str(varName[0]), None, None])
        def constant(self, arg):
            if str(arg[0]) == "true":
                connector = "|"
            elif str(arg[0]) == "false":
                connector = "&"
            return Formula([connector, Formula(["x0", None, None]), Formula(["!", Formula(["x0", None, None] ), None])])
                
        def binary_operator(self, args):
            return str(args[0])
        def unary_operator(self, args):
            return str(args[0])


    
        
        