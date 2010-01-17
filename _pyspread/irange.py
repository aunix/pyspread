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

def irange(start, stop=None, step=1):
    """Range for long integers
    
    Usage: irange([start], stop, [step])
    
    Parameters
    ----------
    start: Integer, defaults to 0
    stop: Integer
    step: Integer, defaults to 1
    
    Note on long integers
    ---------------------
    
    Each of the three parameters can be long integers.
    If stop < start: start(stop-start+step-1) // step must be a short integer.
    If stop > start: start(stop-start+step+1) // step must be a short integer.
    
    """
    
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
        

def indices(slc, length):
    """Long integer dropin for slice method indices"""
    
    if length < 0:
        raise ValueError, "Length must be >= 0"
        
    if slc.step is None:
        step = 1
    else:
        step = slc.step
    
    if slc.start is None:
        if step < 0:
            start = length - 1
        else:
            start = 0
    else:
        start = slc.start
        if start < 0:
            start += length
    
    if slc.stop is None:
        if step < 0:
            stop = -1
        else:
            stop = length
    else:
        stop = slc.stop
        if stop < 0:
            stop += length
    
    return start, stop, step

def slice_range(slc, length):
    """Replaces renge(length)[slc]"""
    
    __indices = slc.indices(length)
    return irange(*__indices)
