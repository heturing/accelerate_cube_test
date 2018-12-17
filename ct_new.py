from pysmt.smtlib.parser import SmtLibParser
from six.moves import cStringIO
from pysmt.fnode import FNodeContent, FNode
from pysmt.shortcuts import And, is_sat, get_model, get_unsat_core
from pysmt.rewritings import conjunctive_partition
from pysmt.operators import SYMBOL
from pysmt.typing import INT
from pysmt.smtlib.script import SmtLibScript, SmtLibCommand
from pysmt.shortcuts import And
import pysmt.smtlib.commands as smtcmd
import numpy as np
import smith_nf

# This a used to show the result of a Formula.
def pre_traversal(tree):
    if tree != None:
        print tree.root
        pre_traversal(tree.leftchild)
        pre_traversal(tree.rightchild)

# Defined by operator.py
symbol_dict = {11:"INT_CONSTANT", 13: "+", 14: "-", 15: "*", 16: "<=", 17: "<", 18: "="}

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
# 4. Substitute variables according to the result of 3 and get a new question.
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

def fnode_to_int(F):
    if F.is_constant():
        return float(F.serialize())

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
# if the return value is not 0, the return type should be Fnode, and it cannot be used to abs().
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
        result = [fnode_to_int(result[index])]
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

def extract_right_side_of_formulas(formulas):
    result = []
    for f in formulas:
        result.append(fnode_to_int(f.args()[1]))
    return np.array([np.array(result)]).T
    
def create_new_variable(variable_index):
    variable_name = "new_variable" + str(variable_index)
    content = FNodeContent(SYMBOL,(),(variable_name, INT))
    node = FNode(content, 10000+variable_index)
    return node

def create_new_fnode_for_num(num):
    content = FNodeContent(11,(),long(num))
    node = FNode(content, 100000+num)
    return node

    
def mul_num_and_fnode(num, node):
    node0 = create_new_fnode_for_num(num)
    content = FNodeContent(15, (node0, node), None)
    result = FNode(content, 200000+num)
    return result

# assume that the length of nums and nodes is same.
def mul_nums_and_fnodes(nums, nodes):
    temp = []
    for index, n in enumerate(nums):
        temp.append(mul_num_and_fnode(n,nodes[index]))
    content = FNodeContent(13, tuple(temp), None)
    result = FNode(content, 300000+nums[0])
    return result
    

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
        for e in equations:
            e.simplify()
        variable_list = list(find_all_variables(equations))
        equations_coefficient = extract_coefficient_in_formulas(equations, variable_list)
        print("variable list is:\n %s" % (variable_list))
        print("coefficient matrix is:\n%s" % (equations_coefficient))

        # start smithify.
        coefficient_matrix = smith_nf.Matrix(equations_coefficient)
        right_matrix = extract_right_side_of_formulas(equations)
        print(type(coefficient_matrix.matrix[:][0]))
        coefficient_matrix.smithify()

        print("smith normal form is:\n%s" % (coefficient_matrix.matrix))
        print("matrix U is\n%s" % (coefficient_matrix.U))
        print("matrix V is\n%s" % (coefficient_matrix.V))
        print("right side is:\n%s" % (right_matrix))
        
        U_mul_right = np.dot(coefficient_matrix.U, right_matrix)
        print("U * right =\n%s" % (U_mul_right))

        # if the rank of the smithify matrix is n, then we just want first n elements of the u_mul_tight.
        trancate_index = np.linalg.matrix_rank(coefficient_matrix.matrix)
        U_mul_right_m = U_mul_right[:][:trancate_index]
        print("After truncation, U * right = \n%s" % (U_mul_right_m))

        variable_num = len(variable_list)
        new_variables_list = []
        for i in range(len(coefficient_matrix.V[0]) - trancate_index):
            new_variables_list.append(create_new_variable(i))

        transform_equations_dict = {}
        for i in range(len(coefficient_matrix.V)):
            temp0 = np.dot(coefficient_matrix.V[i][:trancate_index], U_mul_right_m)
            temp0_node = create_new_fnode_for_num(temp0)
            nums_list = coefficient_matrix.V[i][trancate_index:]
            temp1 = mul_nums_and_fnodes(nums_list, new_variables_list)
            #print("temp1 is:   %s" % (temp1))
            content = FNodeContent(13, (temp0_node, temp1), None)
            temp2 = FNode(content, 400000+i)
            #print("temp2 is:   %s" % (temp2.simplify()))
            transform_equations_dict[variable_list[i]] = temp2.simplify()

        print("the transform dictionary is:\n%s" % (transform_equations_dict))
        print(transform_equations_dict[variable_list[0]])
        print("new variables list is:")
        print(new_variables_list)
        #return transform_equations_dict 
        #print(transform_equations_dict[variable_list[0].serialize()])
        
                
    else:
        # if there is no equation, solve the question by spass
        pass

    #From now on ,start step 4.
    new_inequations = []
    for f in inequations:
        new_inequations.append(f.substitute(transform_equations_dict).simplify())
    print("new inequations is:\n%s" % (new_inequations))

    #print(new_inequations[0].args()[0])

    #From now on, start step 5.
    #Transform equations are stored in a dictionary called transform_equations_dict, and applying this transform, we turn inequations into new_inequations.
    #In step 6, we need to construct a new script variable for this question, and return the transform dictionary and the new question.
    #Also, we need to declare the new variable in script

    new_parser = SmtLibParser()
    new_script = new_parser.get_script(cStringIO(Str))
    new_assert_command = SmtLibCommand(smtcmd.ASSERT, [And(new_inequations)])
    #print("new command is:")
    #print(type(new_command.args))
    for index,cmd in enumerate(script.commands):
        if cmd.name == smtcmd.ASSERT:
            new_script.commands[index] = new_assert_command
        if cmd.name == smtcmd.DECLARE_FUN:
            last_declare_fun = index

    for i in range(0, len(new_variables_list)):
        temp_new_declare_command = SmtLibCommand(smtcmd.DECLARE_FUN, [new_variables_list[i]])
        new_script.commands.insert(last_declare_fun + i + 1, temp_new_declare_command)

    print("new script's content is:")
    print(new_script.commands)

    new_script.to_file("./benchmark/new_test4.smt2")
    


    

def test_print(L):
    for l in L:
        print(l)


if __name__ == "__main__":
    test()
