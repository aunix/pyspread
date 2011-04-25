#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit test for _datastructures.py"""

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


import gmpy
import numpy

import wx

app = wx.App()

import _pyspread._datastructures as _datastructures
import vartypes as v

gmpy.rand('seed', 2)

class TestPyspreadGrid(object):
    """Unit test for PyspreadGrid"""
    
    def setup_method(self, method):
        """Creates a basic grid"""
        
        self.dim = 100, 10, 3
        self.grid = _datastructures.PyspreadGrid(dimensions=self.dim)
        
    def test_init(self):
        """Test for completeness of grid attributes and correct size."""
        
        assert hasattr (self.grid, 'sgrid')
        assert hasattr (self.grid.sgrid, 'macros')
        assert hasattr (self.grid, 'unredo')
        x_list, y_list, z_list = [v.getints(1, 100, 100) for i in xrange(3)]
        for dim in zip(x_list, y_list, z_list):
            self.grid = _datastructures.PyspreadGrid(dimensions=dim)
            del self.grid
    
    def test_getitem(self):
        """Test for item getting, slicing, basic evaluation correctness."""
        
        shape = self.grid.sgrid.shape
        x_list = v.getints(1, shape[0]-1, 100)
        y_list = v.getints(1, shape[1]-1, 100)
        z_list = v.getints(1, shape[2]-1, 100)
        for x, y, z in zip(x_list, y_list, z_list):
            assert self.grid[x, y, z] == None
            self.grid[:x, :y, :z]
            self.grid[:x:2, :y:2, :z:-1]
            
        get_shape = numpy.array(self.grid[:, :, :]).shape
        orig_shape = self.grid.sgrid.shape
        assert get_shape == orig_shape
        
        empty_grid = _datastructures.PyspreadGrid(dimensions=(0, 0, 0))
        assert empty_grid[:, :, :].tolist() == []
        
        gridsize = 100
        filled_grid = _datastructures.PyspreadGrid(dimensions=(gridsize, 10, 1))
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
            self.grid[i, 0, 0] = str(i)
        assert [self.grid.sgrid[i, 0, 0] for i in xrange(10)] == \
                    map(str, xrange(10))
        
        assert [self.grid[i, 0, 0] for i in xrange(10)] == range(10)
        
        # Test cycle detection
        
        filled_grid[0, 0, 0] = "numpy.arange(0, 10, 0.1)"
        filled_grid[1, 0, 0] = "sum(S[0,0,0])"
        
        assert filled_grid[1, 0, 0] == sum(numpy.arange(0, 10, 0.1))
        
    def test_setitem(self):
        """Single and multiple item assignment test"""
        
        self.grid[0, 0, 0] = "'Test'"
        assert len(self.grid.unredo.undolist) == 1
        self.grid[0, 0, 0] = "'Tes'"
        assert len(self.grid.unredo.undolist) == 2
        
        assert self.grid[0, 0, 0] == 'Tes'
        for teststring in v.getstrings(number=100, maxlength=1000):
            x, y, z = [gmpy.rand('next', maxdim) for maxdim in self.dim]
            self.grid[x, y, z] = "".join(["'", teststring, "'"])
            
            assert self.grid[x, y, z] == teststring
    
    def test_len(self):
        """Test for sameness of different grid sizes"""
        
        assert len(self.grid) == len(self.grid.sgrid)

    def test_remove(self):
        """Tests remove operation with single cell, slice, random cells"""
        
        dim = list(self.dim)
        for currdim in xrange(len(dim)):
            # currdim is the dimension for insertion
            cells_2b_removed = v.getints(1, dim[currdim], 6)
            cells_2b_leftalone = v.getints(0, 20, 6)
            for rem, norem in zip(cells_2b_removed, cells_2b_leftalone):
                # gmpy bug: [mpz(2), None].count(None)
                removalpoint = [None] * 3
                removalpoint[currdim] = int(rem)
                #print "Shape",self.grid.shape, removalpoint
                self.grid.remove(removalpoint, norem)
                # Only existent cells are removed
                dim[currdim] -= max([0, min([dim[currdim] - rem, norem])])
                #print dim, rem, norem
                assert self.grid.sgrid.shape == self.grid.sgrid.shape
                sgridshape = tuple(self.grid.sgrid.shape)
                assert sgridshape == tuple(dim)
    
    def test_isinsclice(self):
        """Tests if key in a slice is identified correctly"""
        
        slc = slice(1, 2, 1)
        res = 0
        dim = 0
        key = 0
        assert self.grid.isinsclice(slc, dim, key) == res
        
        key = 2
        assert self.grid.isinsclice(slc, dim, key) == res
        
        key = 1
        res = 1
        assert self.grid.isinsclice(slc, dim, key) == res
        
    
    def test_key_in_slicetuple(self):
        """Tests if keys in a slicetuple are identified correctly"""
        
        slicetuple = (slice(None, None, None), \
                      slice(None, None, None), \
                      slice(None, None, None))
        key = (0, 0, 0)
        res = 1
        assert self.grid.key_in_slicetuple(key, slicetuple) == res

        key = (1, 1, 1)
        assert self.grid.key_in_slicetuple(key, slicetuple) == res
        
        key = (1, 3, 2)
        assert self.grid.key_in_slicetuple(key, slicetuple) == res

        key = (self.dim[0] - 1, self.dim[1] - 1, self.dim[2] - 1)
        assert self.grid.key_in_slicetuple(key, slicetuple) == res        
        
        slicetuple = (slice(1, 2, 1), slice(1, 2, 1), slice(1, 2, 1))
        key = (0, 0, 0)
        res = 0
        assert self.grid.key_in_slicetuple(key, slicetuple) == res

        key = (0, 1, 1)
        assert self.grid.key_in_slicetuple(key, slicetuple) == res

        key = (1, 0, 1)
        assert self.grid.key_in_slicetuple(key, slicetuple) == res
        
        key = (1, 1, 0)
        assert self.grid.key_in_slicetuple(key, slicetuple) == res

        key = (2, 1, 1)
        assert self.grid.key_in_slicetuple(key, slicetuple) == res
        
        key = (1, 2, 1)
        assert self.grid.key_in_slicetuple(key, slicetuple) == res

        key = (1, 1, 2)
        assert self.grid.key_in_slicetuple(key, slicetuple) == res

        key = (2, 2, 2)
        assert self.grid.key_in_slicetuple(key, slicetuple) == res

        key = (1, 1, 1)
        res = 1
        assert self.grid.key_in_slicetuple(key, slicetuple) == res

        
        
        """       
        keys = ((0, 0, 0), (1, 1, 1), (1, 3, 2), \
                (self.dim[0] - 1, self.dim[1] - 1, self.dim[2] - 1))

        tuples = \
            [((None, None, None), (None, None, None), (None, None, None)), \
             ((1, 2, 1), (1, 2, 1), (1, 2, 1)), \
             ((0, 5, 1), (0, 5, 1), (0, 2, 1)), \
             ((None, 0, -1), (1, None, 2), (23, None, -2))]
        
        slicetuples = [tuple(map(slice, ele) for ele in tup) for tup in tuples]
        
        res = [[1, 1, 1, 1], [0, 1, 0, 0], [1, 1, 0, 0], [0, 0, 1, 1]]
        
        for r, slicetup in zip(res, slicetuples):
            for key, rr in zip(keys, r):
                assert self.grid.key_in_slicetuple(key, slicetup) == rr
        """
        
    def test_cycle_detection(self):
        """Tests creation of cycle detection graph"""
        self.grid[0, 1, 0] = '5'
        self.grid[1, 1, 0] = 'S[:10, 1, 0]'
        
        assert self.grid[1, 1, 0][0] == 'Circular dependency at (1, 1, 0)'
    
    def test_insert(self):
        """Tests insert operation with single cell, slice, random cells"""
        
        dim = list(self.dim)
        for currdim in xrange(len(dim)):
            # curredim is the dimension for insertion
            cells_2b_inserted = v.getints(1, dim[currdim], 10)
            cells_2b_leftalone = v.getints(0, 20, 10)
            for ins, noins in zip(cells_2b_inserted, cells_2b_leftalone):
                """ gmpy bug: [mpz(2), None].count(None) """
                insertionpoint = [None] * 3
                insertionpoint[currdim] = int(ins)
                self.grid.insert(insertionpoint, noins)
                dim[currdim] += noins
                assert self.grid.sgrid.shape == self.grid.sgrid.shape
                sgridshape = tuple(self.grid.sgrid.shape)
                #print currdim, self.grid.sgrid.shape
                assert sgridshape == tuple(dim)
                chkpoint = [0] * 3
                chkpoint[currdim] = int(ins)
                assert self.grid[chkpoint[0], chkpoint[1], chkpoint[2]] == None
    
    def test_spread(self):
        """Tests spread method fpr single cells and slices"""
        
        matrix = [[1, 2, 3], [4, 5, 6]]
        grid = self.grid
        sgrid = self.grid.sgrid
        
        grid.spread(matrix, (0, 0, 0))
        assert sgrid[0, 0, 0] == '1'
        assert sgrid[1, 0, 0] == '4'
        assert sgrid[0, 1, 0] == '2'
        
        grid.spread(matrix, (1, 0, 0))
        assert sgrid[1, 0, 0] == '1'
        
        grid.spread(matrix, (self.dim[0] - 1, 0, 0))
        assert sgrid[self.dim[0] - 1, 0, 0] == '1'
        
        grid.spread(matrix, (0, self.dim[1] - 1, 0))
        assert sgrid[0, self.dim[1] - 1, 0] == '1'
        
        grid.spread(matrix, (0, 0, self.dim[2] - 1))
        assert sgrid[0, 0, self.dim[2] - 1] == '1'
        
        grid.spread(matrix, (self.dim[0] - 1, self.dim[1] - 1, self.dim[2] - 1))
        assert sgrid[self.dim[0] - 1, self.dim[1] - 1, self.dim[2] - 1] == '1'

    def test_findnextmatch(self):
        """Find method test"""
        
        for i in xrange(100):
            self.grid.sgrid[i, 0, 0] = str(i)
        
        assert self.grid[3, 0, 0] == 3
        assert self.grid.findnextmatch((0, 0, 0), "3", "DOWN") == (3, 0, 0)
        assert self.grid.findnextmatch((0, 0, 0), "99", "DOWN") == (99, 0, 0)


