import glob
import os

# Find all .smt2 files in path.
def find_all_smt2_file(path):
    str = path + "*.smt2"
    res = glob.glob(str)
    return res

def help():
    print """usage: python ct_new.py [option]
ct_new.py is a tool for solving LIA.
    Options:

        -i / --infile    specify the file wihich contains the question list.
        -h / --help      show this message.
"""
    
    
