from math import pi, sin, cos

import types

import numpy

import wx

from _pyspread.irange import irange

import _pyspread.xrect as xrect

from _pyspread._interfaces import get_brush_from_data, get_pen_from_data, \
                                  get_font_from_data
from _pyspread.config import odftags, selected_cell_brush

# Grid level view
# ---------------


class MemoryMap(object):
    """Memory representation of grid canvas using numpy arrays
    
    Parameters
    ----------
     * size: 2-tuple of Integer
    \tSize of grid canvas in pixels
    
    """
    
    def __init__(self, size):
        self.resize(size)


    def resize(self, size):
        self.width, self.height = width, height = self.size = size
        
        self.background_layer = numpy.zeros((width, height, 3), dtype="uint8")
        self.border_layer     = numpy.zeros((width, height, 4), dtype="uint8")
        self.text_layer       = numpy.zeros((width, height, 4), dtype="uint8")
    
    def ndarray_to_wxbmp(self, ndarray):
        """Returns a wxBitmaop from a numpy array"""
        
        width, height = ndarray.shape[:2]
        
        image = wx.EmptyImage(width, height)
        image.SetData(array.tostring())
        
        # wx.BitmapFromImage(image)
        return image.ConvertToBitmap() 

class GridCollisionMixin(object):
    """Collison helper functions for grid drawing"""

    def colliding_cells(self, row, col, textbox):
        """Generates distance, row, col tuples of colliding cells
        
        Parameters
        ----------
        row: Integer
        \tRow of cell that is tested for collision
        col: Integer
        \tColumn of cell that is tested for collision
        
        """
        
        def l1_radius_cells(dist):
            """Generator of cell index tuples with distance dist to o"""
            
            if not dist:
                yield 0, 0
                
            else:
                for pos in xrange(-dist, dist+1):
                    yield pos, dist
                    yield pos, -dist
                    yield dist, pos
                    yield -dist, pos
        
        def get_max_visible_distance(row, col):
            """Returns maximum distance between current and any visible cell"""

            vis_cell_slice = self.get_visiblecell_slice()
            vis_row_min = vis_cell_slice[0].start
            vis_row_max = vis_cell_slice[0].stop
            vis_col_min = vis_cell_slice[1].start
            vis_col_max = vis_cell_slice[1].stop

            return max(vis_row_max - row, vis_col_max - col,
                       row - vis_row_min, col - vis_col_min)
        
        for dist in irange(get_max_visible_distance(row, col)):
            all_empty = True
            
            for radius_cell in l1_radius_cells(dist + 1):
                __row = radius_cell[0] + row
                __col = radius_cell[1] + col
                
                if self.IsVisible(__row, __col, wholeCellVisible=False):
                    cell_rect = self.CellToRect(__row, __col)
                    cell_rect = xrect.Rect(cell_rect.x, cell_rect.y, 
                                           cell_rect.width, cell_rect.height)
                    if textbox.collides_axisaligned_rect(cell_rect):
                        all_empty = False
                        yield dist + 1, __row, __col

            # If there are no collisions in a circle, we break
            
            if all_empty:
                break

    def get_block_direction(self, rect_row, rect_col, block_row, block_col):
        """Returns a blocking direction string from UP DOWN RIGHT LEFT"""

        diff_row = rect_row - block_row
        diff_col = rect_col - block_col

        assert not diff_row == diff_col == 0

        if abs(diff_row) <= abs(diff_col):
            # Columns are dominant
            if rect_col < block_col:
                return "RIGHT"
            else:
                return "LEFT"
        else:
            # Rows are dominant
            if rect_row < block_row:
                return "DOWN"
            else:
                return "UP"

    def get_background(self, key):
        """Returns the background"""
        
        row, col, _ = key

        _, _, width, height = self.CellToRect(row, col)

        bg_components = ["bgbrush", "borderpen_bottom", "borderpen_right"]

        bg_key = tuple([width, height] + \
                       [tuple(self.pysgrid.get_sgrid_attr(key, bgc)) \
                            for bgc in bg_components])

        try:
            bg = self.backgrounds[bg_key]

        except KeyError:
            if len(self.backgrounds) > 10000:
                # self.table.backgrounds may grow quickly
                self.backgrounds = {}

            bg = self.backgrounds[bg_key] = Background(self, *key)
        
        return bg

# End of class GridCollisionMixin

# Cell level view
# ---------------


