from math import pi, sin, cos

import types

import numpy

import wx

from _pyspread.irange import irange

import _pyspread.xrect as xrect

from _pyspread._interfaces import get_brush_from_data, get_pen_from_data, \
                                  get_font_from_data, hex_to_rgb
from _pyspread.config import odftags, selected_cell_brush

# Grid level view
# ---------------


#class MemoryMap(object):
#    """Memory representation of grid canvas using numpy arrays
#    
#    Parameters
#    ----------
#     * size: 2-tuple of Integer
#    \tSize of grid canvas in pixels
#    
#    """
#    
#    def __init__(self, size):
#        self.resize(size)
#
#
#    def resize(self, size):
#        """Creates a new memory map with a new size"""
#        
#        self.width, self.height = width, height = self.size = size
#        
#        width = width * 4
#        height = height * 4
#        
#        self.x_offset = width // 2
#        self.y_offset = height // 2
#        
#        self.background_layer = numpy.zeros((width, height, 4), dtype="uint8")
#        self.border_layer     = numpy.zeros((width, height, 4), dtype="uint8")
#        self.text_layer       = numpy.zeros((width, height, 4), dtype="uint8")
#    
#    def clear(self):
#        """Sets the memory maps to 0"""
#        
#        self.background_layer[:, :, :] = 0
#        self.border_layer[:, :, :] = 0
#        self.text_layer[:, :, :] = 0
#    
#    def draw_rect(self, target, key, color=(0, 0, 0)):
#        """Draws colors rectangle on target memory map
#        
#        Parameters
#        ----------
#         * target: numpy array
#        \tTarget memory map
#         * key: 2-tuple of slice
#        \tCell slice of rectangle (Works also for non-rectangle slices)
#         * color: Tuple of uint8
#        \tColor 3-tuple for rgb, 4-tuple for rgba
#        
#        """
#        
#        if len(color) == 3:
#            color += (255, )
#        
#        target[key[0], key[1], :] = numpy.array(color)
#    
#    def draw_h_line(self, target, x1, x2, y, color=(0, 0, 0), width=1):
#        """Draws horizontal line from (x1, y) to (x2, y) on target memory map"""
#        
#        width = max(1, int(round(width)))
#        width_2 = int(round(width / 2.0))
#        
#        y_min = y - width_2
#        y_max = y_min + width
#        
#        x1_off = x1 + self.x_offset
#        x2_off = x2 + self.x_offset
#        
#        key = (slice(x1_off - width_2, x2_off + 1 + width_2), 
#               slice(y_min + self.y_offset, y_max + self.y_offset + 1))
#        
#        self.draw_rect(target, key, color)
#
#    def draw_v_line(self, target, x, y1, y2, color=(0, 0, 0), width=1):
#        """Draws horizontal line from (x1, y) to (x2, y) on target memory map"""
#        
#        width = max(1, int(round(width)))
#        width_2 = int(round(width / 2.0))
#        
#        x_min = x - width_2
#        x_max = x_min + width
#        
#        y1_off = y1 + self.y_offset
#        y2_off = y2 + self.y_offset
#        
#        key = (slice(x_min + self.x_offset, x_max + self.x_offset + 1), 
#               slice(y1_off - width_2, y2_off + width_2 + 1))
#        
#        self.draw_rect(target, key, color)


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

        bg = Background(self, *key)
        
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

    def _get_empty_cells(self, dc, grid, key, text_pos, text_extent):
        """Generator of empty cells from key in direction
        
        Parameters
        ----------
        key: 3-tuple of Integer
        \tCurrent cell
        text_pos: 3-tuple
        \tPosition and direction of text

        """
        
        row, col, tab = key
        
        blocking_distance = None
        
        textbox = self.get_text_rotorect(text_pos, text_extent)
        
        for distance, __row, __col in grid.colliding_cells(row, col, textbox):
            # Draw blocking arrows if locking cell is not empty
            
            if (blocking_distance is None or distance == blocking_distance) \
               and not grid.pysgrid[__row, __col, tab]:
               
                yield __row, __col, tab
    
    def _get_available_space_rect(self, dc, grid, key, rect, text_pos, text_extent,
                                  res_text):
        """Returns rect of available space"""

        space_x = rect.x
        space_y = rect.y
        space_width = rect.width
        space_height = rect.height
        
        for cell in self._get_empty_cells(dc, grid, key, text_pos, text_extent):
            __row, __col, _ = cell
            cell_rect = grid.CellToRect(__row, __col)
            
            if cell_rect.x > space_x:
                # Cell is right of current cell
                space_width = cell_rect.x - space_x + cell_rect.width
                
            if cell_rect.x + cell_rect.width < space_x:
                # Cell is right of current cell
                space_width += space_x - cell_rect.x
                space_x = cell_rect.x

            if cell_rect.y > space_y + space_height:
                # Cell is below current cell
                space_height = cell_rect.y - space_y + cell_rect.height

            if cell_rect.y + cell_rect.height < space_y:
                # Cell is above of current cell
                space_height += space_y - cell_rect.y
                space_y = cell_rect.y

        return wx.Rect(space_x, space_y, space_width, space_height)

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
        
        __rect = xrect.Rect(rect.x, rect.y, rect.width, rect.height)
        
        text_extent = dc.GetTextExtent(res_text)
        
        # If cell rect stays inside cell, we simply draw
        
        if all(__rect.is_point_in_rect(*textedge) \
          for textedge in self.get_textbox_edges(text_pos, text_extent)):
            clipping = False
        else:
            clipping = True
            clip_rect = self._get_available_space_rect(dc, grid, key, rect, 
                                text_pos, text_extent, res_text)
        
        if clipping:
            dc.SetClippingRect(clip_rect)
        
        dc.DrawRotatedText(res_text, *text_pos)
        text_extent = dc.GetTextExtent(res_text)
        self._draw_strikethrough_line(grid, dc, rect, text_pos, text_extent,
                                      textattributes)
        if clipping:
            dc.DestroyClippingRegion()
        
        
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
            _, _, width, height = grid.CellToRect(row, col)
            
            bg_components = ["bgbrush", "borderpen_bottom", "borderpen_right"]
            
            bg_key = tuple([width, height] + \
                           [tuple(grid.pysgrid.get_sgrid_attr(key, bgc)) \
                                for bgc in bg_components])
            
            try:
                bg = self.table.backgrounds[bg_key]
                
            except KeyError:
                if len(self.table.backgrounds) > 10000:
                    # self.table.backgrounds may grow quickly
                    self.table.backgrounds = {}
                
                bg = self.table.backgrounds[bg_key] = Background(grid, *key)
            
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
        self.bmp = wx.EmptyBitmap(self.rect.width,self.rect.height)
        
        self.selection = selection
        
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
            bgbrush = wx.Brush(selected_cell_brush)
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

