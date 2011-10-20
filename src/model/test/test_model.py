#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit test for model.py"""

# --------------------------------------------------------------------
# pyspread is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyspread is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

import py.test as pytest
from sys import path, modules
path.insert(0, "..") 
path.insert(0, "../..") 

import gmpy

import numpy

import wx

from model.model import KeyValueStore, CellAttributes, DictGrid
from model.model import DataArray, CodeArray

from lib.selection import Selection

import lib.vartypes as v

class TestKeyValueStore(object):
    """Unit test for KeyValueStore"""
    
    def setup_method(self, method):
        """Creates empty KeyValueStore"""
        
        self.k_v_store = KeyValueStore()
        
    def test_missing(self):
        """Test if missing value returns None"""
        
        assert self.k_v_store[(1,2,3)] is None
        
        self.k_v_store[(1,2,3)] = 7
        
        assert self.k_v_store[(1,2,3)] == 7

class TestCellAttributes(object):
    """Unit test for CellAttributes"""
    
    def setup_method(self, method):
        """Creates empty CellAttributes"""
        
        self.cell_attr = CellAttributes()
    
    def test_undoable_append(self):
        """Test undoable_append"""
        
        pass
    
    def test_getitem(self):
        """Test __getitem__"""
        
        selection_1 = Selection([(2, 2)], [(4, 5)], [55], [55, 66], [(34, 56)])
        selection_2 = Selection([], [], [], [], [(32, 53), (34, 56)])
        
        self.cell_attr.append((selection_1, {"testattr": 3}))
        self.cell_attr.append((selection_2, {"testattr": 2}))
        
        assert self.cell_attr[32, 53]["testattr"] == 2
        assert self.cell_attr[2, 2]["testattr"] == 3

class TestParserMixin(object):
    """Unit test for ParserMixin"""
    
    def test_parse_to_shape(self):
        pass

    def test_parse_to_grid(self):
        pass

    def test_parse_to_attribute(self):
        pass

    def test_parse_to_height(self):
        pass

    def test_parse_to_width(self):
        pass

    def test_parse_to_macro(self):
        pass

class TestStringGeneratorMixin(object):
    """Unit test for StringGeneratorMixin"""
    
    def test_grid_to_strings(self):
        pass

    def test_attributes_to_strings(self):
        pass

    def test_heights_to_strings(self):
        pass

    def test_widths_to_strings(self):
        pass

    def test_macros_to_strings(self):
        pass


class TestDictGrid(object):
    """Unit test for DictGrid"""
    
    def setup_method(self, method):
        """Creates empty DictGrid"""
        
        self.dict_grid = DictGrid((100, 100, 100))
        
    def test_getitem(self):
        """Test __getitem__"""
        
        with pytest.raises(IndexError):
            self.dict_grid[100, 0, 0]
        
class TestDataArray(object):
    """Unit test for DataArray"""
    
    def setup_method(self, method):
        """Creates empty DataArray"""
        
        self.data_array = DataArray((100, 100, 100))
    
    def test_row_heights(self):
        pass

    def test_col_widths(self):
        pass

    def test_cell_attributes(self):
        pass

    def test_keys(self):
        pass

    def test_pop(self):
        pass

    def test_get_shape(self):
        """Test shape attribute"""
        
        assert self.data_array.shape == (100, 100, 100)
        
    def test_set_shape(self):
        """Test shape attribute"""
        
        self.data_array.shape = (10000, 100, 100)
        
        assert self.data_array.shape == (10000, 100, 100)
        
    def test_getstate(self):
        """Test pickle support"""
        
        assert "dict_grid" in self.data_array.__getstate__()

    def test_getitem(self):
        """Test shape attribute"""
        
        pass 

    def test_setitem(self):
        """Single and multiple item assignment test"""
        
        self.data_array[0, 0, 0] = "'Test'"
        ##assert len(self.grid.unredo.undolist) == 1
        self.data_array[0, 0, 0] = "'Tes'"
        ##assert len(self.grid.unredo.undolist) == 2
        
        assert self.data_array[0, 0, 0] == "'Tes'"
        for teststring in v.getstrings(number=100, maxlength=1000):
            x, y, z = [gmpy.rand('next', maxdim) \
                            for maxdim in self.data_array.shape]
            self.data_array[x, y, z] = "".join(["'", teststring, "'"])
            
            assert self.data_array[x, y, z] == "".join(["'", teststring, "'"])
        
    def test_cell_array_generator(self):
        """"""
        
        pass
        
    def test_insert(self):
        """Tests insert operation"""
        
        self.data_array[2, 3, 4] = 42
        self.data_array.insert(1, 100, 0)
        
        assert self.data_array.shape == (200, 100, 100)
        assert self.data_array[2, 3, 4] is None
        
        assert self.data_array[102, 3, 4] == 42
        
    def test_delete(self):
        """Tests delete operation"""
        
        self.data_array[2, 3, 4] = "42"
        self.data_array.delete(1, 1, 0)
        
        assert self.data_array[2, 3, 4] is None
        assert self.data_array[1, 3, 4] == "42"
        print self.data_array.shape
        assert self.data_array.shape == (99, 100, 100)
        
    def test_set_row_height(self):
        pass

    def test_set_col_width(self):
        pass


