from math import acos
from math import sqrt
from math import pi


class Point:
    xcor = None
    ycor = None
    ref_point = None
    angle = None
    dist_to_ref = None
    dot_product = None
    val_in_image = None

    def __init__(self, x, y, ref=None):
        self.xcor = x
        self.ycor = y
        if ref:
            self.ref_point = ref
            self.calc_angle()

    def get_len_to_ref(self):
        self.dist_to_ref = sqrt((self.xcor - self.ref_point.xcor) ** 2 + (self.ycor - self.ref_point.ycor) ** 2)
        return self.dist_to_ref

    def calc_angle(self):
        self.get_len_to_ref()
        if self.dist_to_ref == 0.0:
            self.angle = 0.0
            return self.angle
        cosx = (self.xcor - self.ref_point.xcor) / self.dist_to_ref
        try:
            self.angle = acos(cosx)
            if self.ycor < self.ref_point.ycor:
                self.angle = 2*pi - self.angle
        except ValueError as e:
            print cosx
            print self.xcor, self.ycor
            exit(0)
        return self.angle
