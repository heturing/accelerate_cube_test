import numpy as np
import copy
import fractions

class Matrix(object):
    def __init__(self, row, column):
        self.matrix = np.zeros([row, column])
        self.row_num = row
        self.column_num = column
        self.U = np.eye(row)
        self.V = np.eye(column)

    def __init__(self, matrix):
        self.matrix = matrix
        self.column_num = len(matrix[0])
        self.row_num = len(matrix)
        self.U = np.eye(self.row_num)
        self.V = np.eye(self.column_num)

    def show_U(self):
        print("U is:")
        print(self.U)

    def show_V(self):
        print("V is:")
        print(self.V)

    def show_matrix(self):
        print("matrix is:")
        print(self.matrix)
        self.show_U()
        self.show_V()

    def update(self, row, col, value):
        self.matrix[row][col] = value

    # Variable temp need to be a deep copy, otherwise the value of temp will change with other variables. 
    def swap_row(self, row1, row2):
        temp = copy.deepcopy(self.matrix[row1])
        self.matrix[row1] = self.matrix[row2]
        self.matrix[row2] = temp
        print("swap row %s and row %s" % (row1, row2))
        self.show_matrix()

    def swap_column(self, col1, col2):
        temp = copy.deepcopy(self.matrix[:,col1])
        self.matrix[:,col1] = self.matrix[:,col2]
        self.matrix[:,col2] = temp
        print("swap column %s and column %s" % (col1, col2))
        self.show_matrix()

    def swap_U_row(self, row1, row2):
        temp = copy.deepcopy(self.U[row1])
        self.U[row1] = self.U[row2]
        self.U[row2] = temp
        print("swap row %s and row %s of matrix U" % (row1, row2))
        self.show_U()

    def swap_V_col(self, col1, col2):
        temp = copy.deepcopy(self.V[:,col1])
        self.V[:,col1] = self.V[:,col2]
        self.V[:,col2] = temp
        print("swap column %s and column %s of matrix V" % (col1, col2))
        self.show_V()    
        

    def add_row_to_row(self, row1, row2, times):
        temp = self.matrix[row1] * times
        self.matrix[row2] += temp

    def add_col_to_col(self, col1, col2, times):
        temp = self.matrix[:,col1] * times
        self.matrix[:,col2] += temp

    def sub_row_to_row(self, row1, row2, times):
        temp = self.matrix[row1] * times
        self.matrix[row2] -= temp

    def sub_col_to_col(self, col1, col2, times):
        temp = self.matrix[:,col1] * times
        self.matrix[:,col2] -= temp

    def sub_row_to_row_U(self, row1, row2, times):
        temp = self.U[row1] * times
        self.U[row2] -= temp

    def sub_col_to_col_V(self, col1, col2, times):
        temp = self.V[:,col1] * times
        self.V[:,col2] -= temp       

    def select_row_with_min_value(self, col):
        min_index = -1
        min_value = float('inf')
        for index, value in enumerate(abs(self.matrix[:,col])):
            if min_value > value and value != 0:
                min_index = index
                min_value = value

        return min_index

    def select_col_with_min_value(self, row):
        min_index = -1
        min_value = float('inf')
        for index, value in enumerate(abs(self.matrix[row])):
            if min_value > value and value != 0:
                min_index = index
                min_value = value
        return min_index

    # calculate how many times row1 should be add to row2.
    # Because division is different in python2.7 and python 3.7, this function may not work as expected in python3.
    # This function will return a negative number when data2 is negative.
    def calculate_row_add_times(self, row1, row2, target_col):
        data1 = self.matrix[row1][target_col]
        data2 = self.matrix[row2][target_col]
        times = data2 // data1
        return times

    def calculate_col_add_times(self, col1, col2, target_row):
        data1 = self.matrix[target_row][col1]
        data2 = self.matrix[target_row][col2]
        times = data2 // data1
        return times
        

    # check if this column has element 0. If there is no 0 element, return true.
    def check_zero_element(self, col):
        return 0 not in self.matrix[:,col]

    # check whether we have handled the column.(i.e. self.matrix[col][col] is non-zero and the rest is all zero.)
    def check_col_finish(self, col):
        for i in range(len(self.matrix[:,col])):
            if i != col and self.matrix[i][col] != 0:
                return False
        return True

    def check_row_finish(self, row):
        for i in range(len(self.matrix[row])):
            if i != row and self.matrix[row][i] != 0:
                return False
        return True

    def check_finish(self, index):
        return self.check_col_finish(index) and self.check_row_finish(index)

    # check whether the matrix is in smith normal form or not. If not, return "row" and a row ("col" and a column) number that violates the rule. Return -1 if no row (column violates)
    def is_in_diagonal(self):
        for i in range(self.row_num):
            if not self.check_col_finish(i):
                return "col",i
        for i in range(self.row_num):
            if not self.check_row_finish(i):
                return "row",i
        return ("already",-1)

    def is_good_efficient(self):
        if not self.is_in_diagonal():
            print(" the matrix is not in diagonal")
            return False
        else:
            for i in range(1, min(self.row_num, self.column_num)):
                if self.matrix[i][i] % self.matrix[i-1][i-1] != 0:
                    return False
            return True

    def turn_diagonal_into_positive(self):
        for i in range(min(self.row_num, self.column_num)):
            if self.matrix[i][i] != abs(self.matrix[i][i]):
                self.U[i] = -(self.U[i])
                self.matrix[i][i] = abs(self.matrix[i][i])

    def find_first_zero_in_diagonal(self):
        for i in range(min(self.row_num, self.column_num)):
            if self.matrix[i][i] == 0:
                return i
        return -1

    def find_last_non_zero_in_diagonal(self):
        for i in range(min(self.row_num, self.column_num)-1, -1, -1):
            if self.matrix[i][i] != 0:
                return i
        return -1
       
    def swap_zero_element(self):
        first_zero = self.find_first_zero_in_diagonal()
        last_non_zero = self.find_last_non_zero_in_diagonal()
        while first_zero < last_non_zero and first_zero != -1:
            self.matrix[first_zero][first_zero] = self.matrix[last_non_zero][last_non_zero]
            self.matrix[last_non_zero][last_non_zero] = 0
            self.swap_U_row(first_zero, last_non_zero)
            self.swap_V_col(first_zero, last_non_zero)
            first_zero = self.find_first_zero_in_diagonal()
            last_non_zero = self.find_last_non_zero_in_diagonal()
            
    # The purpose is to make all element in col_num 0 except the first element.
    # 1. First, choose a data with minimal abs value(not 0) and return its row number.
    # 2. Then, swap this line to the toppest.
    # 3. calculate how many times should be subtract to each line. 
    # 4. if there are still non-zore element, redo 1, else, return this matrix.
    def handle_col_once(self, col_num):
        min_row = self.select_row_with_min_value(col_num)
        print("select row %s, the content is %s." % (min_row, self.matrix[min_row]))
        self.swap_row(col_num ,min_row)
        self.swap_U_row(col_num, min_row)
        for i in range(self.row_num):
            if i != col_num:
                times = self.calculate_row_add_times(col_num, i, col_num)
                print("subtract %s times row %s to row %s" % (times, col_num, i))
                self.sub_row_to_row(col_num ,i, times)
                self.sub_row_to_row_U(col_num, i, times)
                self.show_matrix()

    def handle_col(self, col_num):
        while not self.check_col_finish(col_num):
            self.handle_col_once(col_num)

    def handle_row_once(self, row_num):
        min_col = self.select_col_with_min_value(row_num)
        print("select col %s, the content is %s." % (min_col, self.matrix[:,min_col]))
        self.swap_column(row_num, min_col)
        self.swap_V_col(row_num, min_col)
        for i in range(self.column_num):
            if i != row_num:
                times = self.calculate_col_add_times(row_num, i, row_num)
                print("subtract %s times column %s to column %s" % (times, row_num, i))
                self.sub_col_to_col(row_num, i, times)
                self.sub_col_to_col_V(row_num, i, times)
                self.show_matrix()

    def handle_row(self, row_num):
        while not self.check_row_finish(row_num):
            self.handle_row_once(row_num)

    def to_diagonal(self):
        print("Initial matrix is:")
        self.show_matrix()
        rc, index = self.is_in_diagonal()
        while index != -1:
            if rc == "row":
                while not self.check_finish(index):
                    self.handle_row(index)
                    self.handle_col(index)
            else:
                while not self.check_finish(index):
                    self.handle_col(index)
                    self.handle_row(index)
            rc, index = self.is_in_diagonal()

    # The left part is to make sure the element on diagonal do not violate rules.
    # This function adjusts elements matrix[index][index] and matrix[index+1][index+1] so that the last one can divide the previous one.
    def handle_diagonal_once(self, index):
        gcd = fractions.gcd(self.matrix[index][index], self.matrix[index+1][index+1])
        lcm = self.matrix[index][index] * self.matrix[index+1][index+1] // gcd
        self.matrix[index][index] = gcd
        self.matrix[index+1][index+1] = lcm
        
    def to_smith_normal_form(self):
        self.turn_diagonal_into_positive()
        self.swap_zero_element()
        if not self.is_good_efficient():
            for i in range(1,self.column_num):
                self.add_col_to_col(0,i)
                self.add_col_to_col_V(0,i)
                self.to_diagonal()
        #while not self.is_good_efficient():
        #    for i in range(min(self.row_num, self.column_num) - 1):
        #        self.handle_diagonal_once(i)

    def smithify(self):
        self.to_diagonal()
        self.to_smith_normal_form()
            
            
        
