#!/usr/bin/env python
# -*- coding: latin-1 -*-

"""2D Rectangle collision library"""

from math import sin, cos, pi

class Rect(object):
    """Rectangle class for axis aligned 2D rectangles
    
    Parameters
    ----------
    x: Number
    \tX-Coordinate of rectangle origin (lower left dot if angle == 0)
    y: Number
    \tY-Coordinate of rectangle origin (lower left dot if angle == 0)
    width: Number
    \tRectangle number
    height: Number
    \tRectangle height
    
    """
    
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def __str__(self):
        return "Rect(" + \
               ", ".join(map(str, (self.x, self.y, 
                                   self.width, self.height))) + \
               ")"
    
    def get_bbox(self):
        """Returns bounding box (xmin, xmax, ymin, ymax)"""
        
        x_min = self.x
        x_max = x_min + self.width
        y_min = self.y
        y_max = self.y + self.height
        
        return x_min, x_max, y_min, y_max
    
    def is_bbox_not_intersecting(self, other):
        """Returns False iif bounding boxed of self and other intersect"""
        
        self_x_min, self_x_max, self_y_min, self_y_max = self.get_bbox()
        other_x_min, other_x_max, other_y_min, other_y_max = other.get_bbox()
        
        return self_x_min > other_x_max or \
               other_x_min > self_x_max or \
               self_y_min > other_y_max or \
               other_y_min > self_y_max
    
    def is_point_in_rect(self, pt_x, pt_y):
        """Returns True iif point is inside the rectangle (border included)
        
        Parameters
        ----------
        
         * pt_x: Number
        \tx-value of point
         * pt_y: Number
        \ty-value of point
        
        """
        
        x_min, x_max, y_min, y_max = self.get_bbox()
        
        return x_min <= pt_x <= x_max and y_min <= pt_y <= y_max
    
    def collides(self, other):
        """Returns collision with axis aligned rect"""
        
        return not self.is_bbox_not_intersecting(other)


class RotoOriginRect(Rect):
    """Rectangle class for origin centered rotated rectangles
    
    Parameters
    ----------
    width: Number
    \tRectangle number
    height: Number
    \tRectangle height
    angle: Number:
    \tRectangle rotation angle clock-wise around origin
    
    """
    
    def __init__(self, width, height, angle):
        Rect.__init__(self, -width /  2.0, -height / 2.0, width, height)
        self.angle = angle / 180.0 * pi
    
    def __str__(self):
        return "RotoOriginRect(" + \
          ", ".join(map(str, (self.x, self.y, 
                              self.width, self.height, self.angle))) + \
          ")"
    
    def get_bbox(self):
        """Returns bounding box (xmin, xmax, ymin, ymax)"""
        
        width = self.width
        height = self.height
        
        cos_angle = cos(self.angle)
        sin_angle = sin(self.angle)
        
        x_diff = 0.5 * width
        y_diff = 0.5 * height
        
        # self rotates around (0, 0).
        c_x_diff = cos_angle * x_diff
        s_x_diff = sin_angle * x_diff

        c_y_diff = cos_angle * y_diff
        s_y_diff = sin_angle * y_diff
        
        if cos_angle > 0:
            if sin_angle > 0:
                x_max = c_x_diff + s_y_diff
                x_min = -x_max
                y_max = c_y_diff + s_x_diff
                y_min = -y_max
            else:  # sin_angle <= 0.0
                x_max = c_x_diff - s_y_diff
                x_min = -x_max
                y_max = c_y_diff - s_x_diff
                y_min = -y_max

        else:  # cos(angle) <= 0.0
            if sin_angle > 0:
                x_min = c_x_diff - s_y_diff
                x_max = -x_min
                y_min = c_y_diff - s_x_diff
                y_max = -y_min
            else:  # sin_angle <= 0.0
                x_min = c_x_diff + s_y_diff
                x_max = -x_min
                y_min = c_y_diff + s_x_diff
                y_max = -y_min
        
        return x_min, x_max, y_min, y_max
    
    def is_edge_not_excluding_vertices(self, other):
        """Returns False iif any edge excludes all vertices of other."""
        
        c_a = cos(self.angle)
        s_a = sin(self.angle)
        
        # Get min and max of other.
        
        other_x_min, other_x_max, other_y_min, other_y_max = other.get_bbox()
        
        self_x_diff = 0.5 * self.width
        self_y_diff = 0.5 * self.height
        
        if c_a > 0:
            if s_a > 0:
                return \
                c_a * other_x_max + s_a * other_y_max < -self_x_diff or \
                c_a * other_x_min + s_a * other_y_min >  self_x_diff or \
                c_a * other_y_max - s_a * other_x_min < -self_y_diff or \
                c_a * other_y_min - s_a * other_x_max >  self_y_diff

            else: # s_a <= 0.0
                return \
                c_a * other_x_max + s_a * other_y_min < -self_x_diff or \
                c_a * other_x_min + s_a * other_y_max >  self_x_diff or \
                c_a * other_y_max - s_a * other_x_max < -self_y_diff or \
                c_a * other_y_min - s_a * other_x_min >  self_y_diff

        else: # c_a <= 0.0
            if s_a > 0:
                return \
                c_a * other_x_min + s_a * other_y_max < -self_x_diff or \
                c_a * other_x_max + s_a * other_y_min >  self_x_diff or \
                c_a * other_y_min - s_a * other_x_min < -self_y_diff or \
                c_a * other_y_max - s_a * other_x_max >  self_y_diff

            else: # s_a <= 0.0
                return \
                c_a * other_x_min + s_a * other_y_min < -self_x_diff or \
                c_a * other_x_max + s_a * other_y_max >  self_x_diff or \
                c_a * other_y_min - s_a * other_x_max < -self_y_diff or \
                c_a * other_y_max - s_a * other_x_min >  self_y_diff
    
    def collides(self, other):
        """Returns collision with axis aligned rect"""
        
        angle = self.angle
        width = self.width
        height = self.height
        
        if angle == 0:
            return other.collides(Rect(-0.5*width, -0.5*height, width, height))
        
        # Phase 1
        #
        #  * Form bounding box on tilted rectangle P.
        #  * Check whether bounding box and other intersect.
        #  * If not, then self and other do not intersect.
        #  * Otherwise proceed to Phase 2.

        # Now perform the standard rectangle intersection test.

        if self.is_bbox_not_intersecting(other):
            return False


        # Phase 2
        #
        # If we get here, check the edges of self to see
        #  * if one of them excludes all vertices of other.
        #  * If so, then self and other do not intersect.
        #  * (If not, then self and other do intersect.)

        return not self.is_edge_not_excluding_vertices(other)

