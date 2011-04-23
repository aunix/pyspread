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

"""
irange
======

Arbitrary size range and slicing operations

Provides
--------

 * irange: xrange drop in
 * indices: slice.indices drop in
 * slice_range: use this instead of range(length)[slice]

"""

from itertools import count, takewhile
import types

class IRange(object):
    """Range for long integers
    
    Usage: irange([start], [stop], [step])
    
    Parameters
    ----------
    start: Integer, defaults to None
    stop: Integer, defaults to None
    step: Integer, defaults to None
    
    Note on long integers
    ---------------------
    
    Each of the three parameters can be long integers.
    If stop < start: start(stop-start+step-1) // step must be a short integer.
    If stop > start: start(stop-start+step+1) // step must be a short integer.
    
    """

    def __init__(self, start=None, stop=None, step=None):
        self.start = start
        self.stop = stop
        self.step = step
    
    def __iter__(self):
        
        start = self.start
        stop = self.stop
        step = self.step
        
        if start is None:
            raise TypeError, "range() integer argument expected, got NoneType"
        
        if stop is None:
            stop = start
            start = 0
        
        if step is None:
            step = 1
        
        if step > 0:
            if stop < start:
                return (_ for _ in [])
            cond = lambda x: x < stop
            
        elif step < 0:
            if stop > start:
                return (_ for _ in [])
            cond = lambda x: x > stop
            
        else:
            raise ValueError, "irange() step argument must not be zero"
        
        return takewhile(cond, (start + i * step for i in count()))

    def __len__(self):
        
        start = self.start
        stop = self.stop
        step = self.step
        
        return max(0, (stop - start) / step)


def indices(slc, length):
    """indices(slice, len) -> (start, stop, stride)

    Assuming a sequence of length len, calculate the start and stop
    indices, and the stride length of the extended slice described by
    S. Out of bounds indices are clipped in a manner consistent with the
    handling of normal slices."""
    
    if length < 0:
        raise ValueError, "Length must be >= 0"
        
    if slc.step is None:
        stride = 1
    else:
        stride = slc.step
    
    if slc.start is None:
        if stride < 0:
            start = length - 1
        else:
            start = 0
    else:
        start = slc.start
        if start < 0:
            start += length
    
    if slc.stop is None:
        if stride < 0:
            stop = -1
        else:
            stop = length
    else:
        stop = slc.stop
        if stop < 0:
            stop += length
    
    return start, stop, stride
    
def slice_range(slc, length):
    """Replaces range(length)[slc]"""
    
    __indices = slc.indices(length)
    return irange(*__indices)
