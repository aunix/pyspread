#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2009 Martin Manns
# Distributed under the terms of the GNU General Public License

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
# along with pyspread.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

import lib.irange as irange

# Test support code

def params(funcarglist):
    def wrapper(function):
        function.funcarglist = funcarglist
        return function
    return wrapper

def pytest_generate_tests(metafunc):
    for funcargs in getattr(metafunc.function, 'funcarglist', ()):
        metafunc.addcall(funcargs=funcargs)

# Actual test code


class TestIRange(object):
    """Test class for IRange class"""
    
    param_slices = [ \
        {'start': None, 'stop': None, 'step': None, 'length': 0},
        {'start': None, 'stop': None, 'step': None, 'length': 1},
        {'start': None, 'stop': None, 'step': None, 'length': 2},
        {'start': None, 'stop': None, 'step': None, 'length': 10},
        {'start': None, 'stop': None, 'step': None, 'length': 1000},
        {'start': None, 'stop': None, 'step': None, 'length': 200000},
        {'start': None, 'stop': None, 'step': None, 'length': 10**10},
    ]
    
    @params(param_slices)
    def test_iter(self):
        """"""
        
        pass
    
    @params(param_slices)
    def test_len(self):
        """"""
        
        pass
    
param_slices = []
@params(param_slices)
def test_indices(self, start, stop, step, length):
    """"""
    
    pass

@params(param_slices)
def test_slice_range(self, start, stop, step, length):
    """"""
    
    pass
        
