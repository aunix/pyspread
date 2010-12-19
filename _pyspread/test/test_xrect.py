import numpy
import xrect2
import _pyspread.xrect as xrect

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
        rect = xrect2.RotoOriginRect(w, h, angle)
        
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
        
        base_rect = xrect2.RotoOriginRect(20, 10, angle)
        clash_rect = xrect2.Rect(x, y, w, h)
        
        assert base_rect.collides(clash_rect) == res
    
