import smith_nf
import numpy as np
import formula_operation
from pysmt.fnode import FNodeContent, FNode

# Return true if there is no 0 element in list L
def have_non_zero(L):
    for index, l in enumerate(L):
        if l != 0:
            return index
    return -1

# This function will extract all the variables in a formula.
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

# sort a list of variable according to their node id.
def sort_variable_list(L):
    return L.sort(key = lambda x : x.node_id())

# This function will return a ordered list of variables in the input formulas.
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

# convert a fnode which content is a constant number to a integer.
def fnode_to_int(F):
    if F.is_constant():
        return float(F.serialize())

# Extract all the right side value of some formulas.
def extract_right_side_of_formulas(formulas):
    result = []
    for f in formulas:
        result.append(fnode_to_int(f.args()[1]))
    return np.array([np.array(result)]).T

# Apply multiply between an integer and a fnode.
def mul_num_and_fnode(num, node):
    node0 = formula_operation.create_new_fnode_for_num(num)
    content = FNodeContent(15, (node0, node), None)
    result = FNode(content, 200000+num)
    return result

# assume that the length of nums and nodes is same.
# apply multiply between a number and a fnode whose content is a constant number.
def mul_nums_and_fnodes(nums, nodes):
    temp = []
    for index, n in enumerate(nums):
        temp.append(mul_num_and_fnode(n,nodes[index]))
    content = FNodeContent(13, tuple(temp), None)
    result = FNode(content, 300000+nums[0])
    return result

# Find all variables in a formula, return them as a list (unsorted).
# Input formula need to be simplify()
def get_smith_normal_matrix_from_equations(equations, MODE):
    # Firstly, we need to simplify all the equations to get the uniform representation of the equation.
    if equations != []:
        for e in equations:
            e.simplify()
        variable_list = list(find_all_variables(equations))
        equations_coefficient = extract_coefficient_in_formulas(equations, variable_list)
        if MODE == 1:
            print("variable list is:\n %s" % (variable_list))
            print("coefficient matrix is:\n%s" % (equations_coefficient))

        # Start smithify.
        coefficient_matrix = smith_nf.Matrix(equations_coefficient)
        # right_matrix holds all the values on the right side of the equations.
        right_matrix = extract_right_side_of_formulas(equations)
        # Apply smith normal transform.
        coefficient_matrix.smithify()
        # Calculate U * right_matrix
        U_mul_right = np.dot(coefficient_matrix.U, right_matrix)
        # If the rank of the smithify matrix is n, then we just want first n elements of the u_mul_tight. So we need to trancate the U*right in that case.
        trancate_index = np.linalg.matrix_rank(coefficient_matrix.matrix)
        U_mul_right_m = U_mul_right[:][:trancate_index]
        # By now, we have achieved the smithified matrix, and we should generate tranform equations from it.
        # Create some new variables.
        variable_num = len(variable_list)
        new_variables_list = []
        for i in range(len(coefficient_matrix.V[0]) - trancate_index):
            new_variables_list.append(formula_operation.create_new_variable(i))
        # Generate transform equations
        transform_equations_dict = {}
        for i in range(len(coefficient_matrix.V)):
                temp0 = np.dot(coefficient_matrix.V[i][:trancate_index], U_mul_right_m)
                temp0_node = formula_operation.create_new_fnode_for_num(temp0)
                nums_list = coefficient_matrix.V[i][trancate_index:]
                temp1 = mul_nums_and_fnodes(nums_list, new_variables_list)
                content = FNodeContent(13, (temp0_node, temp1), None)
                temp2 = FNode(content, 400000+i)
                transform_equations_dict[variable_list[i]] = temp2.simplify()


        # Print intermediate information
        if MODE == 1:
            print("smith normal form is:\n%s" % (coefficient_matrix.matrix))
            print("matrix U is\n%s" % (coefficient_matrix.U))
            print("matrix V is\n%s" % (coefficient_matrix.V))
            print("right side is:\n%s" % (right_matrix))
            print("U * right =\n%s" % (U_mul_right))
            print("After truncation, U * right = \n%s" % (U_mul_right_m))
            print("the transform dictionary is:\n%s" % (transform_equations_dict))
            print(transform_equations_dict[variable_list[0]])
            print("new variables list is:")
            print(new_variables_list)

        return (transform_equations_dict, new_variables_list)
    else:
        # return an empty dictionary if failed to apply smith normal transform
        return ({}, new_variables_list)
