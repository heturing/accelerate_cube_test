import pysmt.smtlib.commands as smtcmd
from pysmt.smtlib.parser import SmtLibParser
from six.moves import cStringIO
from ct_new import MODE
from pysmt.fnode import FNodeContent, FNode
from pysmt.rewritings import conjunctive_partition
from pysmt.shortcuts import get_unsat_core
from pysmt.operators import SYMBOL
from pysmt.typing import INT
from pysmt.smtlib.script import SmtLibScript, SmtLibCommand
from pysmt.shortcuts import And

# Defined by pysmt.operator.py
symbol_dict = {11:"INT_CONSTANT", 13: "+", 14: "-", 15: "*", 16: "<=", 17: "<", 18: "="}

# Test whether the input formula is an equation.
def is_equation(Formula):
    if Formula.node_type() == 18:
        return True
    else:
        return False

# Extract target formula from the file, and split the formula if it is consistuted by other primitive formula. This function takes a file path as parameter and returns a list of formula.
def read_formula(file_path):
    f = open(file_path)
    Str = f.read()
    parser = SmtLibParser()
    script = parser.get_script(cStringIO(Str))
    target_formula = script.get_last_formula()
    return list(target_formula.get_atoms())

# Take a list of formulas and split them into equations and inequations.
def split_formulas(L):
    equations = []
    inequations = []
    for x in L:
        if is_equation(x):
            equations.append(x.simplify())
        else:
            inequations.append(x.simplify())
    return (equations, inequations)

# This function analyse why a series of formula are unsatisfiable, executing this will return a list of formulas.(i.e., unsat core)
def analyse_unsat(Formulas):
    conj = conjunctive_partition(Formulas)
    ucore = get_unsat_core(conj)
    if MODE == 1:
        print("Unsat core:")
        for f in ucore:
            print(f.serialize())
    return ucore

# Turns a less-than inequation into less inequation.
def less_than_to_less(Formula):
    NewContent = FNodeContent(17, Formula.args(), None)
    NewFormula = FNode(NewContent, -1)
    return NewFormula

# Convert an ineuqation to euqation.
def inequation_to_equation(Formula):
    NewContent = FNodeContent(18, Formula.args(), None)
    NewFormula = FNode(NewContent, -1)
    return NewFormula

# Convert an equation to inequation.
def equation_to_inequation(Formula):
    NewContent = FNodeContent(16, Formula.args(), None)
    NewFormula = FNode(NewContent, -1)
    return NewFormula

# Give a list of formula L and a target formula f, return the first formula in list found to be same with f.
def find_same_formula(L, f):
    for l in L:
        if l.args() == f.args() and l.node_type() == 16:
            return l

# Create a new variable
def create_new_variable(variable_index):
    variable_name = "new_variable" + str(variable_index)
    content = FNodeContent(SYMBOL,(),(variable_name, INT))
    node = FNode(content, 10000+variable_index)
    return node

# Create a fnode for an integer.
def create_new_fnode_for_num(num):
    content = FNodeContent(11,(),long(num))
    node = FNode(content, 100000+num)
    return node

def generate_new_script(file_path, new_inequations,new_variables_list):
    f = open(file_path)
    Str = f.read()
    new_parser = SmtLibParser()
    script = new_parser.get_script(cStringIO(Str))
    new_script = new_parser.get_script(cStringIO(Str))
    new_assert_command = SmtLibCommand(smtcmd.ASSERT, [And(new_inequations)])
    last_declare_fun = 0

    # For each formula in list inequations, create a new command and insert it to the new script./
    for index,cmd in enumerate(script.commands):
        if cmd.name == smtcmd.ASSERT:
            new_script.commands[index] = new_assert_command
            if cmd.name == smtcmd.DECLARE_FUN:
                last_declare_fun = index

    for i in range(0, len(new_variables_list)):
        temp_new_declare_command = SmtLibCommand(smtcmd.DECLARE_FUN, [new_variables_list[i]])
        new_script.commands.insert(last_declare_fun + i + 1, temp_new_declare_command)
    if MODE == 1:
        print("new script's content is:")
        print(new_script.commands)

    split_file_path = file_path.split("/")
    file_name = split_file_path[-1]
    new_file_name = "new.".join(file_name.split("."))
    split_file_path[-1] = new_file_name
    new_file_path = "/".join(split_file_path)
    print("Writing to file %s ..." % (new_file_path))
    new_script.to_file(new_file_path)
