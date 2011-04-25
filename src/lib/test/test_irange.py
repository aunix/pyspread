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

"""Unit-tests for irange.irange class.

Usage:

$ python -W error test_irange.py --with-doctest

Requires: nose (``$ pip install nose``)
"""

from __future__ import nested_scopes
import pickle
import sys
import unittest

try: long
except NameError:
    long = int # Python 3.x

try: xrange
except NameError:
    xrange = range # Python 3.x

try: callable
except NameError: # Python 3.x
    callable = lambda f: hasattr(f, '__call__')

import nose

from lib.irange import irange

if hasattr(sys, "maxint"):
    MAXINT = sys.maxint
else:
    MAXINT = sys.maxsize # Python 3.x

BIGINT = 10**200
LENGTH_CUTOFF = 1000

def skipif(predicate, msg=None):
    """Skip the test if `predicate()` is true."""
    if msg is None:
        msg = getattr(predicate, '__name__', None)
        msg = msg or "skip test due to test condition"

    if not callable(predicate): # allow non-callable condition
        predicate = lambda p=predicate: p

    def decorator(test_fun):
        if not nose.util.isgenerator(test_fun):
            def wrapper(*args, **kwargs):
                if not predicate():
                    return test_fun(*args, **kwargs)
                else:
                    raise nose.SkipTest(msg)
        else: # generator
            def wrapper(*args, **kwargs):
                if not predicate():
                    for t in test_fun(*args, **kwargs):
                        yield t
                else:
                    raise nose.SkipTest(msg)

        return nose.tools.make_decorator(test_fun)(wrapper)
    return decorator


def ispypy():
    """Whether the running interpreter is pypy."""
    return hasattr(sys, 'pypy_version_info')


def eq_range(a, start, stop, step):
    """Assert that `a` is a range defined by `start`, `stop`, `step`."""
    i = start
    for j in a:
        nose.tools.eq_(j, i)
        i += step


def eq_irange(a, b):
    """Assert that `a` equals `b`.

Where `a`, `b` are `irange` objects
"""
    nose.tools.eq_(a._start, b._start)
    nose.tools.eq_(a._stop, b._stop)
    nose.tools.eq_(a._step, b._step)
    nose.tools.eq_(a.length, b.length)

    if a.length < LENGTH_CUTOFF: # test equility for small ranges
        nose.tools.eq_(list(a), list(b))
        eq_range(a, a._start, a._stop, a._step)


def _get_short_iranges_args():
    # perl -E'local $,= q/ /; $n=100; for (1..20)
    # > { say map {int(-$n + 2*$n*rand)} 0..int(3*rand) }'
    input_args = """\
67
-11
51
-36
-15 38 19
43 -58 79
-91 -71
-56
3 51
-23 -63
-80 13 -30
24
-14 49
10 73
31
38 66
-22 20 -81
79 5 84
44
40 49
"""
    return [[int(arg) for arg in line.split()]
            for line in input_args.splitlines() if line.strip()]


