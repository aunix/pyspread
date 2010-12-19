from __future__ import division
import math
import pygame
##############################################################################

cos = lambda deg: math.cos(math.radians(deg))
sin = lambda deg: math.sin(math.radians(deg))

cos_table = dict([(deg, math.cos(math.radians(deg))) for deg in xrange(0, 360)])
sin_table = dict([(deg, math.sin(math.radians(deg))) for deg in xrange(0, 360)])


class RotoRect(pygame.rect.Rect):

    def __init__(self, *a, **kw):
        pygame.rect.Rect.__init__(self, *a, **kw)
        self.deg = kw['deg']

    def rotate(self, point, origin = 0):
    #   returns coords of point p rotated self.theta radians with the rectangle around its center
        if not origin: origin = self.center
        p_x = point[0]
        p_y = point[1]
        o_x = origin[0]
        o_y = origin[1]
        costheta = cos(self.deg)
        sintheta = sin(self.deg)
        return ((o_x + costheta * (p_x - o_x)) - (sintheta * (p_y - o_y)),
               (o_y + sintheta * (p_x - o_x)) + (costheta * (p_y - o_y)))

    def rotoxt(self, a, b):
    #   returns the y extremity xt of rect between self.rect
        a_x = a[0]
        a_y = a[1]
        b_x = b[0]
        b_y = b[1]
        dxl = self.left - b_x                                                 #calculate difference between self.left and b_x
        dxr = self.right - b_x                                                #calcualte difference between self.right and b_x
        if (dxl * dxr) > 0:                                                   #if b_x isn't between self.left and self.right
            if (dxl < 0):                                                       #if dxl < 1, b_x is on the right
                #xt = (m * dxr) + b_y
                xt = ((((b_y - (-a_y)) / (b_x - (-a_x))) * dxr) + b_y)
            else:                                                             #else b_x is on the left
                #xt = (m * dxl) + b_y
                xt = ((((b_y - a_y) / (b_x - a_x)) * dxl) + b_y)
            return xt
        else:                                                                 #else b_x is between self.left and self.right, and xt = b_y
            return b_y

    def rotocollide(self, rect):
    #   check for collision between self.rect and rect
        col = False                                                           #initialize collision to False
        transplane = rect.center                                              #transforming the plane to set rect's center to the origin
        #print "transplane", transplane
        rect.center = (0, 0)                                                  #set rect's center to the origin
        self.center = (self.centerx - transplane[0],
                       self.centery - transplane[1])                          #transform self.rect's center by the transplane amount
        #print "self.center", self.center
        transdeg = self.deg                                                   #transforming the plane to set self.rect's theta to 0
        self.deg = 0                                                          #set self.rect's theta to 0
        rect.deg -= transdeg                                                  #transform rect's theta by the transtheta amount
        if (sin(rect.deg) * cos(rect.deg)) > 0:                   #determine which vertice is min/max x/y NOTE: a = left/right, b = top/bottom
            a, b = rect.topright, rect.topleft                                  #a = extreme left/right, b = extreme top/bottom
        else:
            a, b = rect.topleft, rect.topright
        #print "a, b", a, b
        if sin(rect.deg) < 0:                                           #determine if a.x is min/max
            a  = -a[0], -a[1]                                                   #ensure a is always max
        a_x = a[0]
        negb = -b[0], -b[1]
        #print "negb", negb
        #print a_x, self.left, self.right, -a_x
        if (a_x >= self.left) and (self.right >= -a_x):                        #check that range of rect (-a.x, a.x) overlaps range of self.rect (self.left, self.right)
            xt1 = self.rotoxt(a, b)                                             #get the first extremity
            #print "xt1", xt1
            xt2 = self.rotoxt(a, negb)                                          #get the other extermity
            #print "xt2", xt2
            col = (((xt1 >= self.top) and (self.bottom >= xt2)) or
                   ((xt2 >= self.top) and (self.bottom >= xt1)))                #check for an intersection between the two extremities and self.rect's top/bottom
        rect.center = transplane                                              #retransform rect.center
        self.center = (self.centerx + transplane[0],
                            self.centery + transplane[1])                     #retransform self.rect.center
        self.deg = transdeg                                                   #retransform self.theta
        rect.deg += transdeg                                                  #retransform rect.theta
        return col                                                            #return results of collision test

    @property
    def rotox(self):
        return self.rotate(self.topleft)[0]
    @property
    def rotoy(self):
        return self.rotate(self.topleft)[1]
    @property
    def rotoleft(self):
        return self.rotate(self.left)
    @property
    def rotoright(self):
        return self.rotate(self.right)
    @property
    def rototop(self):
        return self.rotate(self.top)
    @property
    def rotobottom(self):
        return self.rotate(self.bottom)
    @property
    def rototopleft(self):
        return self.rotate(self.topleft)
    @property
    def rototopright(self):
        return self.rotate(self.topright)
    @property
    def rotobottomright(self):
        return self.rotate(self.bottomright)
    @property
    def rotobottomleft(self):
        return self.rotate(self.bottomleft)
    @property
    def rotomidleft(self):
        return self.rotate(self.midleft)
    @property
    def rotomidright(self):
        return self.rotate(self.midright)
    @property
    def rotomidtop(self):
        return self.rotate(self.midtop)
    @property
    def rotomidbottom(self):
        return self.rotate(self.midbottom)


class Polygon(RotoRect):
        def __init__(self, *a, **kw):
            bounds = [(min(e), max(e)) for e in zip(*((point[0], point[1]) for point in a))]
            x, y = bounds[0][0], bounds[1][0]
            w, h = bounds[0][1] - x, bounds[1][1] - y
            RotoRect.__init__(self, x, y, w, h, **kw)
            self._points = [point - self.boundrect.topleft for point in a]

        @property
        def points(self):
            return [point + self.boundrect.topleft for point in self._points]

        def fitrect(self):
            pass


