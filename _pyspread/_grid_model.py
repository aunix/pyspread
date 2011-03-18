import wx.grid

from _pyspread._datastructures import PyspreadGrid

class MainGridTable(wx.grid.PyGridTableBase):
    """Table base class that handles interaction between MainGrid and model"""
    
    def __init__(self, grid, model):
        self.grid = grid
        self.pysgrid = grid.pysgrid
        
        wx.grid.PyGridTableBase.__init__(self)
        
        # we need to store the row length and column length to
        # see if the table has changed size
        self._rows = self.GetNumberRows()
        self._cols = self.GetNumberCols()
    
    def GetNumberRows(self):
        """Return the number of rows in the grid"""
        
        return self.pysgrid.shape[0]
    
    def GetNumberCols(self):
        """Return the number of columns in the grid"""
        
        return self.pysgrid.shape[1]
    
    def GetRowLabelValue(self, row):
        """Returns row number"""
        
        return str(row)
    
    def GetColLabelValue(self, col):
        """Returns column number"""
        
        return str(col)
    
    def GetSource(self, row, col, table=None):
        """Return the source string of a cell"""
        
        if table is None:
            table = self.grid.current_table
            
        value = self.pysgrid.sgrid[row, col, table]
        
        if value is None:
            return u""
        else:
            return value

    def GetValue(self, row, col, table=None):
        """Return the result value of a cell"""
        
        if table is None:
            table = self.grid.current_table
        
        value = self.pysgrid[row, col, table]
        
        if value is None:
            return u""
        else:
            return value
    
    def SetValue(self, row, col, value, refresh=True):
        """Set the value of a cell"""
        
        self.pysgrid[row, col, self.grid.current_table] = value
        
    def UpdateValues(self):
        """Update all displayed values"""
        
        # This sends an event to the grid table 
        # to update all of the values
        
        msg = wx.grid.GridTableMessage(self, 
                wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        self.grid.ProcessTableMessage(msg)

    def ResetView(self):
        """
        (Grid) -> Reset the grid view.   Call this to
        update the grid if rows and columns have been added or deleted
        
        """
        
        grid = self.grid
        
        grid.BeginBatch()

        for current, new, delmsg, addmsg in [
            (self._rows, self.GetNumberRows(), 
             wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, 
             wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED),
            (self._cols, self.GetNumberCols(), 
             wx.grid.GRIDTABLE_NOTIFY_COLS_DELETED, 
             wx.grid.GRIDTABLE_NOTIFY_COLS_APPENDED),
        ]:

            if new < current:
                msg = wx.grid.GridTableMessage(self, delmsg, new, current-new)
                grid.ProcessTableMessage(msg)
            elif new > current:
                msg = wx.grid.GridTableMessage(self, addmsg, new-current)
                grid.ProcessTableMessage(msg)
                self.UpdateValues()

        grid.EndBatch()

        self._rows = self.GetNumberRows()
        self._cols = self.GetNumberCols()

        # update the scrollbars and the displayed part 
        # of the grid
        
        grid.Freeze()
        grid.AdjustScrollbars()
        grid.ForceRefresh()
        grid.Thaw()

# end of class MainGridTable





##To be implemented


class CellTextModel(object):
    """Cell text controller prototype"""
    
    def __init__(self):
        pass
    
    def set_text_font(self, key, font):
        """Sets text font for key cell"""
        
        raise NotImplementedError
        
    def set_text_size(self, key, size):
        """Sets text font for key cell"""
        
        raise NotImplementedError
        
    def set_text_align(self, key, align):
        """Sets text font for key cell"""
        
        raise NotImplementedError    
    
    def set_text_color(self, key, color):
        """Sets text font for key cell"""
        
        raise NotImplementedError
    
    def set_text_style(self,  key, style):
        """Sets text font for key cell"""
        
        raise NotImplementedError
    
    def set_text_frozenstate(self, key, frozenstate):
        """Sets text font for key cell"""
        
        raise NotImplementedError
    
class CellBackgroundModel(object):
    """Cell background controller prototype"""

    def __init__(self):
        pass

    def set_background_color(self, key, color):
        """Sets text font for key cell"""
        
        raise NotImplementedError
    
    
class CellBorderModel(object):
    """Cell border controller prototype"""

    def __init__(self):
        pass

    def set_cell_border_color(self, key, color):
        """Sets text font for key cell"""
        
        raise NotImplementedError
        
    def set_cell_right_border_width(self, key, width):
        """Sets text font for key cell"""
        
        raise NotImplementedError

    def set_cell_lower_border_width(self, key, width):
        """Sets text font for key cell"""
        
        raise NotImplementedError


class CellAttributeModel(CellTextModel, CellBackgroundModel, 
                              CellBorderModel):
    """Cell attribute controller prototype"""

    def __init__(self):
        pass

class CellModel(CellAttributeModel):
    """Cell controller prototype"""

    def __init__(self):
        pass

    def set_cell_code(self,  key,  code):
        """Sets code for key cell"""
        
        raise NotImplementedError
        
    def delete_cell(self,  key):
        """Deletes key cell"""
        
        raise NotImplementedError


class TableRowModel(object):
    """Table row controller prototype"""

    def __init__(self):
        pass

    def set_row_height(self, row, height):
        """Sets row height"""
        
        raise NotImplementedError

    def add_rows(self, row, no_rows=1):
        """Adds no_rows rows before row, appends if row > maxrows"""
        
        raise NotImplementedError

    def delete_rows(self, row, no_rows=1):
        """Deletes no_rows rows"""
        
        raise NotImplementedError


class TableColumnModel(object):
    """Table column controller prototype"""

    def __init__(self):
        pass

    def set_col_width(self, row, width):
        """Sets column width"""
        
        raise NotImplementedError

    def add_cols(self, col, no_cols=1):
        """Adds no_cols columns before col, appends if col > maxcols"""
        
        raise NotImplementedError

    def delete_cols(self, col, no_cols=1):
        """Deletes no_cols column"""
        
        raise NotImplementedError


class TableTabModel(object):
    """Table tab controller prototype"""

    def __init__(self):
        pass

    def add_tabs(self, tab, no_tabs=1):
        """Adds no_tabs tabs before table, appends if tab > maxtabs"""
        
        raise NotImplementedError

    def delete_tabs(self, tab, no_tabs=1):
        """Deletes no_tabs tabs"""
        
        raise NotImplementedError

class TableModel(TableRowModel, TableColumnModel, 
                      TableTabModel):
    """Table controller prototype"""

    def __init__(self, model):
        pass
        
    def OnShapeChange(self, event):
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

    
class MacroModel(object):
    """Macro controller prototype"""

    def __init__(self):
        pass
        

    def set_macros(selfself, macro_string):
        """Sets macro string"""
    
        raise NotImplementedError


class MainGridModel(CellModel, TableModel, MacroModel):
    """Main grid controller prototype"""
    
    def __init__(self, parent):
        self.parent = parent
        self.pysgrid = PyspreadGrid()
        self.macros = self.pysgrid.sgrid.macros
        self.shape = self.pysgrid.shape
        
        self.frozen_cells = self.pysgrid.sgrid.frozen_cells
        
        #self.parent.Bind(EVT_GRID_SHAPE, self.OnShapeChange)