class TextRenderer(wx.grid.PyGridCellRenderer):
    """This renderer draws borders and text at specified font, size, color"""

    def __init__(self, table):
        
        wx.grid.PyGridCellRenderer.__init__(self)
        
        self.table = table
    
    def get_textbox_edges(self, text_pos, text_extent):
        """Returns upper left, lower left, lower right, upper right of text"""
        
        string_x, string_y, angle = text_pos
        
        pt_ul =  string_x, string_y 
        pt_ll =  string_x, string_y + text_extent[1]
        pt_lr =  string_x + text_extent[0], string_y + text_extent[1]
        pt_ur =  string_x + text_extent[0], string_y
        
        if not -0.0001 < angle < 0.0001:
            rot_angle = angle / 180.0 * pi
            def rotation(x, y, angle, base_x=0.0, base_y=0.0):
                x -= base_x
                y -= base_y

                __x =  cos(rot_angle) * x + sin(rot_angle) * y
                __y = -sin(rot_angle) * x + cos(rot_angle) * y

                __x += base_x
                __y += base_y

                return __x, __y
            
            pt_ul = rotation(pt_ul[0], pt_ul[1], rot_angle, 
                              base_x=string_x, base_y=string_y)
            pt_ll = rotation(pt_ll[0], pt_ll[1], rot_angle, 
                              base_x=string_x, base_y=string_y)
            pt_ur = rotation(pt_ur[0], pt_ur[1], rot_angle, 
                              base_x=string_x, base_y=string_y)
            pt_lr = rotation(pt_lr[0], pt_lr[1], rot_angle, 
                              base_x=string_x, base_y=string_y)
        
        return pt_ul, pt_ll, pt_lr, pt_ur
    
    def get_text_rotorect(self, text_pos, text_extent):
        """Returns a RotoRect for given cell text"""
        
        import _pyspread.xrect as xrect
        
        pt_ll = self.get_textbox_edges(text_pos, text_extent)[1]
        
        rr_x, rr_y = pt_ll
        
        angle = float(text_pos[2]) 
        
        return xrect.RotoRect(rr_x, rr_y, text_extent[0], text_extent[1], angle)
    
    def draw_blocking_rect(self, dc, cell_rect, block_direction):
        """Draws block rectangles for given direction and blocking cell
        
        Properties
        ----------
        dc: wx.DC
        \t Target draw context
        block_direction: String in overflow_rects.keys()
        \tIdentifier for direction, in which blocking rect shall point
        cell_rect: wx.Rect
        \tRect of blocking cell
        
        """

        arrow, trafo = overflow_rects[block_direction]

        arrow_x, arrow_y = trafo(cell_rect.x, cell_rect.y,
                          cell_rect.width, cell_rect.height)

        dc.DrawBitmap(arrow, arrow_x, arrow_y, True)
    
    def draw_textbox(self, dc, text_pos, text_extent):
    
        pt_ul, pt_ll, pt_lr, pt_ur = self.get_textbox_edges(text_pos, 
                                                            text_extent)
        
        dc.DrawLine(pt_ul[0], pt_ul[1], pt_ll[0], pt_ll[1])
        dc.DrawLine(pt_ll[0], pt_ll[1], pt_lr[0], pt_lr[1])
        dc.DrawLine(pt_lr[0], pt_lr[1], pt_ur[0], pt_ur[1])
        dc.DrawLine(pt_ur[0], pt_ur[1], pt_ul[0], pt_ul[1])



    def draw_text_label(self, dc, res, rect, grid, pysgrid, key):
        """Draws text label of cell"""
        
        res_text = unicode(res)
        
        if not res_text:
            return
        
        row, col, tab = key
        
        textattributes = pysgrid.get_sgrid_attr(key, "textattributes")
        
        textfont = get_font_from_data( \
            pysgrid.get_sgrid_attr(key, "textfont"))
        
        self.set_font(dc, textfont, textattributes, grid.zoom)
        
        text_pos = self.get_text_position(dc, rect, res_text, 
                                          textattributes)
        ##TODO: Cut drawn text into pieces
        
        dc.DrawRotatedText(res_text, *text_pos)
        
        
        text_extent = dc.GetTextExtent(res_text)
        
        self._draw_strikethrough_line(grid, dc, rect, text_pos, text_extent,
                textattributes)
        
        # Collision detection
        
        __rect = xrect.Rect(rect.x, rect.y, rect.width, rect.height)
        
        # If cell rect stays inside cell, we do nothing
        if all(__rect.is_point_in_rect(*textedge) \
          for textedge in self.get_textbox_edges(text_pos, text_extent)):
            return
            
        textbox = self.get_text_rotorect(text_pos, text_extent)
        self.draw_textbox(dc, text_pos, text_extent)
        
        dc.SetPen(wx.BLACK_PEN)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        
        blocking_distance = None
        
        for distance, __row, __col in grid.colliding_cells(row, col, textbox):
            
            # Rectangles around colliding rects
            
            cell_rect = grid.CellToRect(__row, __col)
            dc.DrawRectangleRect(cell_rect)
            
            # Draw blocking arrows if locking cell is not empty
            
            if (blocking_distance is None or distance == blocking_distance) \
               and grid.pysgrid[__row, __col, tab] is not None:
                blocking_distance = distance
                
                block_direction = grid.get_block_direction(row, col, 
                                                           __row, __col)
                self.draw_blocking_rect(dc, cell_rect, block_direction)

        
    def _draw_strikethrough_line(self, grid, dc, rect, 
                                 text_pos, text_extent, textattributes):
        """Draws a strikethrough line if needed"""
        
        try:
            strikethrough_tag = odftags["strikethrough"]
            strikethrough = textattributes[strikethrough_tag]
            if strikethrough == "transparent":
                return
        except KeyError:
            return
            
        string_x, string_y, angle = text_pos
        
        strikethroughwidth = max(1, int(round(1.5 * grid.zoom)))
        dc.SetPen(wx.Pen(wx.BLACK, strikethroughwidth, wx.SOLID))

        x1 = string_x
        y1 = string_y + text_extent[1] / 2
        x2 = string_x + text_extent[0]
        y2 = string_y + text_extent[1] / 2

        if not -0.0001 < angle < 0.0001:

            rot_angle = angle / 180.0 * pi

            def rotation(x, y, angle, base_x=0.0, base_y=0.0):
                x -= base_x
                y -= base_y

                __x =  cos(rot_angle) * x + sin(rot_angle) * y
                __y = -sin(rot_angle) * x + cos(rot_angle) * y

                __x += base_x
                __y += base_y

                return __x, __y

            x1, y1 = rotation(x1, y1, rot_angle, 
                              base_x=string_x, base_y=string_y)
            x2, y2 = rotation(x2, y2, rot_angle,
                              base_x=string_x, base_y=string_y)

        dc.DrawLine(x1, y1, x2, y2)

    def set_font(self, dc, textfont, textattributes, zoom):
        """Sets font, text color and style"""
        try:
            fontcolortag = odftags["fontcolor"]
            textcolor = textattributes[fontcolortag]
        except KeyError:
            textcolor = wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOWTEXT)
        
        try:
            underline_mode = textattributes[odftags["underline"]]
        except KeyError:
            underline_mode = None
        
        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.SetTextForeground(textcolor)
        
        # Adjust font size to zoom
        
        font_size = textfont.GetPointSize()
        
        zoomed_fontsize = max(1, int(round(font_size * zoom)))
        
        zoomed_font = wx.Font(zoomed_fontsize, textfont.GetFamily(),
            textfont.GetStyle(), textfont.GetWeight(), 
            underline_mode == "continuous", textfont.GetFaceName())
        dc.SetFont(zoomed_font)
    
    def get_text_position(self, dc, rect, res_text, textattributes):
        """Returns text x, y, angle position in cell"""
        
        text_extent = dc.GetTextExtent(res_text)
        
        try: 
            text_align_tag = odftags["textalign"]
            horizontal_align = textattributes[text_align_tag]
        except KeyError: 
            pass
        
        try:
            vert_align_tag = odftags["verticalalign"]
            vertical_align = textattributes[vert_align_tag]
        except KeyError:
            vertical_align = "top"
        
        if vertical_align == "middle":
            string_y = rect.y + rect.height / 2 - text_extent[1] / 2 + 1
            
        elif vertical_align == "bottom":
            string_y = rect.y + rect.height - text_extent[1]
        
        else:
            string_y = rect.y + 2
        
        try:
            rot_angle_tag = odftags["rotationangle"]
            angle = float(textattributes[rot_angle_tag])
        except KeyError:
            angle = 0.0
        
        try:
            justification_tag = odftags["justification"]
            justification = textattributes[justification_tag]
        except KeyError:
            justification = "left"
        
        if justification == "left":
            string_x = rect.x + 2
            
        elif justification == "center":
            # First calculate x value for unrotated text
            string_x = rect.x + rect.width / 2 - 1
            
            # Now map onto rotated xy position
            rot_angle = angle / 180.0 * pi
            string_x = string_x - text_extent[0] / 2 * cos(rot_angle)
            string_y = string_y + text_extent[0] / 2 * sin(rot_angle)

        elif justification == "right":
            # First calculate x value for unrotated text
            string_x = rect.x + rect.width - 2
            
            # Now map onto rotated xy position
            rot_angle = angle / 180.0 * pi
            string_x = string_x - text_extent[0] * cos(rot_angle)
            string_y = string_y + text_extent[0] * sin(rot_angle)
        else:
            raise ValueError, "Cell justification must be left, center or right"
    
        return string_x, string_y, angle
        
    def Draw(self, grid, attr, dc, rect, row, col, isSelected, printing=False):
        """Draws the cell border and content"""
        
        pysgrid = self.table.pysgrid
        key = (row, col, self.table.current_table)
        
        if isSelected:
            grid.selection_present = True
            
            bg = Background(grid, row, col, self.table.current_table,
                            isSelected)
        else:
            bg = grid.get_background(key)
            
        if wx.Platform == "__WXGTK__" and not printing:
            mask_type = wx.AND
        else:
            mask_type = wx.COPY
            
        dc.Blit(rect.x, rect.y, rect.width, rect.height,
                bg.dc, 0, 0, mask_type)
        
        
        # Check if the dc is drawn manually be a return func
        
        res = grid.pysgrid[row, col, grid.current_table]
        
        if type(res) is types.FunctionType:
            # Add func_dict attribute 
            # so that we are sure that it uses a dc
            try:
                res(grid, attr, dc, rect)
            except TypeError:
                pass
        
        elif res is not None:
            self.draw_text_label(dc, res, rect, grid, pysgrid, key)
        
