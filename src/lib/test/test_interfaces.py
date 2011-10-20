#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit test for _interfaces.py"""

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

import types

import gmpy
import numpy

import wx

app= wx.App()

import _pyspread._interfaces as _interfaces
import vartypes as v

gmpy.rand('seed', 2)


class Test(object):
    """Test of free functions"""
    
   
    def test_sorted_keys(self):
        keys = [(1, 0, 0), (2, 0, 0), (0, 1, 0), (0, 99, 0), (0, 0, 0), 
                (0, 0, 99), (1, 2, 3)]
        assert list(_interfaces.sorted_keys(keys, (0, 1, 0))) == \
             [(0, 1, 0), (0, 99, 0), (1, 2, 3), (0, 0, 99), (0, 0, 0), 
              (1, 0, 0), (2, 0, 0)]
        sk = list(_interfaces.sorted_keys(keys, (0, 3, 0), reverse=True))
        assert sk == [(0, 1, 0), (2, 0, 0), (1, 0, 0), (0, 0, 0), (0, 0, 99), 
              (1, 2, 3), (0, 99, 0)]

    def test_sniff(self):
        """csv import sniffer"""
  
        dialect, header = _interfaces.sniff("test/BUG2037662.csv")
        assert not header
        assert dialect.delimiter == ','
        assert dialect.doublequote == 0
        assert dialect.quoting == 0
        assert dialect.quotechar == '"'
        assert dialect.lineterminator == "\r\n"
        assert dialect.skipinitialspace == 0
    
    def test_fill_wxgrid(self):
        """Fill the target with values from an array"""
        
        pass

    def test_is_pyme_present(self):
        pass
        
    def test_genkey(self):
        pass
        
    def test_sign(self):
        pass
        
    def test_verify(self):
        pass
        
    def test_get_font_from_data(self):
        pass
        
    def test_get_pen_from_data(self):
        pass
        
    def test_get_font_list(self):
        pass
        

def test_string_match():
    """Test of string_match function"""
    
    test_strings = ["", "Hello", " Hello", "Hello ", " Hello ", "Hello\n",
                    "THelloT", " HelloT", "THello ", "hello", "HELLO", "sd"]
                    
    search_string = "Hello"
    
    # Normal search
    flags = []
    results = [None, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, None]
    for test_string, result in zip(test_strings, results):
        assert _interfaces.string_match(test_string, search_string, flags) \
               == result
    
    flags = ["MATCH_CASE"]
    results = [None, 0, 1, 0, 1, 0, 1, 1, 1, None, None, None]
    for test_string, result in zip(test_strings, results):
        assert _interfaces.string_match(test_string, search_string, flags) \
               == result
    
    flags = ["WHOLE_WORD"]
    results = [None, 0, 1, 0, 1, 0, None, None, None, 0, 0, None]
    for test_string, result in zip(test_strings, results):
        assert _interfaces.string_match(test_string, search_string, flags) \
               == result

class TestClipboard(object):
    """Unit test class for Clipboard"""

    def setup_method(self, method):
        """???"""
        
        pass
        
    def test_convert_clipboard(self):
        """Test for ."""
        
        pass
    
    def test_get_clipboard(self):
        """Test for ."""
        
        pass
    
    def test_set_clipboard(self):
        """Test for ."""
        
        pass
    
    
class TestCommandline(object):
    """Unit test class for Commandline"""
    
    def setup_method(self, method):
        """???"""
        
        pass
        
    def test_init(self):
        """Test for ."""
        
        pass
    
    def test_parse(self):
        """Test for ."""
        
        pass
    
