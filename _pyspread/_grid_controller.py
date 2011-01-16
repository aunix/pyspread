from itertools import izip

import string

import numpy

import wx.grid

from _pyspread._widgets import EntryLine
from _pyspread._interfaces import Clipboard


# Grid level input
# ----------------


class GridSelectionMask(object):
    """incl. insert and delete, {"rows": [], "cols":[], "tabs":[]}"""
    def __init__(self, grid):
        self.grid = grid
        
    def __call__(self):
        """Returns list of row, col, tab tuples of selection"""
        
        return self.grid.get_selection()
        
    def __getitem__(self, axis):
        """Returns set of selected rows or cols for axis in [0, 1]
        
        Returns set of current tables for axis == 2
        
        """
        
        assert axis in xrange(3)
        
        if axis == 2:
            return set([self.grid.current_table])
        
        return set(c[axis] for c in self.grid.get_selection())
    
    def _get_selected_rows_cols(self, axis):
        """Returns tuple of current insertion position and selected rows"""
        selected_rowcols = self[axis]
        current_rowcol = min(selected_rowcols)
        no_selected_rowcols = max(1, len(selected_rowcols))
        
        return current_rowcol, no_selected_rowcols
        
    def insert(self, axis):
        """Inserts the number of selected rows/cols/tabs before cursor
        
        If axis == 0, the number of selected rows is inserted.
        If axis == 1, the number of selected cols is inserted.
        If axis == 2, one table is inserted.
        
        """
        
        rowcol, no_ins = self._get_selected_rows_cols(axis)
        if axis == 0:
            self.grid.insert_rows(rowcol, no_ins)
        elif axis == 1:
            self.grid.insert_cols(rowcol, no_ins)
        elif axis ==2:
            self.grid.insert_tables(rowcol)
        else:
            raise ValueError, "axis must be in [0, 1, 2]."
            
    def delete(self, axis):
        """Deletes the number of selected rows/cols/tabs starting at cursor
        
        If axis == 0, the number of selected rows is deleted.
        If axis == 1, the number of selected cols is deleted.
        If axis == 2, one table is deleted.
        
        """
        
        rowcol, no_del = self._get_selected_rows_cols(axis)
        if axis == 0:
            self.grid.delete_rows(rowcol, no_del)
        elif axis == 1:
            self.grid.delete_cols(rowcol, no_del)
        elif axis ==2:
            self.grid.delete_tables(rowcol)
        else:
            raise ValueError, "axis must be in [0, 1, 2]."

