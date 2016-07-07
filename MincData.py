import h5py
import numpy as np
import codecs, json
from PIL import Image
import math

class MincData:
    _mincHdf = None
    _imageDataset = None
    _imageDatasetNd = None  # same data as _imageDataset but rearanged into a np.ndarray
    _xLength = 0
    _yLength = 0
    _zLength = 0
    _dataType = None

    def __init__(self, filepath):
        self._mincHdf = h5py.File(filepath, 'r')

        imgGrp = self._mincHdf \
            .require_group("minc-2.0") \
            .require_group("image") \
            .require_group("0")

        self._imageDataset = imgGrp.get("image")

        # number of slices
        self._xLength = self._imageDataset.len()

        # image height
        self._yLength = self._imageDataset[0].shape[0]

        # image width
        self._zLength = self._imageDataset[0].shape[1]

        # datatype (ie. uint8), determines the min, max
        self._dataType = np.dtype(self._imageDataset[0][0][0])

        self._convertDataToNdArray()


    # converting minc data (n 2D images) into a 3D numpy array
    # to speed up the getValue method (~x22 times faster)
    def _convertDataToNdArray(self):
        self._imageDatasetNd = np.ndarray(shape=(self._xLength, self._yLength, self._zLength ), dtype=self._dataType)

        for natSliceIndx in range(0, self._xLength):
            self._imageDatasetNd[natSliceIndx, :, :] = self._imageDataset[natSliceIndx][:, :]


    # returns the numpy type used for data
    def getDataType(self):
        return self._dataType


    # return the minimum value allowed by the datatype (ie. 0 for uint8).
    # useful when we want to output a uint8 image
    def getDataTypeMin(self):
        return np.iinfo(self._dataType).min


    # return the maximum value allowed by the datatype (ie. 255 for uint8)
    # useful when we want to output a uint8 image
    def getDataTypeMax(self):
        return np.iinfo(self._dataType).max


    # should be called at the end of the process, when we are done with hdf5 lib
    def close(self):
        self._mincHdf.close()


    def getSize(self):
        return (self._xLength, self._yLength, self._zLength)


    # export a slice in the the natively encoded datastructure
    def exportNativeSlice(self, sliceIndex, outFilepath):
        if(sliceIndex >= 0 and sliceIndex < self._xLength):
            self._saveImage(self._imageDataset[sliceIndex])
        else:
            print("ERROR: the slice index must be [0; " + str(self._xLength-1) + "]")

    # export a slice after turning the plane over Y axis
    # if native slice are coronal, YRotated will be sagital.
    # width = self._xLength, height = self._yLength
    def exportYRotatedSlice(self, sliceIndex, outFilepath):
        if(sliceIndex >= 0 and sliceIndex < self._zLength):

            # /!\ x and y are kind of
            # reverse from natural conventions in np
            arImg = np.zeros((self._yLength, self._xLength), dtype = self._dataType )

            # rather than filling arImg pixel by pixel,
            # this rotation allows to take entire columns
            for natSliceIndx in range(0, self._xLength):
                arImg[:, natSliceIndx] = self._imageDataset[natSliceIndx][:, sliceIndex]

            self._saveImage(arImg, outFilepath)

        else:
            print("ERROR: the slice index must be [0; " + str(self._zLength-1) + "]")


    # export a slice after turning the plane over Z axis
    # if native slice are coronal, ZRotated will be axial (sometimes called transverse).
    # width = self._xLength, height = self._zLength
    def exportZRotatedSlice(self, sliceIndex, outFilepath):
        if(sliceIndex >= 0 and sliceIndex < self._yLength):

            # /!\ x and y are kind of
            # reverse from natural conventions in np
            arImg = np.zeros((self._zLength, self._xLength), dtype = self._dataType )

            # rather than filling arImg pixel by pixel,
            # this rotation allows to take entire row
            for natSliceIndx in range(0, self._xLength):
                arImg[:, natSliceIndx] = self._imageDataset[natSliceIndx][ sliceIndex, :]

            self._saveImage(arImg, outFilepath)

        else:
            print("ERROR: the slice index must be [0; " + str(self._zLength-1) + "]")


    # USELESS
    # export the 3D block as a json file
    def exportToJson(self, filename):
        print("Info")
        print("\tbuilding 3D structure...")
        arr = self._build3dArrayFromMinc()

        print("\tpreparing data structure...")
        arrList = arr.tolist()

        print("\tconverting to json and write file...")
        #json.dump(arrList, codecs.open(filename, 'w', encoding='utf-8'), separators=(',', ':'), sort_keys=True, indent=4)

        with open(filename, 'w') as outfile:
            json.dump(arrList, outfile)


    # PRIVATE: build a 3D numpy array based on the minc data.
    # TODO: use _imageDatasetNd instead
    # For export purpose but could be used for something else.
    def _build3dArrayFromMinc(self):
        tempArray = np.zeros((self._xLength, self._yLength, self._zLength), dtype=self._dataType)

        for xRange in range(0, self._xLength):
            tempArray[xRange, :, :] = self._imageDataset[xRange]

        return tempArray


    # return the intensity value at a given (x, y, z) coordinate.
    # if x, y or z is not integer, we are performing
    # a trilinear interpolation
    def getValue_ORIG(self, x, y, z):
        # here we are keeping a 1 pixel margin to be sure we can interpolate
        if( (x >= 0 and x < self._xLength) and
            (y >= 0 and y < self._yLength) and
            (z >= 0 and z < self._zLength)):

           if(x.is_integer() and x.is_integer() and z.is_integer()):
              # print x
              # print y
              # print z

               val = self._imageDataset[int(x)][int(y), int(z)]
              # print val
              # print "-------------------------"
               return val
           else:
               return self.getValue( math.floor(x), math.floor(y), math.floor(z))
               #return self._getValueTrilinear(x, y, z)
        else:
            print("ERROR: one of the index is out of range")



    # COPY of the _ORIG, to be removed when done with it
    def getValue(self, x, y, z):
        val = 0

        try:
            val = self._imageDataset[ x][y, z]
        except Exception as e:
            print e

        return val


    # same as getValue but from the np.ndarray data structure
    def getValueNd(self, x, y, z):
        val = 0

        try:
            val = self._imageDatasetNd[x, y, z]
        except IndexError as e:
            print e

        return val


    # same as getValue but from the np.ndarray data structure
    def getValueNdTuple(self, coord):
        return self.getValueNd(coord[0], coord[1], coord[2])


    # exactelly the same as getValue, except it takes
    # a tuple (x, y, z) instead of 3 args
    def getValueTuple(self, coord):
        return self.getValue(coord[0], coord[1], coord[2])


    # each edge has a index, TODO: write about it.
    # return a list of edge data like that:
    # edgeData[n][vector, point]
    # where n is [0, 11] (a cube has 12 edges),
    # vector is a tuple (x, y, z),
    # and point is a point from the edge, also a tuple (x, y, z)
    def getEdgesEquations(self):
        edgeData = []

        # 0
        # vector:
        edge0Vect = (self._xLength, 0, 0)
        edge0Point = (0, 0, 0)

        # 1
        # vector:
        edge1Vect = (0, self._yLength, 0)
        edge1Point = (0, 0, 0)

        # 2
        # vector:
        edge2Vect = (0, 0, self._zLength)
        edge2Point = (0, 0, 0)

        # 3
        # vector:
        edge3Vect = (0, 0, self._zLength)
        edge3Point = (self._xLength, 0, 0)

        # 4
        # vector:
        edge4Vect = (self._xLength, 0, 0)
        edge4Point = (0, 0, self._zLength)

        # 5
        # vector:
        edge5Vect = (self._xLength, 0, 0)
        edge5Point = (0, self._yLength, 0)

        # 6
        # vector:
        edge6Vect = (0, 0, self._zLength)
        edge6Point = (0, self._yLength, 0)

        # 7
        # vector:
        edge7Vect = (0, 0, self._zLength)
        edge7Point = (self._xLength, self._yLength, 0)

        # 8
        # vector:
        edge8Vect = (self._xLength, 0, 0)
        edge8Point = (0, self._yLength, self._zLength)

        # 9
        # vector:
        edge9Vect = (0, self._yLength, 0)
        edge9Point = (0, 0, self._zLength)

        # 10
        # vector:
        edge10Vect = (0, self._yLength, 0)
        edge10Point = (self._xLength, 0, 0)

        # 11
        # vector:
        edge11Vect = (0, self._yLength, 0)
        edge11Point = (self._xLength, 0, self._zLength)

        edgeData.append( (edge0Vect, edge0Point) )
        edgeData.append( (edge1Vect, edge1Point) )
        edgeData.append( (edge2Vect, edge2Point) )
        edgeData.append( (edge3Vect, edge3Point) )
        edgeData.append( (edge4Vect, edge4Point) )
        edgeData.append( (edge5Vect, edge5Point) )
        edgeData.append( (edge6Vect, edge6Point) )
        edgeData.append( (edge7Vect, edge7Point) )
        edgeData.append( (edge8Vect, edge8Point) )
        edgeData.append( (edge9Vect, edge9Point) )
        edgeData.append( (edge10Vect, edge10Point) )
        edgeData.append( (edge11Vect, edge11Point) )

        return edgeData

    # private mathod to save a numpy array as an image.
    # BEWARE: no data casting to [0, 255]
    def _saveImage(self, npArray, filepath):
        im = Image.fromarray(npArray)
        im.save(filepath, quality=100)


    # simple trilinear interpolation taken from
    # http://paulbourke.net/miscellaneous/interpolation
    def _getValueTrilinear(self, x, y, z):

        # we dont bother with the sides
        if( x < 2 or x > self._xLength-3 or
            y < 2 or y > self._yLength-3 or
            z < 2 or z > self._zLength-3):
            return 0

        '''
        Here x, y and z are in a normalized space.

        Vxyz = 	V000 (1 - x) (1 - y) (1 - z) +
                V100 x (1 - y) (1 - z) +
                V010 (1 - x) y (1 - z) +
                V001 (1 - x) (1 - y) z +
                V101 x (1 - y) z +
                V011 (1 - x) y z +
                V110 x y (1 - z) +
                V111 x y z
        '''
        # For the sake of readability, let's assume that:
        xTop = math.ceil(x)
        yTop = math.ceil(y)
        zTop = math.ceil(z)

        xBottom = math.floor(x)
        yBottom = math.floor(y)
        zBottom = math.floor(z)

        # making a normalized space out of our coordinates
        xNorm = x - xBottom
        yNorm = y - yBottom
        zNorm = z - zBottom

        V000 = self.getValueNd(xBottom, yBottom, zBottom)
        V100 = self.getValueNd(xTop, yBottom, zBottom)
        V010 = self.getValueNd(xBottom, yTop, zBottom)
        V001 = self.getValueNd(xBottom, yBottom, zTop)
        V101 = self.getValueNd(xTop, yBottom, zTop)
        V011 = self.getValueNd(xBottom, yTop, zTop )
        V110 = self.getValueNd(xTop, yTop, zBottom)
        V111 = self.getValueNd(xTop, yTop, zTop)

        try:

            interpVal = V000 * (1 - xNorm) * (1 - yNorm) * (1 - zNorm) + \
                    V100 * xNorm * (1 - yNorm) * (1 - zNorm) + \
                    V010 * (1 - xNorm) * yNorm * (1 - zNorm) + \
                    V001 * (1 - xNorm) * (1 - yNorm) * zNorm + \
                    V101 * xNorm * (1 - yNorm) * zNorm + \
                    V011 * (1 - xNorm) * yNorm * zNorm + \
                    V110 * xNorm * yNorm * (1 - zNorm) + \
                    V111 * xNorm * yNorm * zNorm

            return interpVal

        except TypeError as e:
            print e

            print "V110"
            print V110

            print "xNorm"
            print xNorm

            print "yNorm"
            print yNorm

            print "zNorm"
            print zNorm

            print str(x) + " " + str(y) + " " + str(z)

            print "-------------------------------"

            return None





    # return True if the given point is within the data cube.
    # when allowEdges is true, the upper boundaries are pushed
    # by +1 in x, y and z
    def isWithin(self, point, allowEdges=False):

        if(allowEdges):
            if(point[0] >= 0 and \
               point[1] >= 0 and \
               point[2] >= 0 and \
               point[0] <= self._xLength and \
               point[1] <= self._yLength and \
               point[2] <= self._zLength ):
               return True
        else:
            if(point[0] >= 0 and \
               point[1] >= 0 and \
               point[2] >= 0 and \
               point[0] < self._xLength and \
               point[1] < self._yLength and \
               point[2] < self._zLength ):
               return True

        return False
