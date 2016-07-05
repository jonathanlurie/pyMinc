import h5py
import numpy as np
import codecs, json
from PIL import Image
import math

class MincReader:
    _mincHdf = None
    _imageDataset = None
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


    def getDataType(self):
        return self._dataType


    def getDataTypeMin(self):
        return np.iinfo(self._dataType).min


    def getDataTypeMax(self):
        return np.iinfo(self._dataType).max


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
    # For export purpose but could be used for something else.
    def _build3dArrayFromMinc(self):
        tempArray = np.zeros((self._xLength, self._yLength, self._zLength), dtype=self._dataType)

        for xRange in range(0, self._xLength):
            tempArray[xRange, :, :] = self._imageDataset[xRange]

        return tempArray


    # return the intensity value at a given (x, y, z) coordinate.
    # if x, y or z is not integer, we are performing
    # a trilinear interpolation
    def getValue(self, x, y, z):
        if(x >= 0 and x < self._xLength and
           y >= 0 and y < self._yLength and
           z >= 0 and z < self._zLength):

           if(x.is_integer() and x.is_integer() and z.is_integer()):
               print x
               print y
               print z

               val = self._imageDataset[int(x)][int(y), int(z)]
               print val
               print "-------------------------"
               return val
           else:
               return self._getValueTrilinear(x, y, z)
        else:
            print("ERROR: one of the index is out of range")

    # private mathod to save a numpy array as an image.
    # BEWARE: no data casting to [0, 255]
    def _saveImage(self, npArray, filepath):
        im = Image.fromarray(npArray)
        im.save(filepath, quality=100)


    # simple trilinear interpolation taken from
    # http://paulbourke.net/miscellaneous/interpolation
    def _getValueTrilinear(self, x, y, z):
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

        V000 = self.getValue(xBottom, yBottom, zBottom)
        V100 = self.getValue(xTop, yBottom, zBottom)
        V010 = self.getValue(xBottom, yTop, zBottom)
        V001 = self.getValue(xBottom, yBottom, zTop)
        V101 = self.getValue(xTop, yBottom, zTop)
        V011 = self.getValue(xBottom, yTop, zTop )
        V110 = self.getValue(xTop, yTop, zBottom)
        V111 = self.getValue(xTop, yTop, zTop)

        interpVal = V000 * (1 - xNorm) * (1 - yNorm) * (1 - zNorm) + \
                V100 * xNorm * (1 - yNorm) * (1 - zNorm) + \
                V010 * (1 - xNorm) * yNorm * (1 - zNorm) + \
                V001 * (1 - xNorm) * (1 - yNorm) * zNorm + \
                V101 * xNorm * (1 - yNorm) * zNorm + \
                V011 * (1 - xNorm) * yNorm * zNorm + \
                V110 * xNorm * yNorm * (1 - zNorm) + \
                V111 * xNorm * yNorm * zNorm

        return interpVal
