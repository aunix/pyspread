#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2009 Martin Manns
# Distributed under the terms of the GNU General Public License

# --------------------------------------------------------------------
# pyspread is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyspread is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyspread.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

from sys import path, modules
path.insert(0, "..") 
path.insert(0, "../..") 

import numpy
import lib.xrect as xrect

# test support code
def params(funcarglist):
    def wrapper(function):
        function.funcarglist = funcarglist
        return function
    return wrapper

def pytest_generate_tests(metafunc):
    for funcargs in getattr(metafunc.function, 'funcarglist', ()):
        metafunc.addcall(funcargs=funcargs)

# actual test code

class TestRect(object):

    param_comb_get_bbox = [ \
        {'x': 0, 'y': 0, 'w': 1, 'h': 1},
        {'x': 0, 'y': 1, 'w': 1, 'h': 1},
        {'x': 1, 'y': 0, 'w': 1, 'h': 1},
        {'x': 10, 'y': 10, 'w': 1, 'h': 1},
        {'x': 10, 'y': 10, 'w': 0, 'h': 0},
        {'x': 10, 'y': 10, 'w': 11, 'h': 11},
        {'x': 10, 'y': 10, 'w': 111, 'h': 21},
        {'x': 1234230, 'y': 1234320, 'w': 134, 'h': 23423423},
    ]
    
    @params(param_comb_get_bbox)
    def test_get_bbox(self, x, y, w, h):
        rect = xrect.Rect(x, y, w, h)
        assert rect.get_bbox() == (x, x + w, y, y + h)
    
    param_comb_collides = [ \
        {'x1': 0, 'y1': 0, 'w1': 1, 'h1': 1, 
         'x2': 0, 'y2': 0, 'w2': 1, 'h2': 1, 'collision': True},
    ]
    
    @params(param_comb_collides)
    def test_is_bbox_not_intersecting(self, x1, y1, w1, h1, \
                                            x2, y2, w2, h2, collision):
        rect1 = xrect.Rect(x1, y1, w1, h1)
        rect2 = xrect.Rect(x2, y2, w2, h2)
        
        assert rect1.is_bbox_not_intersecting(rect2) != collision
    
    @params(param_comb_collides)
    def test_collides(self, x1, y1, w1, h1, \
                            x2, y2, w2, h2, collision):
        rect1 = xrect.Rect(x1, y1, w1, h1)
        rect2 = xrect.Rect(x2, y2, w2, h2)
        
        assert rect1.collides(rect2) == collision


