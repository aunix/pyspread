#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2008 Martin Manns
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

Model
=====

The model contains the core data structures of pyspread.
It is divided into layers.

Layer 3: CodeArray
Layer 2: DataArray
Layer 1: DictGrid
Layer 0: KeyValueStore

"""

import ast
from copy import copy
import cStringIO
from itertools import imap, product
import sys
from types import SliceType

import numpy

import wx

from lib._interfaces import sorted_keys, string_match
from lib.irange import slice_range
from lib.typechecks import is_slice_like, is_string_like, is_generator_like
from lib.selection import Selection

from unredo import UnRedo

class KeyValueStore(dict):
    """Key-Value store in memory. Currently a dict with default value None.
    
    This class represents layer 0 of the model.
    
    """
    
    def __missing__(self, value):
        """Returns the default value None"""
        
        return
        
# End of class KeyValueStore

# ------------------------------------------------------------------------------

class CellAttributes(list):
    """Stores cell formatting attributes in a list of 3 - tuples
    
    The first element of each tuple is a Selection.
    The second element is the table
    The third element is a dict of attributes that are altered.
    
    The class provides attribute read access to single cells via __getitem__
    Otherwise it behaves similar to a list.
    
    Note that for the method undoable_append to work, unredo has to be
    defined as class attribute.
    
    """
    
    default_cell_attributes = {
        "borderwidth_bottom": 1,
        "borderwidth_right": 1,
        "bordercolor_bottom": wx.Colour(200, 200, 200).GetRGB(),
        "bordercolor_right": wx.Colour(200, 200, 200).GetRGB(),
        "bgcolor": wx.Colour(255, 255, 255).GetRGB(),
        "textfont": wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT).\
                                      GetFaceName(),
        "pointsize": 10,
        "fontweight": wx.NORMAL,
        "fontstyle": wx.NORMAL,
        "textcolor": wx.Colour(0, 0, 0).GetRGB(),
        "underline": False,
        "strikethrough": False,
        "angle": 0.0,
        "column-width": 150,
        "row-height": 26,
        "vertical_align": "top",
        "justification": "left",
        "frozen": False,
    }
    
    # Cache for __getattr__ maps key to tuple of len and attr_dict
    
    _attr_cache = {}
    
    def undoable_append(self, value):
        """Appends item to list and provides undo and redo functionality"""
        
        undo_operation = (self.pop, [])
        redo_operation = (self.undoable_append, [value])

        self.unredo.append(undo_operation, redo_operation)
        
        self.unredo.mark()
        
        self.append(value)
    
    def __getitem__(self, key):
        """Returns attribute dict for a single key"""
        
        assert not any(type(key_ele) is SliceType for key_ele in key)
        
        if key in self._attr_cache:
           cache_len, cache_dict = self._attr_cache[key]
           
           # Use cache result only if no new attrs have been defined 
           if cache_len == len(self):
               return cache_dict
        
        row, col, tab  = key
        
        result_dict = copy(self.default_cell_attributes)
        
        for selection, table, attr_dict in self:
            if tab == table and (row, col) in selection:
                result_dict.update(attr_dict)
        
        # Upddate cache with current length and dict
        self._attr_cache[key] = (len(self), result_dict)
        
        return result_dict

# End of class CellAttributes

class ParserMixin(object):
    """Provides parser methods for DictGrid"""
    
    def _split_tidy(self, string, maxsplit=None):
        """Rstrips string for \n and splits string for \t"""
        
        if maxsplit is None:
            return string.rstrip("\n").split("\t")
        else:
            return string.rstrip("\n").split("\t", maxsplit)
    
    def _get_key(self, *keystrings):
        """Returns int key tuple from key string list"""
        
        return tuple(imap(int, keystrings))
    
    def parse_to_shape(self, line):
        """Parses line and adjusts grid shape"""
        
        self.shape = self._get_key(*self._split_tidy(line))

    def parse_to_grid(self, line):
        """Parses line and inserts grid data"""
        
        row, col, tab, code = self._split_tidy(line, maxsplit=3)
        key = self._get_key(row, col, tab)
        
        self[key] = code
    
    def parse_to_attribute(self, line):
        """Parses line and appends cell attribute"""
        
        splitline = self._split_tidy(line)
        
        selection_data = map(ast.literal_eval, splitline[:5])
        selection = Selection(*selection_data)
        
        tab = int(splitline[5])
        
        attrs = {}
        for col, ele in enumerate(splitline[6:]):
            if col % 2:
                # Even cols are values
                attrs[key] = ast.literal_eval(ele)
                
            else:
                # Odd entries are keys
                key = ast.literal_eval(ele)
                
        self.cell_attributes.append((selection, tab, attrs))


    def parse_to_height(self, line):
        """Parses line and inserts row hight"""
        
        # Split with maxsplit 3
        row, tab, height = self._split_tidy(line)
        key = self._get_key(row, tab)
        
        self.row_heights[key] = float(height)
        

    def parse_to_width(self, line):
        """Parses line and inserts column width"""
        
        # Split with maxsplit 3
        col, tab, width = self._split_tidy(line)
        key = self._get_key(col, tab)
        
        self.col_widths[key] = float(width)
        
    def parse_to_macro(self, line):
        """Appends line to macro"""
        
        self.macros += line

# End of class ParserMixin


class StringGeneratorMixin(object):
    """String generation methods for DictGrid"""
    
    def grid_to_strings(self):
        """Yields a string that represents the grid content for saving
        
        Format
        ------
        [shape]
        rows\tcols\ttabs\n
        [grid]
        row\tcol\ttab\tcode\n
        row\tcol\ttab\tcode\n
        ...
        
        """
        
        yield u"[shape]\n"
        yield u"\t".join(map(unicode, self.shape)) + u"\n"
        
        yield u"[grid]\n"
        
        for key in self:
            yield u"\t".join([repr(ele) for ele in key] + [self[key]]) + "\n"
    


    def attributes_to_strings(self):
        """Yields a string that represents the cell attributes for saving
        
        Format
        ------
        
        [attributes]
        selection[0]\t...\tselection[5]\ttab\tkey\tvalue\t...\tkey\tvalue\n
        ...
        
        """
        
        yield u"[attributes]\n"
        
        for selection, tab, attr_dict in self.cell_attributes:
            sel_list = [selection.block_tl, selection.block_br, 
                        selection.rows, selection.cols, selection.cells]
                        
            tab_list = [tab]
            
            attr_dict_list = []
            for key in attr_dict:
                attr_dict_list.append(key)
                attr_dict_list.append(attr_dict[key])
                
            line_list = map(repr, sel_list + tab_list + attr_dict_list)
            
            yield u"\t".join(line_list) + u"\n"
            
            
    def heights_to_strings(self):
        """Yields a string that represents the row heights for saving
        
        Format
        ------
        
        [row_heights]
        row\ttab\tvalue\n
        ...
        
        """
        
        yield u"[row_heights]\n"
        
        for row, tab in self.row_heights:
            height_strings = map(repr, [row, tab, self.row_heights[(row, tab)]])
            yield u"\t".join(height_strings) + u"\n"


    def widths_to_strings(self):
        """Yields a string that represents the column widths for saving
        
        Format
        ------
        
        [col_widths]
        col\ttab\tvalue\n
        ...
        
        """
        
        yield u"[col_widths]\n"
        
        for col, tab in self.col_widths:
            width_strings = map(repr, [col, tab, self.col_widths[(col, tab)]])
            yield u"\t".join(width_strings) + u"\n"
      
    def macros_to_strings(self):
        """Yields a string that represents the content for saving
        
        Format
        ------
        
        [macros]
        Macro code
        
        """
        
        yield u"[macros]\n"
        
        for line in self.macros.split("\n"):
            yield line + u"\n"

# End of class StringGeneratorMixin

class DictGrid(KeyValueStore, ParserMixin, StringGeneratorMixin):
    """The core data class with all information that is stored in a pys file.
    
    Besides grid code access via standard dict operations, it provides 
    the following attributes:
    
    * cell_attributes: Stores cell formatting attributes
    * macros:          String of all macros
    
    This class represents layer 1 of the model.
    
    Parameters
    ----------
    shape: n-tuple of integer
    \tShape of the grid
    
    """
       
    def __init__(self, shape):
        KeyValueStore.__init__(self)
        
        self.shape = shape
        
        self.cell_attributes = CellAttributes()
        
        self.macros = u""
        
        self.row_heights = {} # Keys have the format (row, table)
        self.col_widths = {}  # Keys have the format (col, table)
    
    def __getitem__(self, key):
        
        shape = self.shape
        
        for axis, key_ele in enumerate(key):
            if shape[axis] <= key_ele or key_ele < -shape[axis]:
                raise IndexError, "Grid index " + \
                      str(key) + " outside grid shape " + str(shape)
        
        return KeyValueStore.__getitem__(self, key)

# End of class DictGrid

# ------------------------------------------------------------------------------

class DataArray(object):
    """DataArray provides enhanced grid read/write access.
    
    Enhancements comprise:
     * Slicing
     * Multi-dimensional operations such as insertion and deletion along 1 axis
     * Undo/redo operations
    
    This class represents layer 2 of the model.
    
    Parameters
    ----------
    shape: n-tuple of integer
    \tShape of the grid
    
    """
    
    def __init__(self, shape):
        self.dict_grid = DictGrid(shape)
    
        # Undo and redo management
        self.unredo = UnRedo()
        self.dict_grid.cell_attributes.unredo = self.unredo
        
        # Safe mode
        self.safe_mode = False
    
    # Row and column attributes mask
    # Keys have the format (row, table)
    
    @property
    def row_heights(self):
        return self.dict_grid.row_heights 
    
    @property
    def col_widths(self):
        return self.dict_grid.col_widths  
    
    # Cell attributes mask
    @property
    def cell_attributes(self):
        return self.dict_grid.cell_attributes
    
    def __iter__(self):
        """returns iterator over self.dict_grid"""
        
        return iter(self.dict_grid)
    
    def _get_macros(self):
        return self.dict_grid.macros

    def _set_macros(self, macros):
        self.dict_grid.macros = macros
        
    macros = property(_get_macros, _set_macros)

    def keys(self):
        """Returns keys in self.dict_grid"""
        
        return self.dict_grid.keys()
    
    def pop(self, key):
        """Pops dict_grid with undo and redo support"""
        
        # UnRedo support
        
        try:
            undo_operation = (self.__setitem__, [key, self.dict_grid[key]])
            redo_operation = (self.pop, [key])

            self.unredo.append(undo_operation, redo_operation)
            
            self.unredo.mark()
            
        except KeyError:
            # If key not present then unredo is not necessary
            pass
            
        # End UnRedo support
        
        return self.dict_grid.pop(key)
    
    # Shape mask
    
    def _get_shape(self):
        """Returns dict_grid shape"""
        
        return self.dict_grid.shape
        
    def _set_shape(self, shape):
        """Deletes all cells beyond new shape and sets dict_grid shape"""
        
        # Delete each cell that is beyond new borders
        
        old_shape = self.shape
        
        if any(new_axis < old_axis 
               for new_axis, old_axis in zip(shape, old_shape)):
            for key in self.dict_grid.keys():
                if any(key_ele >= new_axis 
                       for key_ele, new_axis in zip(key, shape)):
                    self.pop(key)
        
        # Set dict_grid shape attribute
        
        self.dict_grid.shape = shape
        
        # UnRedo support
        
        undo_operation = (setattr, [self.dict_grid, "shape", old_shape])
        redo_operation = (setattr, [self.dict_grid, "shape", shape])

        self.unredo.append(undo_operation, redo_operation)
            
        self.unredo.mark()
    
        # End UnRedo support

    shape = property(_get_shape, _set_shape)

    # Pickle support
    
    def __getstate__(self):
        """Returns dict_grid for pickling
        
        Note that all persistent data is contained in the DictGrid class
        
        """
        
        return {"dict_grid": self.dict_grid}
    
    # Slice support
       
    def __getitem__(self, key):
        """Adds slicing access to cell code retrieval
        
        The cells are returned as a generator of generators, of ... of unicode.
        
        Parameters
        ----------
        key: n-tuple of integer or slice
        \tKeys of the cell code that is returned
        
        Note
        ----
        Classical Excel type addressing (A$1, ...) may be added here
        
        """
        
        for key_ele in key:
            if is_slice_like(key_ele):
                # We have something slice-like here 
                
                return self.cell_array_generator(key)
                
            elif is_string_like(key_ele):
                # We have something string-like here 
                
                raise NotImplementedError, \
                      "Cell string based access not implemented"
                
        # key_ele should be a single cell
        
        return self.dict_grid[key]
    
    def __str__(self):
        return self.dict_grid.__str__()
    
    def __setitem__(self, key, value):
        """Accepts index and slice keys"""
        
        single_keys_per_dim = []
        
        for axis, key_ele in enumerate(key):
            if is_slice_like(key_ele):
                # We have something slice-like here 
                
                single_keys_per_dim.append(slice_range(key_ele, 
                                                       length = key[axis]))
                
            elif is_string_like(key_ele):
                # We have something string-like here 
                
                raise NotImplementedError
            
            else:
                # key_ele is a single cell
                
                single_keys_per_dim.append((key_ele, ))
        
        single_keys = product(*single_keys_per_dim)
        
        unredo_mark = False
        
        for single_key in single_keys:
            if value:
                # UnRedo support
                
                old_value = self(key)
                
                # We seem to have double calls on __setitem__
                # This hack catches them
                
                if old_value != value:
                
                    unredo_mark = True
                
                    undo_operation = (self.__setitem__, [key, old_value])
                    redo_operation = (self.__setitem__, [key, value])
        
                    self.unredo.append(undo_operation, redo_operation)
                    
                    # End UnRedo support
                
                self.dict_grid[single_key] = value
            else:
                # Value is empty --> delete cell
                try:
                    self.dict_grid.pop(key)
                    
                except (KeyError, TypeError):
                    pass
                    
        if unredo_mark:
            self.unredo.mark()
    
    def cell_array_generator(self, key):
        """Generator traversing cells specified in key
        
        Parameters
        ----------
        key: Iterable of Integer or slice
        \tThe key specifies the cell keys of the generator
        
        """
        
        for i, key_ele in enumerate(key):
            
            # Get first element of key that is a slice
            
            if type(key_ele) is SliceType:
                slc_keys = slice_range(key_ele, self.dict_grid.shape[i])
                
                key_list = list(key)
                
                key_list[i] = None
                
                has_subslice = any(type(ele) is SliceType for ele in key_list)
                                            
                for slc_key in slc_keys:
                    key_list[i] = slc_key
                    
                    if has_subslice:
                        # If there is a slice left yield generator
                        yield self.cell_array_generator(key_list)
                        
                    else:
                        # No slices? Yield value
                        yield self[tuple(key_list)]
                    
                break
    
    def _adjust_shape(self, amount, axis):
        """Changes shape along axis by amount"""

        new_shape = list(self.shape)
        new_shape[axis] += amount
        
        self.shape = tuple(new_shape)
    
    def insert(self, insertion_point, no_to_insert, axis):
        """Inserts no_to_insert rows/cols/tabs/... before insertion_point
        
        Parameters
        ----------
        
        insertion_point: Integer
        \tPont on axis, before which insertion takes place
        no_to_insert: Integer >= 0
        \tNumber of rows/cols/tabs that shall be inserted
        axis: Integer
        \tSpecifies number of dimension, i.e. 0 == row, 1 == col, ...
        
        """
        
        if not 0 <= axis <= len(self.shape):
            raise ValueError, "Axis not in grid dimensions"
        
        if insertion_point > self.shape[axis] or \
           insertion_point <= -self.shape[axis]:
            raise IndexError, "Insertion point not in grid"
        
        new_keys = {}
        
        for key in copy(self.dict_grid):
            if key[axis] >= insertion_point:
                new_key = list(key)
                new_key[axis] += no_to_insert
                
                new_keys[tuple(new_key)] = self.pop(key)
        
        self._adjust_shape(no_to_insert, axis)
        
        for key in new_keys:
            self[key] = new_keys[key]
        
    def delete(self, deletion_point, no_to_delete, axis):
        """Deletes no_to_delete rows/cols/tabs/... starting with deletion_point
        
        Axis specifies number of dimension, i.e. 0 == row, 1 == col, ...
        
        """
        
        if no_to_delete < 0:
            raise ValueError, "Cannot delete negative number of rows/cols/..."
        
        if not 0 <= axis <= len(self.shape):
            raise ValueError, "Axis not in grid dimensions"
        
        if deletion_point > self.shape[axis] or \
           deletion_point <= -self.shape[axis]:
            raise IndexError, "Deletion point not in grid"
        
        
        for key in copy(self.dict_grid):
            if deletion_point <= key[axis] < deletion_point + no_to_delete:
                self[key] = self.pop(key)
            
            elif key[axis] >= deletion_point + no_to_delete:
                new_key = list(key)
                new_key[axis] -= no_to_delete
                
                self[tuple(new_key)] = self.pop(key)

        self._adjust_shape(-no_to_delete, axis)

    # Element access via call
    
    __call__ = __getitem__

# End of class DataArray

# ------------------------------------------------------------------------------

class CodeArray(DataArray):
    """CodeArray provides objects when accessing cells via __getitem__
    
    Cell code can be accessed via function call
    
    This class represents layer 3 of the model.
    
    """
    
    operators = ["+", "-", "*", "**", "/", "//",
             "%", "<<", ">>", "&", "|", "^", "~",
             "<", ">", "<=", ">=", "==", "!=", "<>",
            ]
    
    # Cache for results from __getitem calls
    result_cache = {}
    
    def __setitem__(self, key, value):
        """Sets cell code and resets result cache"""
        
        DataArray.__setitem__(self, key, value)
        
        # Reset result cache
        self.result_cache = {} 
    
    def __getitem__(self, key):
        """Returns _eval_cell"""
        
        # Frozen cell handling
        if all(type(k) is not SliceType for k in key):
            frozen_res = self.cell_attributes[key]["frozen"]
            if frozen_res is not False:
                return frozen_res
        
        # Normal cell handling
        
        if repr(key) in self.result_cache:
            return self.result_cache[repr(key)]
            
        else:
            result = self._eval_cell(key)
            
            if self(key) is not None:
                self.result_cache[repr(key)] = result
            
            return result
    
    def _make_nested_list(self, gen):
        """Makes nested list from generator for creating numpy.array"""
        
        res = []
        
        for ele in gen:
            if ele is None:
                res.append(None)
                
            elif is_string_like(ele):
                # String
                res.append(ele)
                
            elif is_generator_like(ele):
                # Nested generator
                res.append(self._make_nested_list(ele))
                
            else:
                res.append(ele)
        
        return res
    
    def _has_assignment(self, code):
        """Returns True iif  code is a global assignment
        
        Assignment is valid iif 
         * only one term in front of "=" and 
         * no "==" and 
         * no operators left and 
         * parentheses balanced
         
        """
        
        return len(code) > 1 and \
               len(code[0].split()) == 1 and \
               code[1] != "" and \
               (not max(op in code[0] for op in self.operators)) and \
               code[0].count("(") == code[0].count(")")
    
    def _eval_cell(self, key):
        """Evaluates one cell"""
        
        # Set up environment for evaluation
        env = globals().copy()
        env.update( {'X':key[0], 'Y':key[1], 'Z':key[2],
                     'R':key[0], 'C':key[1], 'T':key[2],
                     'S':self } )
        
        code = self(key)
        
        # If cell is not present return None
        
        if code is None:
            return
        
        
        elif is_generator_like(code):
            # We have a generator object
            
            return numpy.array(self._make_nested_list(code))
        
        # If only 1 term in front of the "=" --> global
        
        split_exp = code.split("=")
        
        if self._has_assignment(split_exp):
            glob_var = split_exp[0].strip()
            expression = "=".join(split_exp[1:])
        else:
            glob_var = None
            expression = code
        
        try:
            result = eval(expression, env, {})
            
        except AttributeError, err:
            # Attribute Error includes RunTimeError
            result = err 
            
        except Exception, err:
            result = Exception(err)
        
        # Change back cell value for evaluation from other cells
        self.dict_grid[key] = code
        
        if glob_var is not None:
            globals().update({glob_var: result})
        
        return result
    
    def execute_macros(self):
        """Executes all macros and returns result string if not safe_mode"""
        
        if self.safe_mode:
            return "Safe mode activated. Code not executed."
        
        # Windows exec does not like Windows newline
        self.macros = self.macros.replace('\r\n', '\n')
        
        # Create file-like string to capture output
        code_out = cStringIO.StringIO()
        code_err = cStringIO.StringIO()

        # Capture output and errors
        sys.stdout = code_out
        sys.stderr = code_err

        try:
            exec(self.macros, globals())
            
        except Exception, err:
            print err

        # Restore stdout and stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        outstring = code_out.getvalue() + code_err.getvalue()

        code_out.close()
        code_err.close()

        return outstring
    
    def findnextmatch(self, startkey, find_string, flags):
        """ Returns a tuple with the position of the next match of find_string
        
        Returns None if string not found.
        
        Parameters:
        -----------
        startkey:   Start position of search
        find_string:String to be searched for
        flags:      List of strings, out ouf 
                    ["UP" xor "DOWN", "WHOLE_WORD", "MATCH_CASE", "REG_EXP"]
        
        """
        
        assert "UP" in flags or "DOWN" in flags
        assert not ("UP" in flags and "DOWN" in flags)
        
        # List of keys in sgrid in search order
        
        reverse = "UP" in flags
        
        for key in sorted_keys(self.keys(), startkey, reverse=reverse):
            code = self(key)
            res_str = unicode(self[key])
            
            if string_match(code, find_string, flags) is not None or \
               string_match(res_str, find_string, flags) is not None:
                return key
    
# End of class CodeArray