class GridSelectionMixin(object):
    """Easy selection support extension class for wx.grid.Grid
    
    Public methods:
    ---------------
    get_selected_rows_cols
    get_selection
    get_selection_code
    get_currentcell
    get_visiblecell_slice
    getselectiondata
    selection_replace
    selectnewcell
    delete
    
    """
    
    def get_selected_rows_cols(self, selection = None):
        """ Get the slices of selected rows and cols, None if no selection """
        if selection is None:
            selection = self.get_selection()
        try:
            rowslice = slice(min(c[0] for c in selection), \
                             max(c[0] for c in selection) + 1)
        except IndexError:
            rowslice = None
        try: 
            colslice = slice(min(c[1] for c in selection), \
                             max(c[1] for c in selection) + 1)
        except IndexError: 
            colslice = None
        return rowslice, colslice
    
    def get_selection(self):
        """ Returns an index list of all cells that are selected in the grid.
        All selection types are considered equal. If no cells are selected,
        the current cell is returned."""
                
        # GetSelectedCells: individual cells selected by ctrl-clicking
        # GetSelectedRows: rows selected by clicking on the labels
        # GetSelectedCols: cols selected by clicking on the labels
        # GetSelectionBlockTopLeft
        # GetSelectionBlockBottomRight: For blocks of cells selected by dragging
        # across the grid cells.
              
        dimx, dimy = self.pysgrid.sgrid.shape[:2]
        
        selected_rows = self.GetSelectedRows()
        selected_cols = self.GetSelectedCols()
        
        selection = []
        selection += self.GetSelectedCells()
        selection += list((row, y) \
                          for row in selected_rows for y in xrange(dimy))
        selection += list((x, col) \
                          for col in selected_cols for x in xrange(dimx))
        
        selectionblock = izip(self.GetSelectionBlockTopLeft(), \
                              self.GetSelectionBlockBottomRight())
        for topleft, bottomright in selectionblock:
            selection += [(x, y) for x in xrange(topleft[0], bottomright[0]+1) \
                                 for y in xrange(topleft[1], bottomright[1]+1)]
        
        if selection == []:
            selection = [(self.get_currentcell())]
        selection = sorted(list(set(selection)))
        
        return selection
    
    def get_selection_code(self):
        """Returns code for accessing the current selection from a cell"""

        selection = self.get_selection()
        
        # If only one cell is selected return the representation
        
        if len(selection) == 1:
            return "S[%d, %d, %d]" % \
                (selection[0][0], selection[0][1], self.current_table)

        # Check if selection is rectangular
        min_x = min(x for x, y in selection)
        max_x = max(x for x, y in selection) + 1
        min_y = min(y for x, y in selection)
        max_y = max(y for x, y in selection) + 1

        rect = [(x, y) for x in xrange(min_x, max_x) \
                       for y in xrange(min_y, max_y)]

        if set(selection) == set(rect):
            # If a rectangular set is selected return slice
            
            code = "S[%d:%d, %d:%d, %d]" % (min_x, max_x, 
                    min_y, max_y, self.current_table)
        else:
            # If a non-rectangular set is selected return list comprehension
            code = "[S[x, y, " + repr(self.current_table) + \
                   "] for x, y in " + repr(selection) + "]"
        
        return code

    
    def get_currentcell(self):
        """Get cursor position"""
        
        row = self.GetGridCursorRow()
        col = self.GetGridCursorCol()
        return row, col
    
    def get_visiblecell_slice(self):
        """Returns a tuple of 3 slices that contains the visible cells"""
        
        topleft_x = self.YToRow(self.GetViewStart()[1] * self.ScrollLineX)
        topleft_y = self.XToCol(self.GetViewStart()[0] * self.ScrollLineY)
        topleft = (topleft_x, topleft_y)
        row, col = topleft_x + 1, topleft_y + 1 # Ensures visibility
        
        while self.IsVisible(row, topleft[1], wholeCellVisible=False):
            row += 1
        while self.IsVisible(topleft[0], col, wholeCellVisible=False):
            col += 1
        lowerright = (row, col) # This cell is *not* visible
        return (slice(topleft[0], lowerright[0]), \
                slice(topleft[1], lowerright[1]), 
                slice(self.current_table, self.current_table+1))
    
    def getselectiondata(self, source, rowslice, colslice, \
                         selection=None, omittedfield_repr = '\b'):
        """
        Returns 2D source data array that matches the current selection
        
        Parameters:
        -----------
        source: Object
        \t Source of the data, sliceable in >= 2 dimensions
        
        rowslice: Slice
        \tRows to be retrieved
        
        colslice: Slice
        \tColumns to be retrieved
        
        selection: List
        \tRepresents selected cells in data
        
        omittedfield_repr: String
        \tRepresents empty cells and those cells that are printed but not
        \tselected if selection not None
        
        """
        
        getter = source.__getitem__
        
        try:
            data = numpy.array( \
                    getter((rowslice, colslice, self.current_table)).copy(), \
                    dtype="O")
        except AttributeError:
            data = numpy.array( \
                    getter((rowslice, colslice, self.current_table)), \
                    dtype="O")
        if len(data.shape) == 1:
            data = data.reshape((data.shape[0], 1))
            if sum(1 for _ in irange(rowslice.start, rowslice.stop)) == 1:
                data = numpy.transpose(data)
            
        try:
            len(data)
        except TypeError:
            return self.digest(source[rowslice, colslice, self.current_table])
        
        for row in xrange(len(data)):
            try:
                datarange = xrange(len(data[row]))
            except TypeError:
                return data
            for col in datarange:
                try:
                    if (row + rowslice.start, col + colslice.start) \
                          not in selection:
                        data[row, col] = omittedfield_repr
                except TypeError:
                    if selection is None:
                        pass
                
                key = (row + rowslice.start, col + colslice.start, 
                      self.current_table)
                                    
                if hasattr(source, 'sgrid') and source.sgrid[key] == 0  or \
                   data[row, col] is None:
                    try:
                        data[row, col] = omittedfield_repr
                    except IndexError:
                        data[row] = omittedfield_repr
                    except IndexError:
                        data[col] = omittedfield_repr
        return data
    
    def selection_replace(self, editor, data):
        """ Replaces a selection in a TextCtrl with inserted data"""
        
        ##*** This should be moved into a custom TextCtrl class ***
        inspoint = int(editor.InsertionPoint)
        sel_begin, sel_end = editor.GetSelection()
        if sel_begin != sel_end and inspoint > sel_begin:
            inspoint = inspoint - \
                       min(abs(sel_end - sel_begin), abs(inspoint - sel_begin))
        oldval = editor.GetValue()[:sel_begin] + editor.GetValue()[sel_end:]
        newval = oldval[:inspoint] + data + oldval[inspoint:]
        editor.SetValue(newval)
        editor.SetInsertionPoint(inspoint + len(data))
        editor.SetSelection(inspoint, inspoint + len(data))

    def selectnewcell(self, key, event):
        """ Selects the cell with position key.
        
        Parameters:
        -----------
        key: 3-tuple
        \tPosition in grid(x,y,z)
        """
        
        if key[2] != self.current_table:
            self.cbox_z.SetSelection(key[2])
            event.GetString = lambda x = 0: self.digest(key[2])
            self.OnCombo(event)
            self.SetFocus()
        self.MakeCellVisible(*key[:2])
        self.SetGridCursor(*key[:2])
    
    def delete(self, selection=None):
        """Deletes selection"""
        
        if selection is None:
            selection = self.get_selection()
        for cell in selection:
            try:
                self.pysgrid[cell[0], cell[1], self.current_table] = u""
            except KeyError:
                #Cell is not there
                pass
        self.pysgrid.unredo.mark()
    
    def purge(self, selection=None):
        """Deletes selection including cell attributes"""
        
        if selection is None:
            selection = self.get_selection()
        for cell in selection:
            try:
                self.pysgrid.sgrid.pop((cell[0], cell[1], self.current_table))
            except KeyError:
                #Cell is not there
                pass
        self.pysgrid.unredo.mark()
        
