PyMinc reads [Minc v2](http://www.bic.mni.mcgill.ca/ServicesSoftware/MINC) files. This format is based on HDF5 and contains volumetric image data, such as MRI, as well as additional metadata. This is compatible with **Python 2.7.x** and **Python > 3.4**.

PyMinc is far from complete and does not provide any mean to access to most metadata (this could be added, though).

# Installation
## The native lib
Since Minc v2 *is* HDF5, we need to compile/install the libHDF5. [Download the source here](https://support.hdfgroup.org/HDF5/release/obtainsrc.html#src) and extract the archive. Then, compile it:  

```  
# the version at the time of writing this
# is 1.8.17 but a slightly different one should work just as fine

$ cd hdf5-1.x.xx
$ mkdir /where/go/your/customLibs/hdf5
$ ./configure --prefix=/where/go/your/customLibs/hdf5
$ make
$ make install
```

At the end of this step, you should have the folders `bin`, `include`, `lib` and `share` copied in `/where/go/your/customLibs/hdf5`.

## Pythonic dependencies for HDF5
> If you judge Python dependency manager like *pip* or *easy_install* are always working fine, you may skip this part. In my case, these tools always put a mess and end up not working properly so I prefer to deal with the dependencies manually.

Before installing the proper Python bindings to libHDF5, you'll need to install [Nose](https://pypi.python.org/pypi/nose/1.3.7) and [Pkgconfig](https://pypi.python.org/pypi/pkgconfig/1.1.0). Download their source and for each, do:

```
$ python3 setup.py install
```

## Python bindings to HDF5 native lib
Download the source of [H5py](https://pypi.python.org/pypi/h5py/2.6.0) and install them:

```
$ python3 setup.py install
```

## Pythonic dependencies for PyMinc
In addition to just being able to read some HDF5 files, PyMinc converts the internal data into low level array with Numpy, and exports jpeg out of slices using PIL/Pillow.  
If you don't already have those two libraries, you will have to download the source of [Numpy](https://pypi.python.org/pypi/numpy/1.11.2) and [Pillow](https://pypi.python.org/pypi/Pillow/3.4.1) Then, install them:

```
$ python3 setup.py install
```

(I may have forgotten some dependencies of Numpy and Pillow).

# Let's play!
PyMinc is not a proper Python module but rather some py files to copy into your project. The `main.py` file just contains few examples.

## Doing simple things
By *simple things* I mean:
- reading a Minc file
- exporting a native othogonal slice
- get the value of a voxel (nearest neighbor or trilinear interpolation in case of using floating coordinates)
- get the type of data
- get the 3D size of the dataset
- export the whole thing into a json file (Does anyone need that?)

The files you'll need for that is `MincData.py`. Then:

```python
import MincData

# 1- loading the minc file
md = MincData.MincData("data/full8_400um_optbal.mnc")

# get the size of the minc data structure - tuple (x, y, z)
print(md.getSize())

# get the datatype as a string (i.e. "uint8")
print(md.getDataType())

# get a value from the 3D dataset
print(md.getValue(180, 180, 180))

# get a trilinear interpolated value, significantly slower in case of heavy usage
print(md.getValue(200.99, 150.01, 165.99, interpolate=True))

# exporting a slice as an image (native orientation)
md.exportNativeSlice(120, "nativeSlice.jpg")

# exporting a slice as an image  (non native orientation)
md.exportZRotatedSlice(120 , "rotateZSlice.jpg")

# exporting a slice as an image  (non native orientation)
md.exportYRotatedSlice(120, "rotateYSlice.jpg")

```

## Doing a not-so-simple thing: obliques
PyMinc is able to export oblique slices from a volumetric dataset, but you'll need to tune a few things first:
- import additional files
- define a [plane](https://en.wikipedia.org/wiki/Plane_(geometry) ) equation (mandatory)
- define a sampling factor (optional, default: 1)

To define the equation of the [plane](https://en.wikipedia.org/wiki/Plane_(geometry) ) that will slice your volume, you have two alternatives:
- using three 3D points in the space. Note: it's easier to figure when those points are at the edge of the volume.
- using a central point and a normal vector. Note: the point does not have to be within the volume, but it's easier to figure. About the vector, it does not have to be normalized (done internally).

Personally, I find the 2nd alternative much easier. For example, we could choose the center of the volume as a point and (0,1,1) as a vector (towards the diagonal following 2 dimensions out of 3). Example:

```python
import MincData
import Plane
import ObliqueSampler

# 1- loading the minc file
md = MincData.MincData("data/full8_400um_optbal.mnc")

# 2- creating an empty 3D plane
p = Plane.Plane()

# 3- specify the point and the vector
p.makeFromOnePointAndNormalVector((150, 150, 150), (0, 1, 1))

# optional, just to check if it's alright
print(p.getPlaneEquation())

# 4- creating the oblique sampler. See it as a bridge between
# the minc volume dataset  and the plane
os = ObliqueSampler.ObliqueSampler(md, p)

# 5- Should be called everytime the plane equation
# has been set/changed (translation, rotation)
os.update()

# Optional. If 1 (default), 1 minc voxel = 1 output image pixel
# Example usage: 0.5=image will be half the size, 2=image will be twice larger
os.setSamplingFactor(1)

# 6- export the oblique image
os.startSampling("oblique.jpg", interpolate=False)
```

The size of the output image is `volumeDiagonal X volumeDiagonal`. This is a lazy trick to make sure the largest oblique will fit in the output array.

If you specify (1, 0, 0), (0, 1, 0) or (0, 0, 1) as the directional vector, your are not performing obliques, you just use the oblique algorithm to export native orthogonal slices (which is a waste of time).
