import wx.grid

class MainGridTable(wx.grid.PyGridTableBase):
    """Table base class that handles interaction between MainGrid and pysgrid"""
    
    def __init__(self, grid):
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

