#!/usr/bin/env python
# -*- coding: utf-8 -*-

import _sparsearray2

class Testobj_lil_matrix(object):
    def setup_method(self, method):
        self.testarray = _sparsearray.obj_lil_matrix(shape=(100, 100), dtype = "O")
        
    def test_init(self):
        _sparsearray.obj_lil_matrix(A=[1,2,3])
    
    def test_getitem(self):
        assert self.testarray[0, 0] is None
        assert _sparsearray.obj_lil_matrix(A=[1,2,3])[0, 0] == 1
    
    def test_setitem(self):
        testarray = self.testarray
        testarray[1, 1] = 1
        assert testarray.objectpool == [None, 1]
        assert testarray[1, 1] == 1
        
        testarray[1, 1] = "e"
        assert testarray[1, 1] == "e"
        
        testarray[3, 3] = "Test"
        assert testarray[3, 3] == "Test"
        
        testarray = _sparsearray.obj_lil_matrix(shape=(1000, 10000000), dtype = "O")
        testarray[500, 800] = "e"
        assert testarray[500, 800] == "e"
        
        testarray[500, 800000] = "e"
        assert testarray[500, 800000] == "e"
        
        testarray[10, :100] = range(100)
        assert testarray[10, 0] == 0
        #assert testarray[10, 0:100] == range(10)