class Line(object):

    def __init__(self, *a):
        # this should be able to take a Line object as an argument
        a = [e for e in [a[0]]] + [e for e in [a[1]]] + a[2:]             #ensure len(a) == 4
        self.p0_x = a[0]
        self.p0_y = a[1]
        self.p1_x = a[2]
        self.p1_y = a[3]

    @property
    def m(self):
        if self.p0_x != self.p1_x:
            return (self.p1_y - self.p0_y) / (self.p1_x - self.p0_x)
        else:
            return None

    @property
    def b(self):
        return self.p0_y - (self.m * self.p0_x)

    @property
    def dist(self):
        return math.sqrt((self.p1_x - self.p0_x)**2 + (self.p1_y - self.p0_y)**2)

    @property
    def delta(self):
        return (self.p1_x - self.p0_x, self.p1_y - self.p0_y)

    def intersection(self, *a):
        line = Line(*a)                                                   #initialize a line object
        if self.m != line.m:                                                #lines are not parallel
            if self.m and line.m:                                             #neither line is verticle
                x = (line.b - self.b) / (self.m - line.m)                       #
                y = (self.m * x) + self.b                                       #
            elif self.m == None:                                              #self is verticle, use line
                y = (line.m * self.p0_x) + line.b                               #
            elif line.m == None:                                              #line is verticle, use self
                y = (self.m * line.p0_x) + self.b                               #
            return (x, y)                                                     #return point of intersection
        elif self.b == line.b:                                              #else (self.m == line.m) and self.b == line.b
            return self                                                       #all points on line intersect
        else:                                                               #else (self.m == line.m and (self.b != line.b) := lines are parallel and never meet
            return None

    def line_clip(self, rect):
    #   returns a new Line2d object created by clipping self to rect using liang-barsky
        t0 = 0                                                            #initialize p0 (min) scalar
        t1 = 1                                                            #initialize p1 (max) scalar
        delta_x, delta_y = self.delta                                     #initialize delta
        if delta_x != 0:                                                  #if delta.x != 0
            rl = (rect.left - self.p0_x) / delta_x                          #compute clipping scalar to left edge
            rr = (rect.right - self.p0_x) / delta_x                         #compute clipping scalar to right edge
            if delta_x > 0:                                                 #if p0 is leftmost point
                if (rl > t0) and (0 <= rl <= 1):                              #
                    t0 = rl                                                     #
                if (rr < t1) and (0 <= rr <= 1):                              #
                    t1 = rr                                                     #
            else:                                                           #else p0 is rightmost point
                if (rl < t1) and (0 <= rl <= 1):                              #
                    t1 = rl                                                     #
                if (rr > t0) and (0 <= rr <= 1):                              #
                    t0 = rr                                                     #
        if delta_y != 0:                                                  #if delta.y != 0
            rb = (rect.bottom - self.p0_y) / delta_y                        #compute clipping scalar to bottom edge
            rt = (rect.top - self.p0_y) / delta_y                           #compute clipping scalar to top edge
            if delta_y > 0:                                                 #if p0 is topmost point
                if (rb < t1) and (0 <= rb <= 1):                              #
                    t1 = rb                                                     #
                if (rt > t0) and (0 <= rt <= 1):                              #
                    t0 = rt                                                     #
            else:                                                           #else p0 is bottommost point
                if (rb > t0) and (0 <= rb <= 1):                              #
                    t0 = rb                                                     #
                if (rt < t1) and (0 <= rt <= 1):                              #
                    t1 = rt                                                     #
        if t0 > t1:                                                       #if min scalar > max scalar
            return False                                                    #there is no need to clip
        return Line(self.p0_x + (t1 * delta_x),
                    self.p0_y + (t1 * delta_y),
                    self.p0_x + (t0 * delta_x),
                    self.p0_y + (t0 * delta_y))

    def line_trace(self):
    #   a simple line tracing algorithm that returns a set of pixels crossed by self
        s = set()                                                         #initialize a set for holding pixels
        delta_x, delta_y = self.delta                                     #initialize delta
        q_x, q_y = self.p0_x, self.p0_y                                   #instantiate copy of p0 for use in algorithm so original object is not changed
        s.add((self.p0_x, self.p0_y))                                     #add starting point to set of points line crosses
        if (not self.m) or (abs(self.m) >= 1):                            #if rise > run: rotate plane 90 degrees
            m = 1/self.m                                                    #rotate m by 90 degrees
            b = -(self.b * m)                                               #rotate b by 90 degrees
            if delta_y < 0:                                                 #determine direction of self.p1.x from q.y
                delta_y = -1                                                  #
            else:                                                           #
                delta_y = 1                                                   #
            while q_y != self.p1_y:                                         #while q.y has not reached self.p1.y: continue tracing
                q_y += delta_y;                                               #increment q.y one step closer to self.p1.y
                s.add((round((m * q_y) + b), q_y))                            #add the new pixel crossed to the set of pixels crossed
        else:                                                             #else rise < run
            m = self.m                                                      #
            b = self.b                                                      #
            if delta_x < 0:                                                 #determine direction of self.p1.x from q.x
                delta_x = -1                                                  #
            else:                                                           #
                delta_x = 1                                                   #
            while q_x != self.p1_x:                                         #while q.x has not reached self.p1.x: continue tracing
                q_x += delta_x                                                #increment q.x one step closer to self.p1.x
                s.add((q_x, round((m * q_x) + b)))                            #add the new pixel to the set of pixels crossed
        return s                                                          #return set of pixels crossed