class TestUnRedo(object):
    """Unit test for UnRedo"""
    def setup_method(self, method):
        """Setup for dummy undo steps"""
        
        self.unredo = _datastructures.UnRedo()
        self.list = []
        self.step = (self.list.append, ["Test"], self.list.pop, [])
    
    def test_mark(self):
        """Test for marking step delimiters"""
    
        self.unredo.mark()
        assert self.unredo.undolist == [] # Empty undolist needs no marking
        
        self.unredo.undolist = [self.step]
        self.unredo.mark()
        assert self.unredo.undolist[-1] == "MARK"

    def test_undo(self):
        """Test for undo operation"""
        self.unredo.undolist = [self.step]
        self.unredo.undo()
        assert self.list == ["Test"]
        assert self.unredo.redolist == [self.step]
        
        # Test Mark
        self.unredo.mark()
        self.list.pop()
        self.unredo.append(self.step[:2], self.step[2:])
        self.unredo.undo()
        assert self.list == ["Test"]
        assert "MARK" not in self.unredo.undolist
        assert "MARK" in self.unredo.redolist
        
        # When Redolist != [], a MARK should appear
        self.unredo.mark()
        self.list.pop()
        self.unredo.append(self.step[:2], self.step[2:])
        self.unredo.redolist.append('foo')
        self.unredo.undo()
        assert self.list == ["Test"]
        assert "MARK" not in self.unredo.undolist
        assert "MARK" in self.unredo.redolist

    def test_redo(self):
        """Test for redo operation"""
        self.list.append("Test")
        self.unredo.redolist = [self.step]
        self.unredo.redo()
        assert self.list == []
        
        # Test Mark

    def test_reset(self):
        """Test for resettign undo"""
        
        self.unredo.reset()
        assert self.unredo.undolist == []
        assert self.unredo.redolist == []

    def test_append(self):
        """Tests append operation"""
        
        self.unredo.append(self.step[:2], self.step[2:])
        assert len(self.unredo.undolist) == 1
        assert self.unredo.undolist[0] == self.step

