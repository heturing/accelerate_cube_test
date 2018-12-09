from pysmt.smtlib.parser import SmtLibParser
from six.moves import cStringIO
from pysmt.fnode import FNodeContent, FNode
from pysmt.shortcuts import And, is_sat, get_model, get_unsat_core
from pysmt.rewritings import conjunctive_partition
import numpy as np

# This a used to show the result of a Formula.
def pre_traversal(tree):
    if tree != None:
        print tree.root
        pre_traversal(tree.leftchild)
        pre_traversal(tree.rightchild)

# Defined by operator.py
symbol_dict = {13: "+", 14: "-", 15: "*", 16: "<=", 17: "<", 18: "="}

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




# Overall idea:
# for a given LIA question
# 1. Find all exclipit equations in the input.
# 2. Find all implicit euqations among the left formulas.(Put into solver)
# 3. Operate Smith Normal Form Convertion and get a list of equations.
# 4. Substitute according to the result of 3 and get a new question.
# 5. Output this question in smtlib.
#
# Details:
# 1. script.get_last_formula() returns a formula which is the target of the input question
# 2. target_formula.get_atoms() splits the target formula if it contains & or | and returns a tuple of formulas.
# 3. we then construct a tree structure for each formula.
# 4. by judging whether a equation or not, we fill eqautions and inequations lists.

def is_equation(Formula):
    if Formula.node_type() == 18:
        return True
    else:
        return False

def less_than_to_less(Formula):
    NewContent = FNodeContent(17, Formula.args(), None)
    NewFormula = FNode(NewContent, -1)
    return NewFormula

def inequation_to_equation(Formula):
    NewContent = FNodeContent(18, Formula.args(), None)
    NewFormula = FNode(NewContent, -1)
    return NewFormula

def equation_to_inequation(Formula):
    NewContent = FNodeContent(16, Formula.args(), None)
    NewFormula = FNode(NewContent, -1)
    return NewFormula

def analyse_unsat(Formulas):
    conj = conjunctive_partition(Formulas)
    ucore = get_unsat_core(conj)
    print("Unsat core:")
    for f in ucore:
        print(f.serialize())
    return ucore

def have_non_zero(L):
    for index, l in enumerate(L):
        if l != 0:
            return index
    return -1

def print0(a,b):
    print("Equations:")
    test_print(a)
    print('*'*50)
    print("Inequations:")
    test_print(b)

def find_same_formula(L, f):
    for l in L:
        if l.args() == f.args() and l.node_type() == 16:
            return l

def is_int_mul_val(term):
    if term.is_symbol() == False and term. is_constant() == False:
        t0, t1 = term.args()
        if t1.is_constant() == True and t0.is_symbol() == True:
            return (True,[t1],[t0])
    return (False,[],[])

# Find all variables in a formula, return them as a list (unsorted).
# Input formula need to be simplify()
def find_variables_and_coefficient_in_formula(formula):
    result = []
    if formula.is_symbol():
        result.extend([formula])
        return result
    elif formula.is_constant():
        return result
    else:
        for x in list(formula.args()):
            temp = find_variables_and_coefficient_in_formula(x)
            result.extend(temp)
    return result
        
def sort_variable_list(L):
    return L.sort(key = lambda x : x.node_id())

def find_all_variables(formulas):
    result = set()
    for f in formulas:
        result |= (set(find_variables_and_coefficient_in_formula(f)))
    temp = sort_variable_list(list(result))
    return result

# assume input term has been simplified and has the form (var, sym, int)
def find_coefficient_in_term(term, variable):
    args = term.args()
    if args[0] == variable:
        return [args[1]]
    return [0]
    

# get the term of the form (int sym var) by compare the size.
def extract_coefficient_according_to_variable_in_formula(formula, variable):
    result = []
    left = formula.args()[0]
    if left.size() > 3:
        candidates = left.args()
    else:
        candidates = [left]
    for c in candidates:
        result.extend(find_coefficient_in_term(c,variable))
    index =  have_non_zero(result)
    if index != -1:
        result = [result[index]]
    else:
        result = [0]
    return result

# return a list of coefficient according to variable list.
def extract_coefficient_in_formula(formula, variable_list):
    result = []
    for v in variable_list:
        result.extend(extract_coefficient_according_to_variable_in_formula(formula, v))
    return result

# return a matrix which contains the coefficients of the formulas.
def extract_coefficient_in_formulas(formulas, variable_list):
    temp = []
    for f in formulas:
        temp.append(extract_coefficient_in_formula(f, variable_list))
    return np.array(temp)
    
    

def test():
    f = open("./benchmark/test4.smt2")
    Str = f.read()
    parser = SmtLibParser()
    script = parser.get_script(cStringIO(Str))
    target_formula = script.get_last_formula()
    formulas_arith = list(target_formula.get_atoms())

    equations = []
    inequations = []

    # split formulas into equations and inequations.
    for x in formulas_arith:
       if is_equation(x):
           equations.append(x.simplify())
       else:
           inequations.append(x.simplify())
    print0(equations, inequations)
   

# find all let sentences (it seems that all the lets have been substituted by original terms)
#    lets = script.filter_by_command_name("let")
#    if len(lets) == 0:
#        print("no lets")
#    else:
#        print("lets")
#    for l in lets:
#        print(l)


    #From now on, start step 2.
    #Construct a new question according to left inequations.
    new_question = reduce(And, inequations)
    if not is_sat(new_question):
        print("Unsat")
        analyse_unsat(new_question)
        return False
    else:
        #turn all <= into <
        new_formulas = []
        for x in inequations:
            new_formulas.append(less_than_to_less(x))
        print("*"*25,"new_formulas","*"*25)
        print(new_formulas)

    #Construct a new question according to left inequations(new).
    new_questionLQ = reduce(And, new_formulas)
    if is_sat(new_questionLQ):
        #call spass and return
        pass
    else:
        unsat_core = analyse_unsat(new_questionLQ)
        for x in unsat_core:
            equations.append(inequation_to_equation(x).simplify())
            inequations.remove(find_same_formula(inequations, x))
    print0(equations, inequations)

    #From now on, start step 3
    if equations != []:
        pass

    

def test_print(L):
    for l in L:
        print(l)


if __name__ == "__main__":
    test()