# end of class TextRenderer

class Background(object):
    """Memory DC with background content for given cell"""
    
    def __init__(self, grid, row, col, tab, selection=False):
        self.grid = grid
        self.key = row, col, tab
        
        self.dc = wx.MemoryDC() 
        self.rect = grid.CellToRect(row, col)
        self.bmp = wx.EmptyBitmap(self.rect.width, self.rect.height)
        
        self.selection = selection
        self.dc.SelectObject(wx.NullBitmap)
        self.dc.SelectObject(self.bmp)
        
        self.dc.SetBackgroundMode(wx.TRANSPARENT)

        self.dc.SetDeviceOrigin(0,0)
        
        self.draw()
        
        
    def draw(self):
        """Does the actual background drawing"""
        
        self.draw_background(self.dc)
        self.draw_border_lines(self.dc)

    def draw_background(self, dc):
        """Draws the background of the background"""
        
        if self.selection:
            bgbrush = selected_cell_brush
        else:
            bgbrush = get_brush_from_data( \
                self.grid.pysgrid.get_sgrid_attr(self.key, "bgbrush"))
        
        dc.SetBrush(bgbrush)
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangle(0, 0, self.rect.width, self.rect.height)

    def draw_border_lines(self, dc):
        """Draws lines"""
        
        x, y, w, h  = 0, 0, self.rect.width - 1, self.rect.height - 1
        grid = self.grid
        row, col, tab = key = self.key
        
        # Get borderpens and bgbrushes for rects        
        # Each cell draws its bottom and its right line only
        bottomline = x, y + h, x + w, y + h
        rightline = x + w, y, x + w, y + h
        lines = [bottomline, rightline]
        
        pen_names = ["borderpen_bottom", "borderpen_right"]
        
        borderpens = [get_pen_from_data(grid.pysgrid.get_sgrid_attr(key, pen)) \
                        for pen in pen_names]
        
        # Topmost line if in top cell
        
        if row == 0:
            lines.append((x, y, x + w, y))
            topkey = "top", col, tab
            toppen_data  = grid.pysgrid.get_sgrid_attr(topkey, pen_names[0])
            borderpens.append(get_pen_from_data(toppen_data))
        
        # Leftmost line if in left cell
        
        if col == 0:
            lines.append((x, y, x, y + h))
            leftkey = row, "left", tab
            toppen_data  = grid.pysgrid.get_sgrid_attr(leftkey, pen_names[1])
            borderpens.append(get_pen_from_data(toppen_data))
        
        zoomed_pens = []
        
        for pen in borderpens:
            bordercolor = pen.GetColour()
            borderwidth = pen.GetWidth()
            borderstyle = pen.GetStyle()
            
            zoomed_borderwidth = max(1, int(round(borderwidth * grid.zoom)))
            zoomed_pen = wx.Pen(bordercolor, zoomed_borderwidth, borderstyle)
            zoomed_pen.SetJoin(wx.JOIN_MITER)
            
            zoomed_pens.append(zoomed_pen)
        
        dc.DrawLineList(lines, zoomed_pens)

# end of class Background
