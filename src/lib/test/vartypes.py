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

"""Helper class for unit testing that provides random variables."""

import gmpy

gmpy.rand('seed', 1)

RES_LEN = 1000

INTPOOL = \
    {'mandatory': [0, 1, -1, 2**16, -2**16, 2**32, -2**32, 2**52, -2**52],
     'extra': [2, -2, 2**5000+1, -2**5000-1, 2**15, -2**15, 2**31+1, -2**31-1]}

STRPOOL = \
    {'mandatory': ["", " ", "\t", "\n", "0", "print"],
     'extra': ["a" * 1000]}

def getints(minint = 0, maxint = 1, number=RES_LEN):
    """Returns a list of partly random ints
    
    The list starts with the numbers from INTPOOL['mandatory'], continues with
    INTPOOL['extra'] and finishes with uniformly distributed random ints.
    
    Parameters
    ----------
    minint: int, defaults to 0
    \tLower bound of ints in ist
    maxint: int, defaults to 1
    \tUpper bound of ints in ist
    number: int, defaults to RES_LEN (1000)
    \tLength of list
    
    """
    res = INTPOOL['mandatory'][:number]
    res = [x for x in res if minint <= x <= maxint]
    left = number - len(res)
    if left > 0:
        res += INTPOOL['extra'][:left]
    res = [x for x in res if minint <= x <= maxint]
    left = number - len(res)
    while left > 0:
        res += [gmpy.rand('next', maxint - minint) + gmpy.mpz(minint)]
        left -= 1
    return res

def getstrings(number=1, maxlength = 255):
    """Returns a list of partly random strings
    
    The list starts with the numbers from STRPOOL['mandatory'], continues
    with STRPOOL['extra'] and finishes with random strings.
    
    Parameters
    ----------
    number: int, defaults to RES_LEN (1000)
    \tLength of list
    maxlength: int, defaults to 255
    \tCaps long list lengths
    
    """
    
    def _get_randchar():
        """Returns random 8 bit character"""
        
        character = None
        while character is None or character == '\n':
            character = chr(gmpy.rand('next', 255))
        
        return character
    
    res = STRPOOL['mandatory'][:number]
    while '\n' in res:
        res.remove('\n')
    
    left = number - len(res)
    if left > 0:
        res += STRPOOL['extra'][:left]
    left = number - len(res)
    
    while left > 0:
        stringlength = gmpy.rand('next', maxlength)
        randstring = "".join(_get_randchar() for i in xrange(stringlength))
        res += []
        left -= 1
    
    return res
