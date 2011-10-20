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

from sys import path, modules

path.insert(0, "..") 
path.insert(0, "../..") 

from lib.selection import Selection
import actions._grid_actions

class TestSelection(object):
    """Unit test for Selection"""
    
    def setup_method(self, method):
        """Creates selection"""
        
        self.selection = Selection([], [], [], [], [(32, 53), (34, 56)])
        self.SelectionCls = actions._grid_actions.Selection
        
    def test_str(self):
        """Test string representation"""
        
        assert str(self.selection) == \
               "Selection([], [], [], [], [(32, 53), (34, 56)])"
        
    def test_contains(self):
        """Tests __contains__ functionality of selection class
        
        (ele in selection)"""
        
        assert (32, 53) in self.selection
        assert not (23, 34534534) in self.selection
        
        # Test block selection
        
        selection = self.SelectionCls([(4, 5)], [(100, 200)], [], [], [])
        cells_in_selection = ((i, j) for i in xrange(4, 100, 5) 
                                     for j in xrange(5, 200, 5))
        
        for cell in cells_in_selection:
            assert cell in selection
        
        cells_not_in_selection = \
            [(0, 0), (0, 1), (1, 0), (1, 1), (4, 4), (3, 5),
             (100, 201), (101, 200), (101, 201), (10**10, 10**10),
             [0, 0]]
        
        for cell in cells_not_in_selection:
            assert cell not in selection
        
        # Test row selection
        
        # Test column selection
        
        # Test cell selection
        
    def test_get_bbox(self):
        """Test bounding box creation"""
        
        assert self.selection.get_bbox() == ((32, 53), (34, 56))
        
        sel_tl, sel_br = [(4, 5)], [(100, 200)]
        
        selection = self.SelectionCls(sel_tl, sel_br, [], [], [])
        bbox_tl, bbox_br = selection.get_bbox() 
        assert bbox_tl == sel_tl[0]
        assert bbox_br == sel_br[0]
