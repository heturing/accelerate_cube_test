# This a used to show the result of a Formula.
def pre_traversal(tree):
    if tree != None:
        print tree.root
        pre_traversal(tree.leftchild)
        pre_traversal(tree.rightchild)


class BinaryTree(object):
    def __init__(self, root_value):
        self.root = root_value
        self.leftchild = None
        self.rightchild = None
    
    def __str__(self):
        return symbol_dict[self.root]
    
    def insert_left(self, left_value):
        if self.leftchild == None:
            self.leftchild = BinaryTree(left_value)
        else:
            left_subtree = BinaryTree(left_value)
            left_subtree.leftchild = self.leftchild
            self.leftchild = left_subtree

def insert_right(self, right_value):
    if self.rightchild == None:
        self.rightchild = BinaryTree(right_value)
        else:
            right_subtree = BinaryTree(right_value)
            right_subtree.rightchild = self.rightchild
            self.rightchild = right_subtree
                
                def set_root(self, root_value):
                    self.root = root_value

def get_root(self):
    return self.root
    
    def get_leftchild(self):
        return self.leftchild
    
    def get_rightchild(self):
        return self.rightchild

# This class is used to store a formula (e.g. a + b + c <= d) as a binary tree,
# and the tree is constructed recursively.
class Formula(BinaryTree):
    def __init__(self, formula):
        L = self.split_left_and_right(formula)
        self.root = BinaryTree(L[2])
        self.symbol = L[2]
        
        if L[1].is_constant() or L[1].is_symbol():
            self.rightchild = BinaryTree(L[1])
        else:
            self.rightchild = Formula(L[1])
        
        if L[0].is_constant() or L[0].is_symbol():
            self.leftchild = BinaryTree(L[0])
        else:
            self.leftchild = Formula(L[0])

def __str__(self):
    return self.root
    
    def __repr__(self):
        return self.root
    
    
    # This function is to split a formula of form a + b = c into a list [a+b, c, =],
    # if input a formula a + b + c, we split it into [a, b+c, +].
    # 1. formula_type is a number which can be translated into symbol through a dictionary.
    def split_left_and_right(self,formula):
        L = list(formula.args())
        formula_type = formula.node_type()
        if len(L) == 2:
            L.append(formula_type)
        else:
            length = len(L)
            c = FNodeContent(formula_type, tuple(L[1:]), None)
            newNode = FNode(c,-1)
            L = L[:1]
            L.append(newNode)
            L.append(formula_type)
        return L
    
    def split_formulas(self,formulas):
        return formulas.get_atoms()
    
    # This function should evaluate a formula with a dictionary of the form {(fnode, value)}
    def evaluate(self, value_dict):
        pass
    
    # To collect all the equations, we need to judge whether a given formula is an equation.
    def is_equation(self):
        if self.symbol == 18:
            return True
        else:
            return False


