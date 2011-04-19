#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2008 Martin Manns

# This file is NOT licensed under the GPL.

"""
Sparse matrix slicing benchmark
===============================

This benchmark compares three sparse matrix packages for their
effectiveness and efficiency in handling data.

The matrix packages are:
- scpy.sparse.lil_matrix
- scpy.sparse.dok_matrix
- scpy.sparse.csr_matrix
- pysparse.pysparseMatrix.PysparseMatrix
- cvxopt.spmatrix


The benchmark focuses on:
1. Fill of the sparse matrix with single elements
2. Fill of the sparse matrix with numpy.arrays
3. Retrieve single values by indexing
4. Retrieve value lists by slicing
5. Retrieve numpy.arrays by slicing.

Besides the speed of the operations, the memory consumption
is measured. Note that the top-command is used since the 
sparse libraries allocate their memory in C code.

"""
from timeit import Timer

import numpy

SPARSEMATRIX = "scpy.sparse.lil_matrix"
XDIM, YDIM = SHAPE = (10000000, 10000000)
TESTS = ["test_fill_single_element", "test_fill_array", \
         "test_get_single_value", "test_get_list_slice", \
         "test_get_array_slice"]
NO_ELEMENTS = 1000000

RANDINT = numpy.random.randint
RANDOM = numpy.random.random

numpy.random.seed()

def setup():
    """Set up the matrix and time it"""
    
    if SPARSEMATRIX == "scpy.sparse.lil_matrix":
        import scipy.sparse
        
        code = "scipy.sparse.lil_matrix(shape=SHAPE)"
        timer = Timer(code, \
                  "import scipy ;"
                  "from __main__ import SHAPE ;"
                  "gc.enable()")
        
    elif SPARSEMATRIX == "scpy.sparse.dok_matrix":
        import scipy.sparse
        
        code = "scipy.sparse.dok_matrix(A=SHAPE)"
        timer = Timer(code, \
                  "import scipy ;"
                  "from __main__ import SHAPE ;"
                  "gc.enable()")
                  
    elif SPARSEMATRIX == "scpy.sparse.csr_matrix":
        import scipy.sparse
        
        code = "scipy.sparse.csr_matrix(SHAPE, nzmax=1000000)"
        timer = Timer(code, \
                  "import scipy ;"
                  "from __main__ import SHAPE ;"
                  "gc.enable()")
        
    elif SPARSEMATRIX == "pysparse.pysparseMatrix.PysparseMatrix":
        import pysparse.pysparseMatrix
        
        code = "pysparse.pysparseMatrix.PysparseMatrix(" + \
               "nrow=SHAPE[0], ncol=SHAPE[1])"
        timer = Timer(code, \
                  "import pysparse ;"
                  "from __main__ import SHAPE ;"
                  "gc.enable()")
        
    elif SPARSEMATRIX == "cvxopt.spmatrix":
        import cvxopt
        
        code = "cvxopt.spmatrix(0, [], [], size=SHAPE)"
        timer = Timer(code, \
                  "import cvxopt ;"
                  "from __main__ import SHAPE ;"
                  "gc.enable()")
    else:
        raise ValueError, SPARSEMATRIX + "is unknown sparse matrix type"
    
    print timer.timeit(1)
    del timer
    
    global matrix
    matrix = eval(code)
    
    raw_input("Hit <ENTER>")

def test_fill_single_element():
    """Fill matrix with random single elements"""
    
    code = "matrix[RANDINT(0, XDIM), RANDINT(0, YDIM)] = RANDOM()"
    
    if SPARSEMATRIX == "scpy.sparse.lil_matrix":
        pass
        
    elif SPARSEMATRIX == "scpy.sparse.dok_matrix":
        pass
        
    elif SPARSEMATRIX == "scpy.sparse.csr_matrix":
        pass
        
    elif SPARSEMATRIX == "pysparse.pysparseMatrix.PysparseMatrix":
        pass
        
    elif SPARSEMATRIX == "cvxopt.spmatrix":
        pass
        
    else:
        raise ValueError, SPARSEMATRIX + "is unknown sparse matrix type"

    timer = Timer(code, \
              "from __main__ import matrix ;"
              "from __main__ import XDIM ;"
              "from __main__ import YDIM ;"
              "from __main__ import RANDINT ;"
              "from __main__ import RANDOM ;"
              "gc.enable()")
    print timer.timeit(number=NO_ELEMENTS)