#class Background(object):
#    """Memory DC with background content for given cell"""
#    
#    def __init__(self, grid, row, col, tab, selection=False):
#        self.grid = grid
#        self.key = row, col, tab
#        
#        #self.memory_map = self.grid.parent.MainGrid.view.memory_map
#        
#        self.dc = wx.MemoryDC()
#        
#        rect = grid.CellToRect(row, col)
#        self.bmp = None
#        
#        self.selection = selection
#
#        
#        self.draw()
#    
#    def _get_screen_pos(self, x, y):
#        """Returns screen position of grid point"""
#        
#        grid = self.grid
#        
#        yunit, xunit = grid.GetScrollPixelsPerUnit()
#        self.xoff =  grid.GetScrollPos(wx.HORIZONTAL) * xunit
#        self.yoff = grid.GetScrollPos(wx.VERTICAL) * yunit
#        
#        return x - self.xoff, y - self.yoff
#    
#    def get_pasted_map(self, base_map, top_map):
#        """Returns rgba map with top_map on base_map"""
#        
#        alpha_map = numpy.array([(top_map[:, :, 3] / 255.0).tolist()] * 3).\
#                        transpose(1, 2, 0)
#        
#        resultmap = base_map[:, :, :]
#        
#        resultmap[:, :, :3] = numpy.uint8( \
#                                base_map[:, :, :3] * (1 - alpha_map) + \
#                                top_map[:, :, :3] * alpha_map)
#        
#        return resultmap
#    
##    def _adjust_partly_visible_cells(self, x, y, width, height):
##        """Returns x, y, width, height so that rect stays inside memory map"""
##        
##        memshape = self.memory_map.background_layer.shape
##        
##        if x < -self.memory_map.x_offset:
##            width = width + x + self.memory_map.x_offset
##            x = 0
##            if width < 0:
##                raise AssertionError, "Cell invisible."
##                
##        if y < -self.memory_map.x_offset:
##            height = height + y + self.memory_map.x_offset
##            y = 0
##            if height < 0:
##                raise AssertionError, "Cell invisible."
##        
##        return x, y, width, height
#    
#    def _get_rect_coords(self, row, col):
#        """Returns rect coordinates if successful else raises assertion"""
#        
#        rect = self.grid.CellToRect(row, col)
#        x, y, width, height  = rect.Get()
#        x, y = self._get_screen_pos(x, y)
#        
#        return self._adjust_partly_visible_cells(x, y, width, height)
#    
#    def draw(self):
#        """Does the actual background drawing"""
#        
#        row, col, tab = self.key
#        
#        memory_map_cache = self.grid.parent.MainGrid.view.memory_map_cache
#        
#        for key in [(row - 1, col - 1, tab),
#                    (row,     col - 1, tab),
#                    (row + 1, col - 1, tab),
#                    (row - 1, col,     tab),
#                    (row,     col,     tab),
#                    (row + 1, col,     tab),
#                    (row - 1, col + 1, tab),
#                    (row    , col + 1, tab),
#                    (row + 1, col + 1, tab)]:
#            try:
#                self.grid.parent.MainGrid.view.memory_map_cache.pop(key)
#            except KeyError:
#                pass
#        
#        x, y, width, height = self._get_rect_coords(row, col)
#        
#        self.draw_background()
#        self.draw_border_lines()
#        
#        x_offset = self.memory_map.x_offset
#        y_offset = self.memory_map.y_offset
#        
#        key = slice(x + x_offset, x + x_offset + width), \
#              slice(y + y_offset, y + y_offset + height), slice(None, None)
#        
#        pasted_map = self.get_pasted_map(self.memory_map.background_layer[key],
#                                         self.memory_map.border_layer[key])
#        
#        # Note ther eversed w, h notation of wxPython
#        
#        transposed_pasted_map = pasted_map.transpose(1, 0, 2)
#        
#        dummy = numpy.zeros(transposed_pasted_map.shape, dtype="uint8")
#        
#        dummy[:,:,:] = transposed_pasted_map
#        
#        self.bmp = wx.EmptyBitmap(width, height)
#        
#        dc = self.dc
#        
#        dc.SelectObject(wx.NullBitmap)
#        dc.SelectObject(self.bmp)
#        dc.SetBackgroundMode(wx.TRANSPARENT)
#        dc.SetDeviceOrigin(0,0)
#        
#        bmp = wx.BitmapFromBufferRGBA(dummy.shape[1], dummy.shape[0], dummy)
#        
#        dc.DrawBitmap(bmp, 0, 0)
#
#    def draw_background(self):
#        """Draws the background of the background"""
#        
#        row, col, _ = self.key
#        
#        rect = self.grid.CellToRect(row, col)
#        x, y, width, height  = rect.Get()
#        x, y = self._get_screen_pos(x, y)
#        
#        if self.selection:
#            color = selected_cell_brush
#        else:
#            int_col, _ = self.grid.pysgrid.get_sgrid_attr(self.key, "bgbrush")
#            color = hex_to_rgb(int_col)
#        
#        target = self.memory_map.background_layer
#        
#        x_offset = self.memory_map.x_offset
#        y_offset = self.memory_map.y_offset
#        
#        key = slice(x + x_offset, x + x_offset+ width), \
#              slice(y + y_offset, y + y_offset + height)
#        
#        self.memory_map.draw_rect(target, key, color=color)
#    
#    def zoom_line_width(self, width):
#        """Zooms line width according to self.grid.zoom"""
#        
#        return width * self.grid.zoom
#    
#    def get_pen_attr(self, key, pen_name):
#        """Returns color, zoomed width and style of a pen defined in cell key"""
#        
#        cell_attr = self.grid.pysgrid.get_sgrid_attr
#        
#        int_color, width, style = cell_attr(key, pen_name)
#        
#        # Color conversion from rgb packed in an int
#        color = hex_to_rgb(int_color)
#        
#        zoomed_width = self.zoom_line_width(width)
#        
#        return color, zoomed_width, style
#    
#    def draw_border_lines(self):
#        """Draws lines"""
#        
#        row, col, _ = self.key
#        
#        rect = self.grid.CellToRect(row, col)
#        x, y, width, height  = rect.Get()
#        x, y = self._get_screen_pos(x, y)
#        
#        grid = self.grid
#        row, col, tab = key = self.key
#        
#        # Draw to memory map
#        
#        memory_map = self.memory_map
#        
#        color_btm, width_btm, _ = self.get_pen_attr(key, "borderpen_bottom")
#        color_right, width_right, _ = self.get_pen_attr(key, "borderpen_right")
#        
#        target = memory_map.border_layer
#        
#        memory_map.draw_h_line(target, x, x + width, y + height,
#                               color_btm, width=width_btm)
#        memory_map.draw_v_line(target, x + width, y, y + height,
#                               color_right, width=width_right)
#        
#        # Topmost line if in top cell
#        
#        if row == 0:
#            topkey = "top", col, tab
#            
#            color_top, width_top, _ = \
#                self.get_pen_attr(topkey, "borderpen_bottom")
#            
#            memory_map.draw_h_line(target, x, x + width, y, 
#                                   color_top, width=width_top)
#        
#        # Leftmost line if in left cell
#        
#        if col == 0:
#            leftkey = row, "left", tab
#            
#            color_left, width_left, _ = \
#                self.get_pen_attr(leftkey, "borderpen_right")
#            
#            memory_map.draw_v_line(target, x , y, y + height, 
#                                   color_left, width=width_left)
#        

# end of class Background
