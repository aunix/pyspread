#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit test for _grid_model.py"""

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


import wx

app = wx.App()

import _pyspread._datastructures as _datastructures
import _pyspread._grid_model as _grid_model

    
class TestCellTextModel(object):
    """Cell text controller prototype"""
    
    def setup_method(self, method):
        """Instantiates the class"""
        
        dim = 100, 10, 3
        grid = _datastructures.PyspreadGrid(dimensions=dim)
        self.model = _pyspread._grid_model.MainGridModelProto(None, grid)
    
    def test_set_text_font(self, key, font):
        """Sets text font for key cell"""
        
        self.model.set_text_font((0,0,0), "Arial")
        assert self.model.grid == {}
        
    def test_set_text_size(self, key, size):
        """Sets text font for key cell"""
        
        raise NotImplementedError
        
    def test_set_text_align(self, key, align):
        """Sets text font for key cell"""
        
        raise NotImplementedError    
    
    def test_set_text_color(self, key, color):
        """Sets text font for key cell"""
        
        raise NotImplementedError
    
    def test_set_text_style(self,  key, style):
        """Sets text font for key cell"""
        
        raise NotImplementedError
    
    def test_set_text_frozenstate(self, key, frozenstate):
        """Sets text font for key cell"""
        
        raise NotImplementedError
    
class TestCellBackgroundModel(object):
    """Cell background controller prototype"""

    def test___init__(self):
        pass

    def test_set_background_color(self, key, color):
        """Sets text font for key cell"""
        
        raise NotImplementedError
    
    
class TestCellBorderModel(object):
    """Cell border controller prototype"""

    def test___init__(self):
        pass

    def test_set_cell_border_color(self, key, color):
        """Sets text font for key cell"""
        
        raise NotImplementedError
        
    def test_set_cell_right_border_width(self, key, width):
        """Sets text font for key cell"""
        
        raise NotImplementedError

    def test_set_cell_lower_border_width(self, key, width):
        """Sets text font for key cell"""
        
        raise NotImplementedError


class TestCellAttributeModel(CellTextModel, CellBackgroundModel, 
                              CellBorderModel):
    """Cell attribute controller prototype"""

    def test___init__(self):
        pass

class TestCellModel(CellAttributeModel):
    """Cell controller prototype"""

    def test___init__(self):
        pass

    def test_set_cell_code(self,  key,  code):
        """Sets code for key cell"""
        
        raise NotImplementedError
        
    def test_delete_cell(self,  key):
        """Deletes key cell"""
        
        raise NotImplementedError


class TestTableRowModel(object):
    """Table row controller prototype"""

    def test___init__(self):
        pass

    def test_set_row_height(self, row, height):
        """Sets row height"""
        
        raise NotImplementedError

    def test_add_rows(self, row, no_rows=1):
        """Adds no_rows rows before row, appends if row > maxrows"""
        
        raise NotImplementedError

    def test_delete_rows(self, row, no_rows=1):
        """Deletes no_rows rows"""
        
        raise NotImplementedError


class TestTableColumnModel(object):
    """Table column controller prototype"""

    def test___init__(self):
        pass

    def test_set_col_width(self, row, width):
        """Sets column width"""
        
        raise NotImplementedError

    def test_add_cols(self, col, no_cols=1):
        """Adds no_cols columns before col, appends if col > maxcols"""
        
        raise NotImplementedError

    def test_delete_cols(self, col, no_cols=1):
        """Deletes no_cols column"""
        
        raise NotImplementedError


class TestTableTabModel(object):
    """Table tab controller prototype"""

    def test___init__(self):
        pass

    def test_add_tabs(self, tab, no_tabs=1):
        """Adds no_tabs tabs before table, appends if tab > maxtabs"""
        
        raise NotImplementedError

    def test_delete_tabs(self, tab, no_tabs=1):
        """Deletes no_tabs tabs"""
        
        raise NotImplementedError

class TestTableModel(TableRowModel, TableColumnModel, 
                      TableTabModel):
    """Table controller prototype"""

    def test___init__(self, model):
        pass
        
    def test_OnShapeChange(self, event):
        """Grid shape change event handler"""
        
        new_rows, new_cols, new_tabs = event.shape
        old_rows, old_cols, old_tabs = self.pysgrid.shape
        
        if new_rows > old_rows:
            self.add_rows(old_rows, new_rows - old_rows)
        elif new_rows < old_rows:
            self.delete_rows(old_rows, old_rows - new_rows)
        
        if new_cols > old_cols:
            self.add_cols(old_cols, new_cols - old_cols)
        elif new_cols < old_cols:
            self.delete_cols(old_cols, old_cols - new_cols)
            
        if new_tabs > old_tabs:
            self.add_tabs(old_tabs, new_tabs - old_tabs)
        elif new_tabs < old_tabs:
            self.delete_tabs(old_tabs, old_tabs - new_tabs)
        
        self.pysgrid.shape = new_rows, new_cols, new_tabs
        
        event.Skip()

    
class TestMacroModel(object):
    """Macro controller prototype"""

    def test___init__(self):
        pass
        

    def test_set_macros(selfself, macro_string):
        """Sets macro string"""
    
        raise NotImplementedError


class TestMainGridModelProto(CellModel, TableModel, MacroModel):
    """Main grid controller prototype"""
    
    def test___init__(self, parent, grid):
        self.parent = parent
        self.grid = grid
        self.pysgrid = grid.pysgrid
        self.macros = grid.pysgrid.sgrid.macros
        self.shape = grid.pysgrid.shape
        
        self.frozen_cells = self.pysgrid.sgrid.frozen_cells
        
        self.load = grid.loadfile
        self.save = grid.savefile
        
        self.parent.Bind(EVT_GRID_SHAPE, self.OnShapeChange)
