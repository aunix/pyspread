import wx

class MyCanvas(wx.ScrolledWindow):
    def __init__(self, parent, grid, rowslice, colslice, tab,
                 id = -1, size = wx.DefaultSize):
        wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size, style=wx.SUNKEN_BORDER)

        self.lines = []
        self.width  = 1000
        self.height = 1000
        self.x = self.y = 0
        self.curLine = []
        
        self.grid = grid
        
        self.rowslice = rowslice
        self.colslice = colslice
        self.tab = tab

        self.SetBackgroundColour("WHITE")
        self.SetCursor(wx.StockCursor(wx.CURSOR_PENCIL))

        self.SetVirtualSize((self.width, self.height))
        self.SetScrollRate(20,20)
    
    def draw_func(self, dc, rect, row, col):
        """Redirected Draw function from Maingrid"""
        
        attr = wx.grid.GridCellAttr()
        draw_func = self.grid.text_renderer.Draw
        self.grid.text_renderer.redraw_imminent = True
        
        return draw_func(self.grid, attr, dc, rect, row, col, False)

    def DoDrawing(self, dc):
        """Main drawing method"""
        
        rect_w = int(round((self.width - self.x) / \
                           float(self.colslice.stop - self.colslice.start)))
        rect_h = int(round((self.height - self.y) / \
                           float(self.rowslice.stop - self.rowslice.start)))
        
        dc.BeginDrawing()
        
        for row in xrange(self.rowslice.stop, self.rowslice.start, -1):
            for col in xrange(self.colslice.stop, self.colslice.start, -1):
                rect = wx.Rect(rect_w * row, rect_h * col, rect_w, rect_h)
                self.draw_func(dc, rect, row, col)
        
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
        return (1, 2, 1, 2)

    def OnPrintPage(self, page):
        dc = self.GetDC()

        #-------------------------------------------
        # One possible method of setting scaling factors...

        maxX = self.canvas.width
        maxY = self.canvas.height

        # Let's have at least 50 device units margin
        marginX = 50
        marginY = 50

        # Add the margin to the graphic size
        maxX = maxX + (2 * marginX)
        maxY = maxY + (2 * marginY)

        # Get the size of the DC in pixels
        (w, h) = dc.GetSizeTuple()

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


