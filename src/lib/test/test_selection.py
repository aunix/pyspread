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

class TestSelection(object):
    """Unit test for Selection"""
    
    def setup_method(self, method):
        """Creates selection"""
        
        self.selection = Selection([], [], [], [], [(32, 53), (34, 56)])
        
    def test_str(self):
        """Test string representation"""
        
        assert str(self.selection) == \
               "Selection([], [], [], [], [(32, 53), (34, 56)])"
        
    def test_contains(self):
        """Test contains check (ele in selection)"""
        
        assert (32, 53) in self.selection
        assert not (23, 34534534) in self.selection
        
    def test_get_bbox(self):
        """Test bounding box creation"""
        
        assert self.selection.get_bbox() == ((32, 53), (34, 56))
