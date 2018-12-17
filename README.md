# README
This is a solver for Linear Integer Arithmetic.

## Installation
Before executing this program, Python package [pysmt](https://github.com/pysmt/pysmt) must be installed.

To install pysmt, execute the following command:

        pip install pysmt
        
To make pysmt work, at least one solver must be installed. To show available solver, execute the following command.

        pysmt-install --check
        
Then, choose a solver and install it.(e.g., Install [Z3](https://github.com/Z3Prover/z3))

        pysmt-install --z3
        
After installation, you can verify the pysmt works by executing the code in [here](https://github.com/pysmt/pysmt/blob/master/examples/basic.py).

## Usage
To execute this program, type 

        python ct_new.py
        
This will read a SMTLIB file, generate a new LIA question and a series of transform equations, and write it to a new file. (As a test, I specify the input file as "test4.smt2" in directory benchmark. The output file is benchmark/new_test4.smt2, If you need to test other files, please alter the first line of the function test). 
The new question can be solved by algorithm [Cube Test](https://www.mpi-inf.mpg.de/departments/automation-of-logic/software/spass-workbench/spass-iq/). Finally, we can generate the solution of the original question according to the transform equations. (By now, the last step is still unfinished)

## Example
        python ct_new.py

Input file:

        (set-logic QF_LIA)
        (set-info :smt-lib-version 2.0)
        (set-info :status sat)
        (declare-fun x () Int)
        (declare-fun y () Int)
        (declare-fun z () Int)
        (assert
        (and (<= (+ (* 5 x) (* 6 y)) 20)
        (<= (+ (* 3 y) (* 2 x) (* 5 z)) 15)
        (<= (* (- 1) z) 0)
        (<= (+ (* (- 2) x) (* (- 3) y)) (* (- 1) 15))
        )
        )
        (check-sat)
        (exit)
        
Output file:

        (set-logic QF_LIA)
        (set-info :smt-lib-version |2.0|)
        (set-info :status sat)
        (declare-fun x () Int)
        (declare-fun y () Int)
        (declare-fun z () Int)
        (declare-fun new_variable0 () Int)
        (assert (let ((.def_0 (* new_variable0 (- 2)))) (let ((.def_1 (+ .def_0 15))) (let ((.def_2 (* .def_1 6))) (let ((.def_3 (* new_variable0 3))) (let ((.def_4 (+ .def_3 (- 15)))) (let ((.def_5 (* .def_4 5))) (let ((.def_6 (+ .def_5 .def_2))) (let ((.def_7 (<= .def_6 20))) .def_7)))))))))
        (check-sat)
        (exit)
        
Transform equations:

        x = (new_variable0 * 3) + -15
        y = (new_variable0 * -2) + 15
        z = 0

## Supplement information
### cannot use pysmt to solve question.
After executing `pysmt-install --check`, if you get a list like this:

        Installed Solvers:
        msat      False (None)              Not in Python's path!
        cvc4      False (None)              Not in Python's path!
        z3        True (4.6.0)              Not in Python's path!
        yices     False (None)              Not in Python's path!
        btor      False (None)              Not in Python's path!
        picosat   False (None)              Not in Python's path!
        bdd       False (None)              Not in Python's path!
        
It means that python does not know where your solver is installed, try to execute this:

        source <(pysmt-install --env)
        
### Python version
As far as I know, pysmt can only be used in python2.7. Although pysmt can be installed in python3.5, I still cannot import it to python.

### Output file
The output file's format seems a little strange at first, cause pysmt try to output `let` command as much as possible when writing an LIA problem into a file. Actually, It is just another syntax.

