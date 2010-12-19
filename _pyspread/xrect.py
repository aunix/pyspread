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
    
    def get_bbox(self):
        """Returns bounding box (xmin, ymin, xmax, ymax)"""
        
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
        
        self.width = width
        self.height = height
        self.angle = angle / 180.0 * pi
    
    def get_bbox(self):
        """Returns bounding box (xmin, ymin, xmax, ymax)"""
        
        angle = self.angle
        width = self.width
        height = self.height
        
        cos_angle = cos(angle)
        sin_angle = sin(angle)
        
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
        
    def collides(self, other):
        """Returns collision with axis aligned rect"""
        
        angle = self.angle
        width = self.width
        height = self.height
        
        if angle == 0:
            return other.collides(Rect(-0.5*width, -0.5*height, width, height))
        
        other_x = other.x
        other_y = other.y
        other_width = other.width
        other_height = other.height
        
        """
        Phase 1

         * Form bounding box on tilted rectangle P.
         * Check whether bounding box and other intersect.
         * If not, then self and other do not intersect.
         * Otherwise proceed to Phase 2.

        """

        # Now perform the standard rectangle intersection test.

        if self.is_bbox_not_intersecting(other):
            return False

        """
        Phase 2

        If we get here, check the edges of self to see
         * if one of them excludes all vertices of other.
         * If so, then self and other do not intersect.
         * (If not, then self and other do intersect.)

        """
        c = cos(angle)
        s = sin(angle)
        
        # Get min and max of other.
        other_x_min = other_x
        other_x_max = other_x_min + other_width
        other_y_min = other_y
        other_y_max = other_y_min + other_height
        
        self_x_diff = 0.5 * width
        self_y_diff = 0.5 * height
        
        if c > 0:
            if s > 0:
                return not ( \
                c * other_x_max + s * other_y_max < -self_x_diff or \
                c * other_x_min + s * other_y_min >  self_x_diff or \
                c * other_y_max - s * other_x_min < -self_y_diff or \
                c * other_y_min - s * other_x_max >  self_y_diff )

            else: # s <= 0.0
                return not ( \
                c * other_x_max + s * other_y_min < -self_x_diff or \
                c * other_x_min + s * other_y_max >  self_x_diff or \
                c * other_y_max - s * other_x_max < -self_y_diff or \
                c * other_y_min - s * other_x_min >  self_y_diff )

        else: # c <= 0.0
            if s > 0:
                return not ( \
                c * other_x_min + s * other_y_max < -self_x_diff or \
                c * other_x_max + s * other_y_min >  self_x_diff or \
                c * other_y_min - s * other_x_min < -self_y_diff or \
                c * other_y_max - s * other_x_max >  self_y_diff )

            else: # s <= 0.0
                return not ( \
                c * other_x_min + s * other_y_min < -self_x_diff or \
                c * other_x_max + s * other_y_max >  self_x_diff or \
                c * other_y_min - s * other_x_max < -self_y_diff or \
                c * other_y_max - s * other_x_min >  self_y_diff )

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
    \tRectangle rotation angle clock-wise around origin
    
    """
    
    def __init__(self, x, y, width, height, angle):
        pass
        

if __name__ == "__main__":
    pass
