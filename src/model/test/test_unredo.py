#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit test for unredo.py"""

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

from model.unredo import UnRedo

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