# end of class GridSelectionMixin

class GridClipboard(object):
    """Easy clipboard support extension class for wx.grid.Grid
    
    Public methods:
    ---------------
    cut
    copy
    paste
    undo
    redo
    
    """
    
    def __init__(self, grid, model):
        self.grid = grid
        self.model = model
        
        self.clipboard = Clipboard()
    
    def cut(self):
        """Cuts TextCtrlSelection if present else cuts Grid cells
        
        Source can be sgrid or the displayed wxGrid
        
        """
        
        self.copy(source=self.model.pysgrid.sgrid)
        
        focus = self.grid.parent.FindFocus()
        
        if isinstance(focus, wx.TextCtrl):
            self.grid.selection_replace(focus, "")
        else:
            self.grid.delete()
    
    def _copy_textctrl(self, control):
        """Copies TextCtrlSelection"""
        
        selection = control.GetStringSelection()
        if selection != u"":
            self.copy_selection = []
            return selection
        else:
            return None
    
    def _copy_grid(self, source):
        """Copies Grid cells"""
        
        selection = self.grid.get_selection()
        
        rowslice, colslice = self.grid.get_selected_rows_cols(selection)
        data = self.grid.getselectiondata(source, rowslice, colslice, selection)
        
        self.grid.copy_selection = [ \
            (cell[0]-rowslice.start, cell[1]-colslice.start) \
            for cell in selection]
        
        try:
            iter(data)
            assert not isinstance(data, unicode) and \
                   not isinstance(data, basestring)
                   
        except (TypeError, AssertionError):
            return self.grid.digest(data)
        
        try:
            data[0][0]
        except (IndexError, TypeError): # Only one row
            data = [data]
        
        clipboard_data = [[]]
        for datarow in data:
            if isinstance(datarow, unicode) or isinstance(datarow, basestring):
                clipboard_data[-1].append(self.grid.digest(datarow))
            else:
                try:
                    for ele in datarow:
                        clipboard_data[-1].append(self.grid.digest(ele))
                except TypeError:
                    clipboard_data[-1].append(u"")
            clipboard_data.append([])
        
        return "\n".join("\t".join(line) for line in clipboard_data)

    
    def copy(self, source=None):
        """Copies TextCtrlSelection if present else copies Grid cells
        
        Parameters
        ----------
        source: sgrid
        
        """
        
        if source is None:
            source = self.grid.pysgrid.sgrid
            
        focus = self.grid.parent.FindFocus()
        
        if isinstance(focus, wx.TextCtrl):
            clipboard_data = self._copy_textctrl(focus)
        else:
            clipboard_data = self._copy_grid(source)
            
        if clipboard_data is not None:
            self.clipboard.set_clipboard(clipboard_data)
    
    def paste(self):
        """Pastes into TextCtrl if active else pastes to grid"""
        
        focus = self.grid.parent.FindFocus()
        if isinstance(focus, wx.TextCtrl):
            data = self.grid.clipboard.get_clipboard()
            self.selection_replace(focus, data)
        else: # We got a grid selection
            pastepos = (self.grid.GetGridCursorRow(), \
                        self.grid.GetGridCursorCol(), \
                        self.grid.current_table)
            self.clipboard.grid_paste(self.model.pysgrid, key=pastepos)
        self.grid.Freeze()
        self.grid.ForceRefresh()
        self.grid.Thaw()