class TestCodeArray(object):
    """Unit test for CodeArray"""
    
    def setup_method(self, method):
        """Creates empty DataArray"""
        
        self.code_array = CodeArray((100, 10, 3))
        
    def test_getitem(self):
        """Test for item getting, slicing, basic evaluation correctness."""
        
        shape = self.code_array.shape
        x_list = v.getints(1, shape[0]-1, 100)
        y_list = v.getints(1, shape[1]-1, 100)
        z_list = v.getints(1, shape[2]-1, 100)
        for x, y, z in zip(x_list, y_list, z_list):
            assert self.code_array[x, y, z] == None
            self.code_array[:x, :y, :z]
            self.code_array[:x:2, :y:2, :z:-1]
            
        get_shape = numpy.array(self.code_array[:, :, :]).shape
        orig_shape = self.code_array.shape
        assert get_shape == orig_shape
        
        empty_grid = CodeArray((0, 0, 0))
        assert empty_grid[:, :, :].tolist() == []
        
        gridsize = 100
        filled_grid = CodeArray((gridsize, 10, 1))
        for i in v.getints(-2**99, 2**99, 10):
            for j in xrange(gridsize):
                filled_grid[j, 0, 0] = str(i)
                filled_grid[j, 1, 0] = str(i) + '+' + str(j)
                filled_grid[j, 2, 0] = str(i) + '*' + str(j)                
            
            for j in xrange(gridsize):
                assert filled_grid[j, 0, 0] == i
                assert filled_grid[j, 1, 0] == i + j
                assert filled_grid[j, 2, 0] == i * j
                
            for j, funcname in enumerate(['int', 'gmpy.mpz', 'gmpy.mpq']):
                filled_grid[0, 0, 0] = "gmpy = __import__('gmpy')"
                filled_grid[0, 0, 0]
                filled_grid[1, 0, 0] = "math = __import__('math')"
                filled_grid[1, 0, 0]
                filled_grid[j, 3, 0] = funcname +' (' + str(i) + ')'
                
                res = eval(funcname +"("+"i"+")")
                assert filled_grid[j, 3, 0] == eval(funcname +"("+"i"+")")
        #Test X, Y, Z
        for i in xrange(10):
            self.code_array[i, 0, 0] = str(i)
        assert [self.code_array((i, 0, 0)) for i in xrange(10)] == \
                    map(str, xrange(10))
        
        assert [self.code_array[i, 0, 0] for i in xrange(10)] == range(10)
        
        # Test cycle detection
        
        filled_grid[0, 0, 0] = "numpy.arange(0, 10, 0.1)"
        filled_grid[1, 0, 0] = "sum(S[0,0,0])"
        
        assert filled_grid[1, 0, 0] == sum(numpy.arange(0, 10, 0.1))
        
        filled_grid[0, 0, 0] = "S[5:10, 1, 0]"
        assert filled_grid[0, 0, 0].tolist() == range(7, 12)

    def test_cycle_detection(self):
        """Tests creation of cycle detection graph"""
        
        self.code_array[0, 1, 0] = 'S[1, 1, 0]'
        self.code_array[1, 1, 0] = 'S[0, 1, 0]'
        res = self.code_array[1, 1, 0]
        comp = KeyError("Circular dependency at (1, 1, 0)")
        assert repr(res) == repr(comp)

    def test_findnextmatch(self):
        """Find method test"""
        
        code_array = self.code_array
        
        for i in xrange(100):
            code_array[i, 0, 0] = str(i)
        
        assert code_array[3, 0, 0] == 3
        assert code_array.findnextmatch((0, 0, 0), "3", "DOWN") == (3, 0, 0)
        assert code_array.findnextmatch((0, 0, 0), "99", "DOWN") == (99, 0, 0)
