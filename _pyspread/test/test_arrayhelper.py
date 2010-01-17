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
        
        self.dim = 100, 10, 3
        self.grid = _datastructures.PyspreadGrid(dimensions=self.dim)
    
    def test_getflatpos(self):
        """Tests flattened position calculation in Fortran order"""
        
        testarray = numpy.zeros((10, 20))
        assert _arrayhelper.getflatpos(testarray, (0, 0)) == 0
        assert _arrayhelper.getflatpos(testarray, (3, 3)) == 33
        assert _arrayhelper.getflatpos(testarray, (9, 19)) == 199
        assert _arrayhelper.getflatpos(testarray, (10, 19)) == 200
        assert _arrayhelper.getflatpos(testarray, (10**25, 0)) == 10**25
    
    def test_getshapedpos(self):
        """Tests shaped position calculation in Fortran order"""
        
        testarray = numpy.zeros((10, 20))
        assert _arrayhelper.getshapedpos(testarray, 0) == (0, 0)
        assert _arrayhelper.getshapedpos(testarray, 1) == (1, 0)
        assert _arrayhelper.getshapedpos(testarray, 11) == (1, 1)
        assert _arrayhelper.getshapedpos(testarray, 199) == (9, 19)