# end of class GridClipboardMixin

class GridManipulationMixin(object):
    """Manipulates rows, columns and tables. Mixin for wx.grid.Grid
    
    change_dim
    insert_selected_rows
    insert_selected_cols
    insert_selected_tables
    delete_selected_rows
    delete_selected_cols
    delete_selected_tables
    
    """
    
    def change_dim(self, dimension, number):
        """
        Appends/deletes a number of rows/cols/tables to a dimension of the grid
        
        Parameters
        ----------
        
        dimension: int
        \tThe dimension at which rows/cols/tables are appended
        number: int
        \tThe number of rows that shall be appended (if > 0) or deleted (if < 0)
        
        """
        
        assert dimension in xrange(3)
        
        if number == 0:
            # Nothing to do
            return None
        
        elif number < 0:
            number = abs(number)
            delete = True
            
            # Size of target grid dimension
            size = self.pysgrid.sgrid.shape[dimension] - number
            
        else:
            delete = False
            
            # Size of source grid dimension
            size = self.pysgrid.sgrid.shape[dimension]
        
        # Append
        if dimension == 0:
            operations = \
              [(self.pysgrid.insert, [[size, None, None], number])]
            undo_operations = \
              [(self.pysgrid.remove, [[size, None, None], number])]
            
        elif dimension == 1:
            operations = \
              [(self.pysgrid.insert, [[None, size, None], number])]
            undo_operations = \
              [(self.pysgrid.remove, [[None, size, None], number])]
            
        elif dimension == 2:
            minsize = min(size, size + number)
            maxsize = max(size, size + number)
            operations = \
              [(self.pysgrid.insert, [[None, None, size], number])] + \
              [(self.cbox_z.Append, [unicode(i)]) \
                    for i in xrange(minsize, maxsize)]
            undo_operations = \
              [(self.pysgrid.remove, [[None, None, size], number])] + \
              [(self.cbox_z.Delete, [i-1]) \
                    for i in range(minsize, maxsize + 1)[::-1]]
        
        if delete:
            operations, undo_operations = undo_operations, operations
        
        for undo_operation, operation in zip(undo_operations, operations):
            operation[0](*operation[1]) # Do the operation
            self.pysgrid.unredo.append(undo_operation, operation)
        
        self.create_rowcol()
    
    def insert_rows(self, row, no_ins=1):
        """Inserts the number of rows of the imminent selection at cursor."""
        
        # Insert rows
        self.pysgrid.insert(insertionpoint=[row, None, None], notoinsert=no_ins)
        self.create_rowcol()
        self.pysgrid.unredo.mark()
    
    def insert_cols(self, col, no_ins=1):
        """Inserts the number of cols of the imminent selection at cursor."""
        
        self.pysgrid.insert(insertionpoint=[None, col, None], notoinsert=no_ins)
        self.create_rowcol()
        self.pysgrid.unredo.mark()
    
    def insert_tables(self, tab):
        """Inserts one table before the current one."""
        
        current_table = self.current_table
        no_selected_tables = 1
        operation = (self.cbox_z.Append, [unicode(self.pysgrid.shape[2])])
        undo_operation = (self.cbox_z.Delete, [self.pysgrid.shape[2]])
        self.pysgrid.unredo.append(undo_operation, operation)
        self.cbox_z.Append(unicode(self.pysgrid.shape[2]))
        self.pysgrid.insert(insertionpoint=[None, None, current_table], \
                            notoinsert=no_selected_tables)
        self.pysgrid.unredo.mark()

    def delete_rows(self, row, no_del=1):
        """Deletes no_del rows beginning at row."""
        
        if self.pysgrid.shape[0] > 0:
            self.pysgrid.remove(removalpoint=[row, None, None],
                                notoremove=no_del)
            self.create_rowcol()
        self.pysgrid.unredo.mark()
    
    def delete_cols(self, col, no_del=1):
        """Deletes no_del cols beginning at col."""
        
        if self.pysgrid.shape[1] > 0:
            self.pysgrid.remove(removalpoint=[None, col, None], \
                                notoremove=no_del)
            self.create_rowcol()
        self.pysgrid.unredo.mark()
    
    def delete_tables(self, tab):
        """Deletes table tab."""
        
        if self.pysgrid.shape[2] > 1:
            no_selected_tables = 1
            operation = (self.cbox_z.Delete, [self.pysgrid.shape[2] - 1])
            undo_operation = (self.cbox_z.Append, \
                              [unicode(self.pysgrid.shape[2] - 1)])
            self.pysgrid.unredo.append(undo_operation, operation)
            self.cbox_z.Delete(self.pysgrid.shape[2] - 1)
            self.pysgrid.remove(removalpoint=[None, None, tab], \
                                notoremove=1)
        self.pysgrid.unredo.mark()
    