class RotoRect(object):
    """Rectangle class for generic rotated rectangles
    
    Parameters
    ----------
    x: Number
    \tX-Coordinate of rectangle origin (lower left dot if angle == 0)
    y: Number
    \tY-Coordinate of rectangle origin (lower left dot if angle == 0)
    width: Number
    \tRectangle number
    height: Number
    \tRectangle height
    angle: Number:
    \tRectangle rotation angle counter clock-wise around origin
    
    """
    
    def __init__(self, x, y, width, height, angle):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.angle_rad = angle / 180.0 * pi
        self.angle_deg = angle 

    def __str__(self):
        return "RotoRect(" + \
          ", ".join(map(str, (self.x, self.y, 
                              self.width, self.height, self.angle))) + \
          ")"
    
    def get_center(self):
        """Returns rectangle center"""
        
        c_a = cos(self.angle_rad)
        s_a = sin(self.angle_rad)
        
        center_x = self.x + self.width / 2.0 * c_a \
                          - self.height / 2.0 * s_a
        center_y = self.y - self.height / 2.0 * c_a \
                          - self.width / 2.0 * s_a
                          
        return center_x, center_y
    
    def collides_axisaligned_rect(self, other):
        """Returns collision with axis aligned other rect"""
        
        # Shift both rects so that self is centered at origin

        self_shifted = RotoOriginRect(self.width, self.height, -self.angle_deg)

        self_shifted_bbox = self_shifted.get_bbox()
        
        center_x, center_y = self.get_center()

        other_shifted = Rect(other.x - center_x, other.y - center_y, 
                             other.width, other.height)

        # Calculate collision
        
        return self_shifted.collides(other_shifted)

    def collides(self, other):
        """Returns collision with other rect"""
        
        # Is other rect not axis aligned?
        if hasattr(other, "angle"):
            raise NotImplementedError, "Non-axis aligned rects not implemented"
            
        else: # Other rect is axis aligned
            return self.collides_axisaligned_rect(other)

#if __name__ == "__main__":
#    pass
