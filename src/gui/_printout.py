import wx

from lib.irange import irange

class PrintCanvas(wx.ScrolledWindow):
    def __init__(self, parent, grid, print_area,id=-1, size=wx.DefaultSize):
        wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size, 
                                   style=wx.SUNKEN_BORDER)
        
        self.grid = grid
        self.print_area = print_area
        
        self.lines = []
        
        # Get dc size
        
        self.width, self.height = self._get_dc_size()
        
        self.x = self.y = 0
        self.curLine = []
        
        self.grid_attr = wx.grid.GridCellAttr()
        
        self.SetBackgroundColour("WHITE")
        self.SetCursor(wx.StockCursor(wx.CURSOR_PENCIL))

        self.SetVirtualSize((self.width, self.height))
        self.SetScrollRate(20, 20)
        
        self.Show(False)
    
    def _get_dc_size(self):
        """Returns width and height of print dc"""
        
        grid = self.grid
        (top, left), (bottom, right) = self.print_area
        
        tl_rect = grid.CellToRect(top, left)
        br_rect = grid.CellToRect(bottom, right)
        
        width  = br_rect.x + br_rect.width  - tl_rect.x
        height = br_rect.y + br_rect.height - tl_rect.y
        
        return width, height
    
    def draw_func(self, dc, rect, row, col):
        """Redirected Draw function from main grid"""
        
        return self.grid.grid_renderer.Draw( \
            self.grid, self.grid_attr, dc, rect, 
            row, col, False, printing=True)

    def get_print_rect(self, grid_rect):
        """Returns wx.Rect that is correctly positioned on the print canvas"""
        
        grid = self.grid
        
        rect_x = grid_rect.x - \
                 grid.GetScrollPos(wx.HORIZONTAL) * grid.GetScrollLineX()
        rect_y = grid_rect.y - \
                 grid.GetScrollPos(wx.VERTICAL) * grid.GetScrollLineY()
        
        return wx.Rect(rect_x, rect_y, grid_rect.width, grid_rect.height)

    def DoDrawing(self, dc):
        """Main drawing method"""
        
        (top, left), (bottom, right) = self.print_area
        
        dc.BeginDrawing()
        
        for row in irange(bottom, top, -1):
            for col in irange(right, left, -1):
                
                #Draw cell content
                
                grid_rect = self.grid.CellToRect(row, col)
                rect = self.get_print_rect(grid_rect)
                
                self.draw_func(dc, rect, row, col)
                
                # Draw grid
                
                ##self.grid._main_grid.text_renderer.redraw_imminent = False
                if col == left:
                    dc.DrawLine(rect.x, rect.y, rect.x, rect.y + rect.height)
                elif col == right:
                    dc.DrawLine(rect.x + rect.width, rect.y, 
                                rect.x + rect.width, rect.y + rect.height)
                if row == top:
                    dc.DrawLine(rect.x, rect.y, rect.x + rect.width, rect.y)
                elif row == bottom:
                    dc.DrawLine(rect.x, rect.y + rect.height, 
                                rect.x + rect.width, rect.y + rect.height)
        dc.EndDrawing()


class Printout(wx.Printout):
    def __init__(self, canvas):
        wx.Printout.__init__(self)
        self.canvas = canvas

    def OnBeginDocument(self, start, end):
        return super(Printout, self).OnBeginDocument(start, end)

    def OnEndDocument(self):
        super(Printout, self).OnEndDocument()

    def OnBeginPrinting(self):
        super(Printout, self).OnBeginPrinting()

    def OnEndPrinting(self):
        super(Printout, self).OnEndPrinting()

    def OnPreparePrinting(self):
        super(Printout, self).OnPreparePrinting()

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