# end of class GridManipulationMixin

# Manual cell level input
# -----------------------

class TextCellEditor(wx.grid.PyGridCellEditor):
    """Custom cell editor
    
    All the methods that can be overridden are present. The ones that 
    must be overridden are marked with "*Must Override*" in the docstring.
    
    """
    
    def __init__(self, parent):
        self.parent = parent
        wx.grid.PyGridCellEditor.__init__(self)

    def Create(self, parent, id, evtHandler):
        """Called to create the control, which must derive from wx.Control.
        
        *Must Override*
        
        """
        
        self._tc = EntryLine(parent, id)
        self._tc.SetInsertionPoint(0)
        self.SetControl(self._tc)
        
        if evtHandler:
            self._tc.PushEventHandler(evtHandler)

    def Show(self, show, attr):
        """
        Show or hide the edit control.  You can use the attr (if not None)
        to set colours or fonts for the control.
        
        """
        
        super(TextCellEditor, self).Show(show, attr)

    def BeginEdit(self, row, col, grid):
        """Fetch value from the table and prepare the edit control for editing.
        
        Set the focus to the edit control.
        *Must Override*
        
        """
        
        self.start_value = grid.GetTable().GetSource(row, col)
        try:
            self._tc.SetValue(self.start_value)
        except TypeError:
            pass
        self._tc.SetInsertionPointEnd()
        
        # wx.GTK fix that prevents the grid from moving around
        grid.Freeze()
        gridpos = grid.GetScrollPos(wx.HORIZONTAL), \
                  grid.GetScrollPos(wx.VERTICAL)
        self._tc.SetFocus()
        new_gridpos = grid.GetScrollPos(wx.HORIZONTAL), \
                      grid.GetScrollPos(wx.VERTICAL)
        if gridpos != new_gridpos:
            grid.Scroll(*gridpos)
        grid.Thaw()
        
        # Select the text
        self._tc.SetSelection(-1, -1)

    def EndEdit(self, row, col, grid):
        """Complete the editing of the current cell.
        
        Returns True if the value has changed.  
        If necessary, the control may be destroyed.
        *Must Override*
        
        """
        changed = False
        
        val = self._tc.GetValue()
        
        if val != self.start_value:
            changed = True
            
            # Update the table
            
            grid.GetTable().SetValue(row, col, val) 
            
        self.start_value = ''
        
        self.parent.pysgrid.unredo.mark()
        
        return changed

    def Reset(self):
        """
        Reset the value in the control back to its starting value.
        
        *Must Override*
        
        """
        
        self._tc.SetValue(self.start_value)
        self._tc.SetInsertionPointEnd()

    def StartingKey(self, evt):
        """If the editor is enabled by pressing keys on the grid, this will be
        
        called to let the editor do something about that first key if desired.
        
        """
        
        key = evt.GetKeyCode()
        char = None
        if key in [ wx.WXK_NUMPAD0, wx.WXK_NUMPAD1, wx.WXK_NUMPAD2, 
                    wx.WXK_NUMPAD3, wx.WXK_NUMPAD4, wx.WXK_NUMPAD5, 
                    wx.WXK_NUMPAD6, wx.WXK_NUMPAD7, wx.WXK_NUMPAD8, 
                    wx.WXK_NUMPAD9 ]:
            char = chr(ord('0') + key - wx.WXK_NUMPAD0)

        elif key < 256 and key >= 0 and chr(key) in string.printable:
            char = chr(key)

        if char is not None:
            #self._tc.AppendText(char)
            self._tc.ChangeValue(char) # Replace
            self._tc.SetInsertionPointEnd()
        else:
            self._tc.SetSelection(-1, -1)
            evt.Skip()

    def StartingClick(self):
        """If the editor is enabled by clicking on the cell,
        this method will be called to allow the editor to 
        simulate the click on the control if needed.
        
        """
        
        pass

    def Clone(self):
        """Create a new object which is the copy of this one
        
        *Must Override*
        
        """
        
        return TextCellEditor(parent=self)

# end of class TextCellEditor