class TestRotoOriginRect(object):
    
    param_comb_get_bbox = [ \
        {'w': 1, 'h': 1, 'angle': 0},
        {'w': 0, 'h': 0, 'angle': 0},
        {'w': 10, 'h': 10, 'angle': 0},
        {'w': 10, 'h': 20, 'angle': 0},
        {'w': 10, 'h': 10, 'angle': 10},
        {'w': 20, 'h': 10, 'angle': 10},
        {'w': 45, 'h': 45, 'angle': 45},
        {'w': 210, 'h': 10, 'angle': 78},
        {'w': 2310, 'h': 2310, 'angle': 230},
        {'w': 110, 'h': 2310, 'angle': -20},
        {'w': 10, 'h': 10, 'angle': 121231320},
    ]
    
    @params(param_comb_get_bbox)
    def test_get_bbox(self, w, h, angle):
        w = 10
        h = 10
        angle  = 247
        rect = xrect.RotoOriginRect(w, h, angle)
        
        from math import sin, cos, pi
        
        rad_angle = angle / 180.0 * pi
        
        bbox_from_method = rect.get_bbox()
        
        trafo = numpy.matrix([cos(rad_angle), -sin(rad_angle),
                             sin(rad_angle), cos(rad_angle)]).reshape(2, 2)
        
        points = [numpy.array([-w / 2.0, -h / 2.0]).reshape(2, 1),
                  numpy.array([-w / 2.0, h / 2.0]).reshape(2, 1),
                  numpy.array([w / 2.0, h / 2.0]).reshape(2, 1),
                  numpy.array([w / 2.0, -h / 2.0]).reshape(2, 1)]
        
        p_rots = [trafo * point for point in points]
        
        bbox_x_min = float(min(p_rot[0] for p_rot in p_rots))
        bbox_x_max = float(max(p_rot[0] for p_rot in p_rots))
        bbox_y_min = float(min(p_rot[1] for p_rot in p_rots))
        bbox_y_max = float(max(p_rot[1] for p_rot in p_rots))
        
        bbox_calculated = bbox_x_min, bbox_x_max, bbox_y_min, bbox_y_max
        
        for b1, b2 in zip(bbox_from_method, bbox_calculated):
            print b1, b2
            assert abs(b1 - b2) < 1.0E-10
            
    
    param_comb_rotoorigin_collide = [ \
        # Identity
        {'x': -10, 'y': -5, 'w': 20, 'h': 10, 'angle': 0, 'res': True},
        # Move x
        {'x': -40, 'y': -5, 'w': 20, 'h': 10, 'angle': 0, 'res': False},
        {'x': -31, 'y': 0, 'w': 20, 'h': 10, 'angle': 0, 'res': False},
        {'x': -30, 'y': 0, 'w': 20, 'h': 10, 'angle': 0, 'res': True},
        {'x': 0, 'y': 0, 'w': 20, 'h': 10, 'angle': 0, 'res': True},
        {'x': 9, 'y': 0, 'w': 20, 'h': 10, 'angle': 0, 'res': True},
        {'x': 10, 'y': 0, 'w': 20, 'h': 10, 'angle': 0, 'res': True},
        {'x': 11, 'y': 0, 'w': 20, 'h': 10, 'angle': 0, 'res': False},
        {'x': 20, 'y': 0, 'w': 20, 'h': 10, 'angle': 0, 'res': False},
        # Move y
        {'x': -10, 'y': -20, 'w': 20, 'h': 10, 'angle': 0, 'res': False},
        {'x': -10, 'y': -16, 'w': 20, 'h': 10, 'angle': 0, 'res': False},
        {'x': -10, 'y': -15, 'w': 20, 'h': 10, 'angle': 0, 'res': True},
        {'x': -10, 'y': 4, 'w': 20, 'h': 10, 'angle': 0, 'res': True},
        {'x': -10, 'y': 5, 'w': 20, 'h': 10, 'angle': 0, 'res': True},
        {'x': -10, 'y': 6, 'w': 20, 'h': 10, 'angle': 0, 'res': False},
        {'x': -10, 'y': 10, 'w': 20, 'h': 10, 'angle': 0, 'res': False},
        # Move x and y
        {'x': -40, 'y': -20, 'w': 20, 'h': 10, 'angle': 0, 'res': False},
        {'x': -31, 'y': -16, 'w': 20, 'h': 10, 'angle': 0, 'res': False},
        {'x': -30, 'y': -15, 'w': 20, 'h': 10, 'angle': 0, 'res': True},
        {'x': 10, 'y': 5, 'w': 20, 'h': 10, 'angle': 0, 'res': True},
        {'x': 11, 'y': 6, 'w': 20, 'h': 10, 'angle': 0, 'res': False},
        # Move size
        {'x': -100, 'y': -50, 'w': 200, 'h': 100, 'angle': 0, 'res': True},
        {'x': -1, 'y': -0.5, 'w': 2, 'h': 1, 'angle': 0, 'res': True},
        {'x': -1, 'y': -0.5, 'w': 0, 'h': 0, 'angle': 0, 'res': True},
        # Move angle
        {'x': -10, 'y': -5, 'w': 20, 'h': 10, 'angle': 0.1, 'res': True},
        {'x': -10, 'y': -5, 'w': 20, 'h': 10, 'angle': 1, 'res': True},
        {'x': -10, 'y': -5, 'w': 20, 'h': 10, 'angle': 45.0, 'res': True},
        {'x': -10, 'y': -5, 'w': 20, 'h': 10, 'angle': -90.0, 'res': True},
        # Move angle and x
        {'x': -50, 'y': -5, 'w': 20, 'h': 10, 'angle': -0.1, 'res': False},
        {'x': -50, 'y': -5, 'w': 20, 'h': 10, 'angle': 0.1, 'res': False},
        {'x': -50, 'y': -5, 'w': 20, 'h': 10, 'angle': 1.0, 'res': False},
        {'x': -50, 'y': -5, 'w': 20, 'h': 10, 'angle': 90, 'res': False},
        {'x': 50, 'y': -5, 'w': 20, 'h': 10, 'angle': -0.1, 'res': False},
        {'x': 50, 'y': -5, 'w': 20, 'h': 10, 'angle': 0.1, 'res': False},
        {'x': 50, 'y': -5, 'w': 20, 'h': 10, 'angle': 1.0, 'res': False},
        # Move angle and size
        {'x': -20, 'y': -10, 'w': 40, 'h': 20, 'angle': 45.0, 'res': True},
        {'x': 8, 'y': 5, 'w': 2, 'h': 2, 'angle': -1.0, 'res': False},
        {'x': 8, 'y': 5, 'w': 2, 'h': 2, 'angle': 1.0, 'res': True},
    ]
    
    @params(param_comb_rotoorigin_collide)
    def test_rotoorigin_collide(self, x, y, w, h, angle, res):
        
        base_rect = xrect.RotoOriginRect(20, 10, angle)
        clash_rect = xrect.Rect(x, y, w, h)
        
        assert base_rect.collides(clash_rect) == res

class TestRotoRect(object):
    param_collides_axisaligned_rect = [ \
        # Identity
        {'x': 0, 'y': 0, 'w': 20, 'h': 10, 'angle': 0, 
         'x1': -10, 'y1': -5, 'w1': 20, 'h1': 10, 'res': True},
        # Shifted
        {'x': 50, 'y': 0, 'w': 20, 'h': 10, 'angle': 0, 
         'x1': -10, 'y1': -5, 'w1': 20, 'h1': 10, 'res': False},
        # Shifted and rotated
        {'x': 50, 'y': 0, 'w': 20, 'h': 10, 'angle': 30, 
         'x1': -10, 'y1': -5, 'w1': 20, 'h1': 10, 'res': False},
        {'x': 50, 'y': 0, 'w': 20, 'h': 10, 'angle': 30, 
         'x1': -10, 'y1': -5, 'w1': 100, 'h1': 10, 'res': True},
    ]
    
    @params(param_collides_axisaligned_rect)
    def test_collides_axisaligned_rect(self, x, y, w, h, angle, 
                                             x1, y1, w1, h1, res):
        base_rect = xrect.RotoRect(x, y, w, h, angle)
        clash_rect = xrect.Rect(x1, y1, w1, h1)
        
        assert base_rect.collides(clash_rect) == res