class TestDictGrid(object):
    """Unit test for DictGrid"""
    def setup_method(self, method):
        """Setup for dummy undo steps"""
        
        self.dictgrid = _datastructures.DictGrid(shape = (1000,1000,1000))
        self.dictgrid[(1, 2, 3)] = 1
        self.dictgrid[(2, 2, 3)] = 2
        self.dictgrid[(3, 2, 3)] = 3
        self.dictgrid[(4, 2, 3)] = 4
        self.dictgrid[1, 0, 3] = 23

    def test_getitem(self):
        assert self.dictgrid[1,2,3] == 1
        
        assert self.dictgrid[1:5, 2, 3].shape == numpy.array([1, 2, 3, 4]).shape
        assert all(self.dictgrid[1:5, 2, 3] == [1, 2, 3, 4])

        assert self.dictgrid[1:5:2, 2, 3].shape == numpy.array([1, 3]).shape
        assert all(self.dictgrid[1:5:2, 2, 3] == numpy.array([1, 3]))

        assert self.dictgrid[4::-1,2,3].shape == numpy.array([4, 3, 2, 1, None]).shape
        assert all(self.dictgrid[4::-1,2,3] == [4, 3, 2, 1, None])

        assert self.dictgrid[:,2,3].shape == numpy.array([None, 1, 2, 3, 4] + [None] * 995).shape
        assert all(self.dictgrid[:,2,3] == [None, 1, 2, 3, 4] + [None] * 995)

        assert self.dictgrid[1:5, :3, 3].shape == numpy.array([[23, None, 1],
                                             [None, None, 2],
                                             [None, None, 3],
                                             [None, None, 4]]).shape
        assert numpy.all(self.dictgrid[1:5, :3, 3] == numpy.array([[23, None, 1],
                                             [None, None, 2],
                                             [None, None, 3],
                                             [None, None, 4]]))
        assert len(self.dictgrid[2:4,2:4,2:4:-1]) == 0

    
    def test_set_shape(self):
        self.dictgrid.set_shape((10000, 1000, 100))
        
        dict_indices = map(list, self.dictgrid.indices)
        indices = [range(size) for size in (10000, 1000, 100)]
        
        assert dict_indices == indices
            