def test_fill_array():
    """Fill of the sparse matrix with numpy.arrays"""
    
    max_dim_size = 100
    
    start_stop_x = RANDINT(0, XDIM - max_dim_size)
    start_stop_x = [start_stop_x, start_stop_x + max_dim_size]
    start_stop_y = RANDINT(0, YDIM - max_dim_size)
    start_stop_y = [start_stop_y, start_stop_y + max_dim_size]
    
    global slice_x
    global slice_y
    slice_x = slice(min(start_stop_x), max(start_stop_x))
    slice_y = slice(min(start_stop_y), max(start_stop_y))
    
    dim_x = max(start_stop_x) - min(start_stop_x)

    dim_y = max(start_stop_y) - min(start_stop_y)
    
    no_cells = dim_x * dim_y
    
    global content
    content = numpy.array(([RANDOM() for i in xrange(no_cells)]))
    content = content.reshape(dim_x, dim_y)
    
    code = "matrix[" + repr(slice_x) + ", " + repr(slice_y) + "] = content"
    
    if SPARSEMATRIX == "scpy.sparse.lil_matrix":
        pass
        
    elif SPARSEMATRIX == "scpy.sparse.dok_matrix":
        pass
        
    elif SPARSEMATRIX == "scpy.sparse.csr_matrix":
        pass
        
    elif SPARSEMATRIX == "pysparse.pysparseMatrix.PysparseMatrix":
        code = \
            "indices = numpy.nonzero(content);" + \
            "target_indices = (indices[0] + slice_x.start, " + \
            "                  indices[1] + slice_y.start);" + \
            "values = [content[x, y] for x, y in zip(*indices)];" + \
            "matrix.put(values, target_indices[0], target_indices[1])"
     
    elif SPARSEMATRIX == "cvxopt.spmatrix":
        pass
        
    else:
        raise ValueError, SPARSEMATRIX + "is unknown sparse matrix type"

    timer = Timer(code, \
              "from __main__ import matrix ;"
              "from __main__ import content ;"
              "from __main__ import slice_x ;"
              "from __main__ import slice_y ;"
              "from __main__ import XDIM ;"
              "from __main__ import YDIM ;"
              "from __main__ import RANDINT ;"
              "from __main__ import RANDOM ;"
              "from __main__ import numpy ;"
              "gc.enable()")
    print timer.timeit(100)

def test_get_single_value():
    """Retrieve single values by indexing"""
    
    code = "dummy = matrix[RANDINT(0, XDIM), RANDINT(0, YDIM)]"
    
    if SPARSEMATRIX == "scpy.sparse.lil_matrix":
        pass
        
    elif SPARSEMATRIX == "scpy.sparse.dok_matrix":
        pass
        
    elif SPARSEMATRIX == "scpy.sparse.csr_matrix":
        pass
        
    elif SPARSEMATRIX == "pysparse.pysparseMatrix.PysparseMatrix":
        pass
        
    elif SPARSEMATRIX == "cvxopt.spmatrix":
        pass
        
    else:
        raise ValueError, SPARSEMATRIX + "is unknown sparse matrix type"
    
    timer = Timer(code, \
              "from __main__ import matrix ;"
              "from __main__ import XDIM ;"
              "from __main__ import YDIM ;"
              "from __main__ import RANDINT ;"
              "gc.enable()")
    print timer.timeit(1000000)


def test_get_list_slice():
    """Retrieve value lists by slicing"""
    
    code = "dummy = matrix[slice(0, RANDINT(2, XDIM)), 100]"
    
    if SPARSEMATRIX == "scpy.sparse.lil_matrix":
        pass
        
    elif SPARSEMATRIX == "scpy.sparse.dok_matrix":
        pass
        
    elif SPARSEMATRIX == "scpy.sparse.csr_matrix":
        pass
        
    elif SPARSEMATRIX == "pysparse.pysparseMatrix.PysparseMatrix":
        code = "dummy = matrix[slice(0, RANDINT(2, XDIM)), slice(100, 101)]"
        
    elif SPARSEMATRIX == "cvxopt.spmatrix":
        pass
        
    else:
        raise ValueError, SPARSEMATRIX + "is unknown sparse matrix type"
    
    timer = Timer(code, \
              "from __main__ import matrix ;"
              "from __main__ import XDIM ;"
              "from __main__ import RANDINT ;"
              "gc.enable()")
    print timer.timeit(10)

def test_get_array_slice():
    """Retrieve numpy.arrays by slicing"""
    
    code = "dummy = matrix[slice(0, RANDINT(2, XDIM)), slice(0, RANDINT(2, YDIM))]"
    
    if SPARSEMATRIX == "scpy.sparse.lil_matrix":
        pass
        
    elif SPARSEMATRIX == "scpy.sparse.dok_matrix":
        code = "dummy = [numpy.array(matrix[slice(0, RANDINT(2, XDIM)), col]) for col in xrange(0, RANDINT(2, YDIM))]"
        
    elif SPARSEMATRIX == "scpy.sparse.csr_matrix":
        pass
        
    elif SPARSEMATRIX == "pysparse.pysparseMatrix.PysparseMatrix":
        pass
        
    elif SPARSEMATRIX == "cvxopt.spmatrix":
        pass
        
    else:
        raise ValueError, SPARSEMATRIX + "is unknown sparse matrix type"
    
    timer = Timer(code, \
              "from __main__ import matrix ;"
              "from __main__ import XDIM ;"
              "from __main__ import YDIM ;"
              "from __main__ import RANDINT ;"
              "from __main__ import numpy ;"
              "gc.enable()")
    print timer.timeit(10)
def main():
    """Main"""

    setup()
    for test in TESTS:
        print "Test: " + test
        eval(test)()
        raw_input("Hit <ENTER>")

if __name__ == '__main__':
    main()
