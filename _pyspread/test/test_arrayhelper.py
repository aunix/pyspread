#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit test for _arrayhelper.py"""

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

import wx.grid
import numpy

app = wx.App()

import _pyspread._datastructures as _datastructures
import _pyspread._arrayhelper as _arrayhelper

class TestPyspreadGrid(object):
    """Unit test for array functions"""
    
    def setup_method(self, method):
        """Creates a basic grid"""
        
        pass
    
    def test_sorted_keys(self):
        keys = [(1, 0, 0), (2, 0, 0), (0, 1, 0), (0, 99, 0), (0, 0, 0), 
                (0, 0, 99), (1, 2, 3)]
        assert \
            list(_arrayhelper.sorted_keys(keys, (0, 1, 0))) == \
             [(0, 1, 0), (0, 99, 0), (1, 2, 3), (0, 0, 99), (0, 0, 0), 
              (1, 0, 0), (2, 0, 0)]
        assert \
            list(_arrayhelper.sorted_keys(keys, (0, 3, 0), reverse=True)) == \
             [(2, 0, 0), (1, 0, 0), (0, 0, 0), (0, 0, 99), (1, 2, 3), 
              (0, 99, 0), (0, 1, 0)]
