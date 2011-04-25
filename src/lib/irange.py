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

"""Define `irange.irange` class

`xrange`, py3k's `range` analog for large integers

Stolen from:
https://github.com/zed/irange/blob/master/irange.py

"""

try: long
except NameError:
    long = int # Python 3.x

try: xrange
except NameError:
    xrange = range # Python 3.x

try: any
except NameError:
    def any(iterable): # for Python 2.4
        for i in iterable:
            if i:
                return True
        return False

import sys as _sys
if hasattr(_sys, "maxint"):
    _MAXINT = _sys.maxint
else:
    _MAXINT = _sys.maxsize # Python 3.x


def _toindex(arg):
    """Convert `arg` to integer type that could be used as an index."""
    
    for cls in (int, long):
        if isinstance(arg, cls): # allow int subclasses
           return int(arg)

    raise TypeError("'%s' object cannot be interpreted as an integer" % (
        type(arg).__name__,))


class irange(object):
    """irange([start,] stop[, step]) -> irange object

    Return an iterator that generates the numbers in the range on demand.

    Pure Python implementation of py3k's `range()`.

    (I.e. it supports large integers)

    If `xrange` and py3k `range()` differ then prefer `xrange`'s behaviour

    Based on:
    http://svn.python.org/view/python/branches/py3k/Objects/
           rangeobject.c?view=markup

    """

    def __new__(cls, *args):
        nargs = len(args)
        if nargs == 1:
            stop = _toindex(args[0])
            start = 0
            step = 1
        elif nargs in (2, 3):
            start = _toindex(args[0])
            stop = _toindex(args[1])
            if nargs == 3:
                step = _toindex(args[2])
                if step == 0:
                    raise ValueError("irange() arg 3 must not be zero")
            else:
                step = 1
        else:
            raise TypeError("irange(): wrong number of arguments," +
                             " got %s" % (args,))

        r = super(irange, cls).__new__(cls)
        assert start is not None
        assert stop is not None
        assert step is not None
        r._start, r._stop, r._step = start, stop, step
        return r

    def length(self):
        """len(self) might throw OverflowError, this method shouldn't."""
        if self._step > 0:
            lo, hi = self._start, self._stop
            step = self._step
        else:
            hi, lo = self._start, self._stop
            step = -self._step
            assert step

        if lo >= hi:
            return 0
        else:
            return (hi - lo - 1) // step + 1

    def __len__(self):
        L = self.length
        if L > _MAXINT:
            raise OverflowError(
                "cannot fit '%.200s' into an index-sized integer" \
                    % type(L).__name__)
        return int(L)

    length = property(length)

    def __getitem__(self, i):
        if i < 0:
            i = i + self.length
        if i < 0 or i >= self.length:
            raise IndexError("irange object index out of range")

        return self._start + i * self._step

    def __repr__(self):
        if self._step == 1:
            return "%s(%r, %r)" % (
                self.__class__.__name__, self._start, self._stop)
        else:

            return "%s(%r, %r, %r)" % (
                self.__class__.__name__, self._start, self._stop, self._step)

    def __contains__(self, ob):
        if type(ob) not in (int, long, bool): # mimic py3k
            # perform iterative search
            return any(i == ob for i in self)

        # if long or bool
        if self._step > 0:
            inrange = self._start <= ob < self._stop
        else:
            assert self._step
            inrange = self._stop < ob <= self._start

        if not inrange:
            return False
        else:
            return ((ob - self._start) % self._step) == 0

    def __iter__(self):
        try:
            return iter(xrange(self._start, self._stop,
                               self._step)) # use `xrange`'s iterator
        except (NameError, OverflowError):
            return self._iterator()

    def _iterator(self):
        len_ = self.length
        i = 0
        while i < len_:
            yield self._start + i * self._step
            i += 1


    def __reversed__(self):
        len_ = self.length
        new_start = self._start + (len_ - 1) * self._step
        new_stop = self._start
        if self._step > 0:
            new_stop -= 1
        else:
            new_stop += 1
        return irange(new_start, new_stop, -self._step)

    def __getnewargs__(self):
        return self._start, self._stop, self._step
    
def slice_range(slc, length):
    """Replaces range(length)[slc]"""
    
    __indices = slc.indices(length)
    return irange(*__indices)
