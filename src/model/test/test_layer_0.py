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

from model.layer_0 import ArrayDict

class TestArrayDict(object):
    """Unit test for ArrayDict"""
    
    def setup_method(self, method):
        """Creates empty array_dict"""
        
        self.array_dict = ArrayDict()
        
    def test_missing(self):
        """Test if missing value returns None"""
        
        assert self.array_dict[(1,2,3)] is None
        
        self.array_dict[(1,2,3)] = 7
        
        assert self.array_dict[(1,2,3)] == 7
        
    def test_():
        """Test cell_array_generator"""
        
        d[2,3] = 3

        cell_gen = d.cell_array_generator((slice(1, 300000), slice(0, 70)))

        for row in cell_gen:
            [cell for cell in row]
