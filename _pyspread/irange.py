#! /usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import count, imap, islice

def scount(n=0, step=1):
    """Count that supports a step attribute"""
    
    while True:
        yield n
        n += step

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
        return islice(scount(start, step), (stop-start+step-1) // step)
        
    elif step < 0:
        if stop > start:
            return (_ for _ in [])
        return islice(scount(start, step), (stop-start+step+1) // step)
        
    else:
        raise ValueError, "irange() step argument must not be zero"

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
    
    indices = slc.indices(length)
    return irange(*indices)
