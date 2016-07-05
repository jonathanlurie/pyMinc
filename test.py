'''
Author: Jonathan Lurie

Documentation can be found here:
http://docs.h5py.org/en/latest/
'''
import numpy as np

import h5py


def printGroupName(name):
    """ For being used recursively with visit() """
    print name


def printGroupAttributes(name, object):
    """ For being used recursively with visititems() """
    print("------------------------------------------------")
    print name
    print object.attrs.keys()
    print object.attrs.values()
    #object.attrs.items()


mincFile = "data/full8_400um_optbal.mnc"

mincHdf = h5py.File(mincFile, 'r')
#print("name:")
#print(mincHdf.name)
#print("keys:")
#print(mincHdf.keys())
#print("values:")
#print(mincHdf.values())

# print names of group and subgroup recursively
#mincHdf.values()[0].visit(printGroupName)

#mincHdf.visititems(printGroupAttributes)


#imgGrp = mincHdf.require_group("minc-2.0/image/0/image")

imgGrp = mincHdf \
    .require_group("minc-2.0") \
    .require_group("image") \
    .require_group("0")


imgDataset = imgGrp.get("image")
#print(imgDataset.len())
print(imgDataset[0].shape[0])

print(np.dtype(imgDataset[11][165][136]))

print np.iinfo(np.dtype(imgDataset[11][165][136])).min
print np.iinfo(np.dtype(imgDataset[11][165][136])).max






#imgDataset = imgGrp.require_dataset("image")

#print(imgDataset)


mincHdf.close()
