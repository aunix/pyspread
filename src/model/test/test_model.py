#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit test for _layer0.py"""

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

import wx

from model.model import KeyValueStore, CellAttributes, DictGrid, UnRedo
from model.model import DataArray, CodeArray

from lib.selection import Selection

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
        
    def test_getitem(self):
        """Test __getitem__"""
        
        selection_1 = Selection([(2, 2)], [(4, 5)], [55], [55, 66], [(34, 56)])
        selection_2 = Selection([], [], [], [], [(32, 53), (34, 56)])
        
        self.cell_attr.append((selection_1, {"testattr": 3}))
        self.cell_attr.append((selection_2, {"testattr": 2}))
        
        assert self.cell_attr[32, 53]["testattr"] == 2
        assert self.cell_attr[2, 2]["testattr"] == 3

class TestDictGrid(object):
    """Unit test for DictGrid"""
    
    def setup_method(self, method):
        """Creates empty DictGrid"""
        
        self.dict_grid = DictGrid((100, 100, 100))
        
    def test_getitem(self):
        """Test __getitem__"""
        
        with pytest.raises(IndexError):
            self.dict_grid[100, 0, 0]


class TestUnRedo(object):
    """Unit test for UnRedo"""
    def setup_method(self, method):
        """Setup for dummy undo steps"""
        
        self.unredo = UnRedo()
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
        
class TestDataArray(object):
    """Unit test for DataArray"""
    
    def setup_method(self, method):
        """Creates empty DataArray"""
        
        self.data_array = DataArray((100, 100, 100))
        
    def test_get_shape(self):
        """Test shape attribute"""
        
        assert self.data_array.shape == (100, 100, 100)
        
    def test_set_shape(self):
        """Test shape attribute"""
        
        pass
        
    def test_getstate(self):
        """Test shape attribute"""
        
        pass 

    def test_is_slice_like(self):
        """Test shape attribute"""
        
        pass 
        
    def test_is_string_like(self):
        """Test shape attribute"""
        
        pass 
        
    def test_getitem(self):
        """Test shape attribute"""
        
        pass 

    def test_setitem(self):
        """Test shape attribute"""
        
        pass 
        
    def test_cell_array_generator(self):
        """"""
        
        pass
        
    def test_insert(self):
        """"""
        
        pass
        
    def test_delete(self):
        """"""
        
        pass
        

class TestCodeArray(object):
    """Unit test for CodeArray"""
    
    def setup_method(self, method):
        """Creates empty DataArray"""
        
        self.code_array = CodeArray((100, 100, 100))
        
    def test_getitem(self):
        """Test shape attribute"""
        
        pass