def _get_iranges_args():
    N = 2**100
    return [(start, stop, step)
            for start in range(-2*N, 2*N, N//2+1)
            for stop in range(-4*N, 10*N, N+1)
            for step in range(-N//2, N, N//8+1)]


def _get_short_iranges():
    return [irange(*args) for args in _get_short_iranges_args()]


def _get_iranges():
    return (_get_short_iranges() +
            [irange(*args) for args in _get_iranges_args()])


@nose.tools.raises(TypeError)
def test_kwarg():
    irange(stop=10)

def test_len_overflow24():
    # __len__() should return 0 <= outcome < 2**31 on py2.4
    try: len(irange(MAXINT))
    except OverflowError:
        if sys.version_info[:2] == (2,4):
            pass
        else:
            raise

@nose.tools.raises(OverflowError)
def test_len_overflow():
    len(irange(MAXINT+1))

def test_float_arg():
    def _test(args):
        irange(*map(int, args)) # args work as ints
        # args raise TypeError as floats
        nose.tools.assert_raises(TypeError, irange, *args)

    for args in [(1.0,), (1e10, 1e10), (1e1, 1e1), (-1, 2, 1.0), (1.0, 2),
                 (1, 2, 1.0), (1e100, 1e101, 1e101)]:
        yield _test, args

def test_int_subclass_args():
    class Int(int):
        pass
    class Long(long):
        pass

    for args in [ (Int(10,),),
                  (Int(1), Int(2), Int(1)),
                  (Long(1),),
                  (1, 2, Long(1e100)),
                  (True,),]:
        n = len(args)
        if n == 1:
            yield irange, args[0]
        elif n == 2:
            yield irange, args[0], args[1]
        elif n == 3:
            yield irange, args[0], args[1], args[2]
        else:
            assert 0


@nose.tools.raises(TypeError)
def test_empty_args():
    irange()


def test_empty_range():
    for args in (
        "-3",
        "1 3 -1",
        "1 1",
        "1 1 1",
        "-3 -4",
        "-3 -2 -1",
        "-3 -3 -1",
        "-3 -3",
        ):
        r = irange(*[int(a) for a in args.split()])
        yield nose.tools.eq_, len(r), 0
        L = list(r)
        yield nose.tools.eq_, len(L), 0


def test_small_ints():
    for args in _get_short_iranges_args():
        ir, r = irange(*args), xrange(*args)
        yield nose.tools.eq_, len(ir), len(r)
        yield nose.tools.eq_, list(ir), list(r)


def test_len_type():
    ir = irange(10)
    yield nose.tools.eq_, type(len(ir)), int
    yield nose.tools.eq_, type(len(xrange(10))), int
    yield nose.tools.eq_, type(len(range(10))), int


def test_big_ints():
    N = 10**100
    for args, len_ in [
        [(N,), N],
        [(N, N+10), 10],
        [(N, N-10, -2), 5],
        ]:
        ir = irange(*args)
        #
        ir[ir.length-1]
        #
        if len(args) >= 2:
            r = range(*args)
            yield nose.tools.eq_, list(ir), list(r)
            yield nose.tools.eq_, ir[ir.length-1], r[-1]
            yield nose.tools.eq_, list(reversed(ir)), list(reversed(r))


def test_negative_index():
    yield nose.tools.eq_, irange(10)[-1], 9
    yield nose.tools.eq_, irange(2**100+1)[-1], 2**100


def test_reversed():
    for r in _get_iranges():
        if r.length > LENGTH_CUTOFF: continue # skip long
        yield nose.tools.eq_, list(reversed(list(reversed(r)))), list(r)
        yield eq_range, r, r._start, r._stop, r._step


def test_pickle_all_but_highest_protocol():
    for proto in range(pickle.HIGHEST_PROTOCOL):
        yield _test_pickle, proto

@skipif(ispypy, msg="known failure. It causes 'segmentation fault' with pypy-c")
def test_pickle_highest_protocol():
    yield _test_pickle, pickle.HIGHEST_PROTOCOL
    yield _test_pickle, -1
    yield _test_pickle, None


def _test_pickle(proto):
    for r in _get_iranges():
        if proto is None:
            rp = pickle.loads(pickle.dumps(r))
        else:
            rp = pickle.loads(pickle.dumps(r, proto))
        eq_irange(rp, r)


def test_equility():
    for args in _get_iranges_args():
        a, b = irange(*args), irange(*args)
        yield nose.tools.ok_, a is not b
        yield nose.tools.assert_not_equals, a, b
        yield nose.tools.eq_, a.length, b.length
        if a.length < LENGTH_CUTOFF: # skip long
            yield nose.tools.eq_, list(a), list(b), (a, b)
        yield eq_irange, a, b


def test_contains():
    class IntSubclass(int):
        pass

    for r in [irange(10), irange(9,-1,-1)]:
        for i in range(10):
            yield nose.tools.ok_, i in r
            yield nose.tools.ok_, IntSubclass(i) in r

        yield nose.tools.ok_, 10 not in r
        yield nose.tools.ok_, -1 not in r
        yield nose.tools.ok_, IntSubclass(10) not in r
        yield nose.tools.ok_, IntSubclass(-1) not in r


def test_repr():
    yield nose.tools.eq_, repr(irange(True)), repr(irange(1))
    for r in _get_iranges():
        yield eq_irange, eval(repr(r)), r


class _indices(object):
    def __getitem__(self, slices):
        # make sure slices is iterable
        try: slices = list(iter(slices))
        except TypeError:
            slices = [slices]
        # behaviour for short and long integers must be the same
        for N in (None, 2**101):
            for s in slices:
                if type(s) == slice:
                    start, stop, step = s.start, s.stop, s.step
                    if N is not None:
                        start = start and start+N
                        stop = stop and stop+N
                        step = step
                    # try from 0 to 3 arguments
                    for args in [(), (stop,), (start, stop),
                                 (start, stop, step)]:
                        try:
                            lr = irange(*args)
                            if len(args) == 1:
                                nstart, nstep, nstop = 0, 1, stop
                                assert stop is not None
                            if len(args) == 2:
                                nstart, nstop, nstep = start, stop, 1
                                assert start is not None
                                assert stop is not None
                            if len(args) == 3:
                                nstart, nstop, nstep = start, stop, step
                                assert start is not None
                                assert stop is not None
                                assert step is not None
                            assert 0 <= len(args) < 4

                            nose.tools.eq_(lr._start, nstart)
                            nose.tools.eq_(lr._stop, nstop)
                            nose.tools.eq_(lr._step, nstep)
                            if lr.length < LENGTH_CUTOFF:
                                nose.tools.eq_(list(lr),
                                               list(range(nstart, nstop, nstep)))
                        except TypeError:
                            # expected if any of the arguments is None
                            if len(args) > 0:
                                assert start is None or stop is None or \
                                       step is None
                else: # s is not slice
                    assert s is not None
                    if N is not None:
                        s = s + N
                    lr = irange(s)
                    nose.tools.eq_(lr.length, s)

def test_new():
    #
    _indices()[3,4:,:5,6:7,7:8,8:13:2,:,-1:,:-2,10:6:-2,::11,::]
    _indices()[0,0:,:0,0:0]

@nose.tools.raises(TypeError)
def test_new_none():
    irange(None)

@nose.tools.raises(ValueError)
def test_zero_step():
    _indices()[1:2:0]

def test_overflow():
    lo, hi, step = MAXINT-2, 4*MAXINT+3, MAXINT // 10
    lr = irange(lo, hi, step)
    xr = irange(MAXINT//4, MAXINT//2, MAXINT // 10)
    nose.tools.eq_(list(lr), list(range(lo, hi, step)))

def test_index_error():
    r = irange(10)
    for i in [-11, 10, 11]:
        yield nose.tools.assert_raises, IndexError, r.__getitem__, i

def test_getitem():
    r = irange(MAXINT-2, MAXINT+3)
    for i in range(5):
        yield nose.tools.eq_, r[i], MAXINT-2+i
    for i in range(-1, -5, -1):
        yield nose.tools.eq_, r[i], MAXINT+3+i

    L = []
    L[:] = r
    yield nose.tools.eq_, len(L), len(r)
    yield nose.tools.eq_, L, list(r)


class TestBIGINT(unittest.TestCase):

    def setUp(self):
        self.lr = irange(BIGINT)

    def test_big_length(self):
        nose.tools.eq_(self.lr.length, BIGINT)

    @nose.tools.raises(OverflowError)
    def test_overflow_len(self):
        len(self.lr)

    def tearDown(self):
        self.lr = None


if __name__ == "__main__":
    import nose
    sys.exit(nose.main())
