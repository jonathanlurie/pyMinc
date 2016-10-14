# some doc about afine/plane intersection: http://bit.ly/29kRQhv

import math

import VectorTools
import MincData
import Plane

import numpy as np
from PIL import Image

class ObliqueSampler:
    _3Ddata = None  # an instance of MincData
    _plane = None   # an instance of Plane
    _planePolygon = None # the polygon formed by the intersection of the plane and the cube of data (from 3 to 6 vertice)
    _samplingFactor = None # impact the size of the finale image

    _vecTools = None     # some (simple) tool to perform vector calculus

    def __init__(self, data3D, plane):
        self._samplingFactor = 1.
        self._vecTools = VectorTools.VectorTools()
        self._3Ddata = data3D
        self._plane = plane


    # important in case the plane changes (rotation or translation).
    # for now, it's only about the intersection polygon, but other method
    # may add up later
    def update(self):
        self.computeCubePlaneHitPoints()


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

        except ZeroDivisionError as e:
            # occures when this edge of the cube is defined along this plane
            return float("inf")

        return (x, y, z)


    # return the center of the polygon
    # as a tuple (x, y, z)
    def _getStartingSeed(self):
        if(self._planePolygon):

            xSum = 0
            ySum = 0
            zSum = 0
            numOfVertex = float( len(self._planePolygon) )

            for vertex in self._planePolygon:
                xSum = xSum + vertex[0]
                ySum = ySum + vertex[1]
                zSum = zSum + vertex[2]

            xCenter = float(xSum) / numOfVertex
            yCenter = float(ySum) / numOfVertex
            zCenter = float(zSum) / numOfVertex

            return (xCenter, yCenter, zCenter)

        else:
            print("ERROR: the polygon is not defined yet, you should call the update() method")
            return None


    # return the diagonal (length) of the polygon bounding box.
    # affected by the _samplingFactor (ie. doubled if 2)
    def _getLargestSide(self):

        if(self._planePolygon):

            xMin = self._planePolygon[0][0]
            yMin = self._planePolygon[0][1]
            zMin = self._planePolygon[0][2]

            xMax = self._planePolygon[0][0]
            yMax = self._planePolygon[0][1]
            zMax = self._planePolygon[0][2]

            for vertex in self._planePolygon:
                xMin = min(xMin, vertex[0])
                xMax = max(xMax, vertex[0])

                yMin = min(yMin, vertex[1])
                yMax = max(yMax, vertex[1])

                zMin = min(zMin, vertex[2])
                zMax = max(zMax, vertex[2])

            boxSide = math.sqrt((xMax-xMin)*(xMax-xMin) + (yMax-yMin)*(yMax-yMin) + (zMax-zMin)*(zMax-zMin))

            return boxSide * self._samplingFactor

        else:
            print("ERROR: the polygon is not defined yet, you should call the update() method")
            return None


    # we always start to fill the oblique image from its 2D center (in arg)
    # the center of the 2D oblique image matches the 3D starting seed
    # (center of the inner polygon, made by the intersection of the
    # plane with the cube)
    def obliqueImageCoordToCubeCoord(self, centerImage, startingSeed, dx, dy):
        u = self._plane.getUvector() # u goes to x direction (arbitrary)
        v = self._plane.getVvector() # v goes to y direction (arbitrary)

        target3Dpoint = (startingSeed[0] + dx * u[0] / self._samplingFactor + dy * v[0] / self._samplingFactor, \
            startingSeed[1]  + dx * u[1] / self._samplingFactor + dy * v[1] / self._samplingFactor, \
            startingSeed[2] + dx * u[2] / self._samplingFactor + dy * v[2] / self._samplingFactor)

        return target3Dpoint


    # returns True if the 3D coord matching to this oblique image point
    # is within the cube.
    # Returns False if outside the cube.
    def isImageCoordInCube(self, centerImage, startingSeed, dx, dy):
        cubeCoord = self.obliqueImageCoordToCubeCoord(centerImage, startingSeed, dx, dy)
        return self._3Ddata.isWithin(cubeCoord)



    def setSamplingFactor(self, f):
        self._samplingFactor = float(f)


    # start the sampling/filling process.
    # interpolate:
    #   False (default) = nearest neighbor, crispier
    #   True = trilinear (3D) interpolation, slower, smoother
    def startSampling(self, filepath, interpolate=False):

        dataType = self._3Ddata.getDataType()
        largestSide = round(self._getLargestSide())
        startingSeed = self._getStartingSeed()

        obliqueImageCenter = ( int(largestSide) / 2, int(largestSide) / 2)

        print(largestSide)

        # will contain the (interpolated) data from the cube
        obliqueImage = np.zeros((int(largestSide), int(largestSide)), dtype=dataType )

        # mask of boolean to track where the filling algorithm has already been
        obliqueImageMask = np.zeros((int(largestSide), int(largestSide)), dtype=dataType  )

        # stack used for the fillin algorithm
        pixelStack = []
        pixelStack.append(obliqueImageCenter)

        counter = 0

        print("start sampling...")

        while(len(pixelStack) > 0):
            currentPixel = pixelStack.pop()
            x = currentPixel[0]
            y = currentPixel[1]

            # if the image was not filled here...
            if(obliqueImageMask[y, x] == 0):
                # marking the mask (been here!)
                obliqueImageMask[y, x] = 255

                cubeCoord = self.obliqueImageCoordToCubeCoord(obliqueImageCenter, startingSeed, x - obliqueImageCenter[0], y - obliqueImageCenter[1])

                if(counter == 1500):
                    print(self._plane.getUvector() ) # u goes to x direction (arbitrary)
                    print(self._plane.getVvector() )
                    print("currentPixel:")
                    print(currentPixel)
                    print("cubeCoord:")
                    print(cubeCoord)

                # get the interpolated color of the currentPixel from 3D cube
                color = self._3Ddata.getValueTuple(cubeCoord, interpolate)

                # painting the image
                if(color):
                    obliqueImage[y, x] = int(color)
                else:
                    obliqueImage[y, x] = 0

                # going north
                try:
                    yNorth = y + 1
                    xNorth = x
                    if(obliqueImageMask[yNorth, xNorth] == 0):
                        if(self.isImageCoordInCube(obliqueImageCenter, startingSeed, xNorth - obliqueImageCenter[0], yNorth - obliqueImageCenter[1]) ):
                            pixelStack.append((xNorth, yNorth))
                except IndexError as e:
                    print(e)

                # going south
                try:
                    ySouth = y - 1
                    xSouth = x
                    if(obliqueImageMask[ySouth, xSouth] == 0):
                        if(self.isImageCoordInCube(obliqueImageCenter, startingSeed, xSouth - obliqueImageCenter[0], ySouth - obliqueImageCenter[1])):
                            pixelStack.append((xSouth, ySouth))
                except IndexError as e:
                    print(e)

                # going east
                try:
                    yEast = y
                    xEast = x + 1
                    if(obliqueImageMask[yEast, xEast] == 0):
                        if(self.isImageCoordInCube(obliqueImageCenter, startingSeed, xEast - obliqueImageCenter[0], yEast - obliqueImageCenter[1])):
                            pixelStack.append((xEast, yEast))
                except IndexError as e:
                    print(e)

                # going west
                try:
                    yWest = y
                    xWest = x - 1
                    if(obliqueImageMask[yWest, xWest] == 0):
                        if(self.isImageCoordInCube(obliqueImageCenter, startingSeed, xWest - obliqueImageCenter[0], yWest - obliqueImageCenter[1])):
                            pixelStack.append((xWest, yWest))
                except IndexError as e:
                    print(e)

            if(counter%100 == 0):
                None
                #print(counter)
                #im = Image.fromarray(obliqueImageMask)
                #im.save("mask/mask_" + str(counter) + ".jpg", quality=80)

            counter = counter + 1


        im = Image.fromarray(obliqueImage)
        im.save(filepath, quality=100)



    # TODO : add a sampling step for the oblique image
