import VectorTools
import math

# simple verification from casio website: http://bit.ly/29LMfQ9

class Plane:

    # the plane equation is:
    # ax + by + cz + d = 0
    # here are those coeficents:
    _a = None
    _b = None
    _c = None
    _d = None

    _n = None   # the normal vector to the plane
    _u = None   # one of the vector that belong to the plane
    _v = None   # another vector that belong to the plane, orthogonal to _u

    _vecTools = None    # some (simple) tool to perform vector calculus


    def __init__(self):
        self._vecTools = VectorTools.VectorTools()


    # initialize the equation of the plane from 3 points
    # each point is a tuple (x, y, z)
    def makeFromThreePoints(self, P, Q, R):
        # vector from P to Q
        vPQ = (Q[0] - P[0], Q[1] - P[1], Q[2] - P[2])
        vPR = (R[0] - P[0], R[1] - P[1], R[2] - P[2])

        self._n = self._vecTools.crossProduct(vPQ, vPR, False)

        self._a = self._n[0]
        self._b = self._n[1]
        self._c = self._n[2]
        self._d = (-1) * (self._a * P[0] + self._b * P[1] + self._c * P[2] )

        self._defineUandVwith2points(P, Q)


    # initialize the equation of the plane from 1 point and a vector.
    # The point does not have to be within the cube.
    # point and vector are both tuple (x, y, z)
    def makeFromOnePointAndNormalVector(self, point, vector):
        self._n = vector
        self._a = self._n[0]
        self._b = self._n[1]
        self._c = self._n[2]
        self._d = (-1) * (self._a * point[0] + self._b * point[1] + self._c * point[2] )

        # find another point on the plane...

        # The next 3 cases are for when a plane is (at least in 1D)
        # aligned with the referential
        point2 = None

        # case 1
        try:
            x2 = point[0] + 1
            y2 = point[1]
            z2 = (-1) * ( (self._a * x2 + self._b * y2 + self._d) / self._c )
            point2 = (x2, y2, z2)

        except ZeroDivisionError:
            None

        # case 2
        try:
            if(not point2):
                x2 = point[0] + 1
                z2 = point[2]
                y2 = (-1) * ( (self._a * x2 + self._c * z2 + self._d) / self._b )
                point2 = (x2, y2, z2)
        except ZeroDivisionError:
            None

        # case 3
        try:
            if(not point2):
                y2 = point[1] + 1
                z2 = point[2]
                x2 =  (-1) * ( (self._b * y2 + self._c * z2 + self._d) / self._a )
                point2 = (x2, y2, z2)
        except ZeroDivisionError:
            None

        self._defineUandVwith2points(point, point2)


    # return the abcd factors of the plane equation as a tuple
    # assuming ax + by + cz + d = 0
    def getPlaneEquation(self):
        return (self._a, self._b, self._c, self._d)


    # return tuple with normal the vector
    def getNormalVector(self):
        return self._n


    # u and v are two vectors frome this plane.
    # they are orthogonal and normalize so that we can build a regular grid
    # along this plane.
    # BEWARE: the equation and normal to the plane must be set
    # Some calculus hints come from there: http://bit.ly/29coWgs .
    # args: P and Q are two points from the plane. vPQ, when normalized
    # will be used as u
    def _defineUandVwith2points(self, P, Q):
        self._u = self._vecTools.normalize( ( \
            Q[0] - P[0], \
            Q[1] - P[1], \
            Q[2] - P[2]\
            ) )

        self._v =  self._vecTools.crossProduct(self._u, self._n)


    # return the unit vector u as a tuple (x, y, z)
    def getUvector(self):
        return self._u


    # return the unit vector v as a tuple (x, y, z)
    def getVvector(self):
        return self._v






if __name__ == "__main__":
    p = Plane()
    #p.makeFromThreePoints( (1, -2, 0), (3, 1, 4), (0, -1, 2))
    #p.makeFromThreePoints( (1, -2, 0), (3, 10, 4), (0, -1, 2))
    p.makeFromThreePoints( (0, 0, 0), (1, 0, 0), (0, 1, 1))
    print(p.getPlaneEquation() )
