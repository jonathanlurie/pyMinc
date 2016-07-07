import MincData
import Plane
import ObliqueSampler

# 1- loading the minc file
md = MincData.MincData("data/full8_400um_optbal.mnc")

# exporting a slice as an image (native orientation)
#md.exportNativeSlice(120, "out/nativeSlice.jpg")

# exporting a slice as an image  (non native orientation)
#md.exportZRotatedSlice(120 , "out/rotateZSlice2.jpg")

# exporting a slice as an image  (non native orientation)
#md.exportYRotatedSlice(120, "yrotate.jpg")

# get the size of the minc data structure - tuple (x, y, z)
#print md.getSize()

# get a value from the cube
#print md.getValue(200, 150, 165)

# get a trilinear interpolated value, significantly slower in case of heavy usage
#print md.getValue(200.99, 150.01, 165.99, interpolate=True)

# Export the entire 3D dataset as a json file. The file produced is huge
# and maybe hard to parse then.
#md.exportToJson("data/full8_400um_optbal_2.json")


# 2- creating an empty 3D plane
p = Plane.Plane()

# setting the plane with 3 points, each is a tuple (x, y, z)
# Not bounded by the minc cube but should cross it at certain point
# if you want to get an oblique section... (makes sense, right?)
p.makeFromThreePoints( (0, 120, 0), (386, 120, 0), (0, 120, 348))


# 3- creating the oblique sampler, that build a bridge between
# the minc cube and the plane
os = ObliqueSampler.ObliqueSampler(md, p)

# Should be called at the begining or everytime the plane equation
# has changed (translation, rotation)
os.update()

# Optional. If 1 (default), 1 minc voxel = 1 output image pixel
# Exaple usage: 0.5=image will be half the size, 2=image will be twice larger
os.setSamplingFactor(1)

# Start the interpolation.
# interpolate=True will use a trilinear interpolation (slower, smoother)
os.startSampling("out/obliqueFlat120.jpg", interpolate=True)
