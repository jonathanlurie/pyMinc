

class Plane:

    # the plane equation is:
    # ax + by + cz + d = 0

    _a = None
    _b = None
    _c = None
    _d = None
    _normalVector = None

    def __init__(self):
        None


    # initialize the equation of the plane from 3 points
    # each point is a tuple (x, y, z)
    def makeFromThreePoints(self, P, Q, R):
        # vector from P to Q
        vPQ = (Q[0] - P[0], Q[1] - P[1], Q[2] - P[2])
        vPR = (R[0] - P[0], R[1] - P[1], R[2] - P[2])

        self._normalVector = ( \
            vPQ[1] * vPR[2] - vPQ[2] * vPR[1], \
            (vPQ[0] * vPR[2] - vPQ[2] * vPR[0] ) * (-1), \
            vPQ[0] * vPR[1] - vPQ[1] * vPR[0]
        )

        self._a = self._normalVector[0]
        self._b = self._normalVector[1]
        self._c = self._normalVector[2]
        self._d = (-1) * (self._a * P[0] + self._b * P[1] + self._c * P[2] )


    # return the abcd factors of the plane equation as a tuple
    # assuming ax + by + cz + d = 0
    def getPlaneEquation(self):
        return (self._a, self._b, self._c, self._d)


    # return tuple with normal the vector
    def getNormalVector(self):
        return self._normalVector


    # u and v are two vectors frome this plane.
    # they are orthogonal and normalize so that we can build a regular grid
    # along this plane.
    # BEWARE: the equation and normal to the plane must be set
    # Some calculus hints come from there: http://bit.ly/29coWgs .
    # args: P and Q are two points from the plane. vPQ, when normalized
    # will be used as u
    def _defineUandV(self, P, Q):
        futureU = (Q[0] - P[0], Q[1] - P[1], Q[2] - P[2])

        # the future vector v
        futureV = ( \
            futureU[1] * self._normalVector[2] - futureU[2] * self._normalVector[1], \
            (futureU[0] * self._normalVector[2] - futureU[2] * self._normalVector[0] ) * (-1), \
            futureU[0] * self._normalVector[1] - futureU[1] * self._normalVector[0]
        )

        futureU_norm = math.sqrt(futureU[0]*futureU[0] + futureU[1]*futureU[1] + futureU[2]*futureU[2])
        futureU = (futureU[0]/futureU_norm, futureU[1]/futureU_norm, futureU[2]/futureU_norm)

        futureV_norm = math.sqrt(futureV[0]*futureV[0] + futureV[1]*futureV[1] + futureV[2]*futureV[2])
        futureV = (futureV[0]/futureV_norm, futureV[1]/futureV_norm, futureV[2]/futureV_norm)


if __name__ == "__main__":
    p = Plane()
    #p.makeFromThreePoints( (1, -2, 0), (3, 1, 4), (0, -1, 2))

    p.makeFromThreePoints( (1, -2, 0), (3, 10, 4), (0, -1, 2))
