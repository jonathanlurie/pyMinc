# some doc about afine/plane intersection: http://bit.ly/29kRQhv

import VectorTools
import MincData
import Plane

class ObliqueSampler:
    _3Ddata = None  # an instance of MincData
    _plane = None   # an instance of Plane
    _planePolygon = None # the polygon formed by the intersection of the plane and the cube of data (from 3 to 6 vertice)

    _vecTools = None     # some (simple) tool to perform vector calculus

    def __init__(self, data3D, plane):
        self._vecTools = VectorTools.VectorTools()
        self._3Ddata = data3D
        self._plane = plane


    # takes all the edges or the cube (12 in total)
    # and make the intersection with the plane.
    # For one single edge, there can be:
    # - no hit (the edge doesnt cross the plane)
    # - one hit (the edge crosses the plane)
    # - an infinity of hits (the edge belongs to the plane)
    def computeCubePlaneHitPoints(self):
        cubeEdges = self._3Ddata.getEdgesEquations()
        hitPoints = []

        for edge in cubeEdges:
            tempHitPoint = self._getHitPoint(edge[0], edge[1], self._plane)

            # 1- We dont want to add infinite because it mean an orthogonal edge
            # from this one (still of the cube) will cross the plane in a single
            # point -- and this later case is easier to deal with.
            # 2- Check if hitpoint is within the cube.
            if( tempHitPoint != float("inf") and \
                self._3Ddata.isWithin(tempHitPoint, True)):
                hitPoints.append(tempHitPoint)

        # trick to keep unique instance
        self._planePolygon = list(set(hitPoints))


    # return a point in 3D space (tuple (x, y, z) ).
    # vector and point define a "fixed vector" (droite affine)
    # both are tuple (x, y, z)
    # plane is the plane equation as a tuple (a, b, c, d)
    def _getHitPoint(self, vector, point, plane):

        # 3D affine system tuple:
        # ( (l, alpha), (m, beta), (n, gamma) )
        affineSystem = self._vecTools.affine3DFromVectorAndPoint(vector, point)

        # equation plane as ax + by + cz + d = 0
        # this tuple is (a, b, c, d)
        planeEquation = plane.getPlaneEquation()

        # system resolution for t:
        # t = (a*l + b*m + c*n + d) / ( -1 * (a*alpha + b*beta + c*gamma) )
        try:
            '''
            t = ( planeEquation[0]* affineSystem[0][0] + \
                  planeEquation[1]* affineSystem[1][0] + \
                  planeEquation[2]* affineSystem[2][0] + \
                  planeEquation[3] ) \
                / \
                ( (-1) * \
                ( planeEquation[0]* affineSystem[0][1] + \
                  planeEquation[1]* affineSystem[1][1] + \
                  planeEquation[2]* affineSystem[2][1] ) \
                )
            '''

            tNumerator = ( planeEquation[0]* affineSystem[0][0] + \
                  planeEquation[1]* affineSystem[1][0] + \
                  planeEquation[2]* affineSystem[2][0] + \
                  planeEquation[3] )

            tDenominator = (-1) * \
                ( planeEquation[0]* affineSystem[0][1] + \
                  planeEquation[1]* affineSystem[1][1] + \
                  planeEquation[2]* affineSystem[2][1] )

            # float conversion is mandatory to avoid euclidean div...
            t = float(tNumerator) / float(tDenominator)

            # injection of t to the 3D affine system:
            x =  affineSystem[0][0] + affineSystem[0][1] * t
            y =  affineSystem[1][0] + affineSystem[1][1] * t
            z =  affineSystem[2][0] + affineSystem[2][1] * t

            '''
            print "tNumerator:"
            print tNumerator
            print "tDenominator:"
            print tDenominator
            print "planeEquation:"
            print planeEquation
            print "affineSystem:"
            print affineSystem
            print "t:"
            print t
            print(str(x) + " " + str(y) + " " +  str(z))
            print("------------------------------")
            '''

        except ZeroDivisionError as e:
            #print "inf"
            #print("------------------------------")
            return float("inf")


        return (x, y, z)


    # return the center of the polygon
    # as a tuple (x, y, z)
    def _defineStartingSeed(self):
        if(self._planePolygon):

            xSum = 0
            ySum = 0
            zSum = 0
            numOfVertex = float(self._planePolygon.length)

            for vertex in self._planePolygon:
                xSum = xSum + vertex[0]
                ySum = ySum + vertex[1]
                zSum = zSum + vertex[2]

            xCenter = float(xSum) / numOfVertex
            yCenter = float(ySum) / numOfVertex
            zCenter = float(zSum) / numOfVertex

            return (xCenter, yCenter, zCenter)

        else:
            print("ERROR: the polygon is not defined yet")
            return None
