import numpy as np
import smith_nf
import os
import sys
import getopt
import formula_operation
import calculation
from pysmt.smtlib.parser import SmtLibParser
from six.moves import cStringIO
from pysmt.shortcuts import And, is_sat, get_model


# Defined by operator.py
symbol_dict = {11:"INT_CONSTANT", 13: "+", 14: "-", 15: "*", 16: "<=", 17: "<", 18: "="}

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

def less_than_to_less(Formula):
    NewContent = FNodeContent(17, Formula.args(), None)
    NewFormula = FNode(NewContent, -1)
    return NewFormula


def print_equations_and_inequations(a,b):
    print("Equations:")
    for l in a:
        print l
    print('*'*50)
    print("Inequations:")
    for l in b:
        print l




def is_int_mul_val(term):
    if term.is_symbol() == False and term. is_constant() == False:
        t0, t1 = term.args()
        if t1.is_constant() == True and t0.is_symbol() == True:
            return (True,[t1],[t0])
    return (False,[],[])

# input python ct_new.py -i/--infile to specify a file that contains input question. If this parameter is absent, try to solve all the smt2 file in current directory.
# The main function is the entry of this program, and it should be start with the parameter sys.argv[1:].
# Information about parameter.
# -i/--infile : input file

# Mode can be 0 or 1. 0 stands for expriment mode adn 1 stands for debug mode. In debug mode, all the intermediate step will be printed.
MODE = 1

def main(argv):
    input_file = ''
    try:
        opts,args = getopt.getopt(sys.argv[1:], "i:",["infile="])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--infile"):
            input_file = arg
    print 'Input file is ', input_file


# After getting the input file, we need to extract the file to make a question list.
    question_list = []
    with open(input_file) as myFile:
        for line in myFile:
            question_list.append(line[:-1])
    if MODE == 1:
        print "{0} questions need to be solved, and they are {1}".format(len(question_list), question_list)

# All the question are now in question_list, and we need to calculate them one by one.
    for q in question_list:
        solve_question(q,MODE)


# Solve the question in file_path. MODE is used to specify the detail extent of output content.
def solve_question(file_path, MODE):
    print "solving question in file", file_path, "..."
    
# Extract target formulas from the file.
    formulas_arith = formula_operation.read_formula(file_path)
    if MODE == 1:
        print("The question is: " + str(formulas_arith))

# Split the formulas into equations and inequations
    equations = []
    inequations = []
    equation, inequations = formula_operation.split_formulas(formulas_arith)
    if MODE == 1:
        print_equations_and_inequations(equations, inequations)
   

# find all let sentences (it seems that all the lets have been substituted by original terms)
#    lets = script.filter_by_command_name("let")
#    if len(lets) == 0:
#        print("no lets")
#    else:
#        print("lets")
#    for l in lets:
#        print(l)


    #From now on, start step 2. In step 2, we want to find all the implicit equations.
    #Construct a new question according to left inequations.
    new_question = reduce(And, inequations)
    if not is_sat(new_question):
        print("Unsat")
        formula_operation.analyse_unsat(new_question)
        return False
    else:
        # Then, we turn all the <= into < and test the satisfiability again.
        new_formulas = []
        for x in inequations:
            new_formulas.append(formula_operation.less_than_to_less(x))
        if MODE ==1:
            print("*"*25,"new_formulas","*"*25)
            print(new_formulas)

    #Construct a new question according to left inequations(new).
    new_questionLQ = reduce(And, new_formulas)
    # if the new question is still sat, the original question contains no implicit equations.
    if is_sat(new_questionLQ):
        #call spass and return
        #because spass cannot work on mac, we use z3 to test to validaty of this program.
        os.system("z3 " + file_path)
        return
    # Else,there are implicit equations in original question. We need to move these "equations" from list inequations to list equations.
    else:
        unsat_core = formula_operation.analyse_unsat(new_questionLQ)
        for x in unsat_core:
            equations.append(formula_operation.inequation_to_equation(x).simplify())
            inequations.remove(formula_operation.find_same_formula(inequations, x))
        if MODE == 1:
            print_equations_and_inequations(equations, inequations)

    # By now, we should have collect all the equations (explicit and implicit) into the list. Then, we should compute the smith normal form for the coefficient of equations.
    dict_and_list = calculation.get_smith_normal_matrix_from_equations(equations, MODE)
    print("dict and list", dict_and_list)
    transform_equations_dict = dict_and_list[0]
    new_variables_list = dict_and_list[1]
    if transform_equations_dict == {}:
        return False

    #From now on ,start step 4.
    new_inequations = []
    for f in inequations:
        new_inequations.append(f.substitute(transform_equations_dict).simplify())
        if MODE == 1:
            print("new inequations is:\n%s" % (new_inequations))

    #From now on, start step 5.
    #Transform equations are stored in a dictionary called transform_equations_dict, and applying this transform, we turn inequations into new_inequations.
    #In step 6, we need to construct a new script variable for this question, and return the transform dictionary and the new question.
    #Also, we need to declare the new variable in script

    formula_operation.generate_new_script(file_path, new_inequations, new_variables_list)

if __name__ == "__main__":
    main(sys.argv[1:])
