import wx

from _pyspread.irange import irange

class MyCanvas(wx.ScrolledWindow):
    def __init__(self, parent, grid, rowslice, colslice, tab,
                 id = -1, size = wx.DefaultSize):
        wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size, 
                                   style=wx.SUNKEN_BORDER)
        
        self.lines = []
        
        # Get dc size
        
        self.width, self.height = self._get_dc_size(grid, rowslice, colslice)
        
        self.x = self.y = 0
        self.curLine = []
        
        self.grid = grid
        self.grid_attr = wx.grid.GridCellAttr()
        
        self.rowslice = rowslice
        self.colslice = colslice
        
        self.tab = tab

        self.SetBackgroundColour("WHITE")
        self.SetCursor(wx.StockCursor(wx.CURSOR_PENCIL))

        self.SetVirtualSize((self.width, self.height))
        self.SetScrollRate(20, 20)
        
        self.Show(False)
    
    def _get_dc_size(self, grid, rowslice, colslice):
        """Returns width and height of print dc"""
        
        ul_rect = grid.CellToRect(rowslice.start, colslice.start)
        lr_rect = grid.CellToRect(rowslice.stop, colslice.stop)
        
        width  = lr_rect.x + lr_rect.width  - ul_rect.x
        height = lr_rect.y + lr_rect.height - ul_rect.y
        
        return width, height
    
    def draw_func(self, dc, rect, row, col):
        """Redirected Draw function from Maingrid"""
        
        return self.grid.text_renderer.Draw(self.grid, self.grid_attr, dc, 
                                      rect, row, col, False, printing=True)

    def DoDrawing(self, dc):
        """Main drawing method"""
        
        dc.BeginDrawing()
        
        for row in irange(self.rowslice.stop-1, self.rowslice.start-1, -1):
            for col in irange(self.colslice.stop-1, self.colslice.start-1, -1):
                rect = self.grid.CellToRect(row, col)
                
                rect = wx.Rect(rect.x - \
                               self.grid.GetScrollPos(wx.HORIZONTAL) * \
                               self.grid.GetScrollLineX(), 
                               rect.y - \
                               self.grid.GetScrollPos(wx.VERTICAL) * \
                               self.grid.GetScrollLineY(), 
                               rect.width, 
                               rect.height)
                
                self.draw_func(dc, rect, row, col)
                
                self.grid.text_renderer.redraw_imminent = False
                if col == self.colslice.start:
                    dc.DrawLine(rect.x, rect.y, rect.x, rect.y + rect.height)
                elif col == self.colslice.stop-1:
                    dc.DrawLine(rect.x + rect.width, rect.y, 
                                rect.x + rect.width, rect.y + rect.height)
                if row == self.rowslice.start:
                    dc.DrawLine(rect.x, rect.y, rect.x + rect.width, rect.y)
                elif row == self.rowslice.stop-1:
                    dc.DrawLine(rect.x,              rect.y + rect.height, 
                            rect.x + rect.width, rect.y + rect.height)
        dc.EndDrawing()


class MyPrintout(wx.Printout):
    def __init__(self, canvas):
        wx.Printout.__init__(self)
        self.canvas = canvas

    def OnBeginDocument(self, start, end):
        return super(MyPrintout, self).OnBeginDocument(start, end)

    def OnEndDocument(self):
        super(MyPrintout, self).OnEndDocument()

    def OnBeginPrinting(self):
        super(MyPrintout, self).OnBeginPrinting()

    def OnEndPrinting(self):
        super(MyPrintout, self).OnEndPrinting()

    def OnPreparePrinting(self):
        super(MyPrintout, self).OnPreparePrinting()

    def HasPage(self, page):
        if page <= 2:
            return True
        else:
            return False

    def GetPageInfo(self):
        return (1, 1, 1, 1)

    def OnPrintPage(self, page):
        dc = self.GetDC()

        # Set scaling factors

        maxX = self.canvas.width
        maxY = self.canvas.height

        # Let's have at least 50 device units margin
        marginX = 50
        marginY = 50

        # Add the margin to the graphic size
        maxX = maxX + (2 * marginX)
        maxY = maxY + (2 * marginY)

        # Get the size of the DC in pixels
        w, h = dc.GetSizeTuple()
        
        # Calculate a suitable scaling factor
        scaleX = float(w) / maxX
        scaleY = float(h) / maxY

        # Use x or y scaling factor, whichever fits on the DC
        actualScale = min(scaleX, scaleY)

        # Calculate the position on the DC for centering the graphic
        posX = (w - (self.canvas.width * actualScale)) / 2.0
        posY = (h - (self.canvas.height * actualScale)) / 2.0

        # Set the scale and origin
        dc.SetUserScale(actualScale, actualScale)
        dc.SetDeviceOrigin(int(posX), int(posY))

        #-------------------------------------------

        self.canvas.DoDrawing(dc)
        dc.DrawText("Page: %d" % page, marginX/2, maxY-marginY)

        return True


