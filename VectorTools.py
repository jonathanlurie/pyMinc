import math

class VectorTools:

    def __init__(self):
        None


    # returns the cross product vector between v1 and v2
    # both are tuple (x, y, z), and the one returned as well.
    # Note: the cross product of 2 vectors is also the normal vector.
    def crossProduct(self, v1, v2, normalize = True):
        normalVector = ( \
            v1[1] * v2[2] - v1[2] * v2[1], \
            (v1[0] * v2[2] - v1[2] * v2[0] ) * (-1), \
            v1[0] * v2[1] - v1[1] * v2[0]
        )

        if(normalize):
            normalVector = self.normalize(normalVector)

        return normalVector


    # normalize the vector v.
    # The returned vector will have a norm (length) of 1.
    def normalize(self, v):
        n = self.getNorm(v)
        normalizedV = (v[0]/n, v[1]/n, v[2]/n)
        return normalizedV


    # return the norm (length) of a vector
    def getNorm(self, v):
        n = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
        return n


    # Build a 3-member system for each x, y and z so that we can
    # make some calculus about a 3D affine line into a 3D space.
    # x = l + alpha * t
    # y = m + beta * t
    # z = n + gamma * t
    # (the parametric variable is t)
    # returns a tuple of tuple:
    # ( (l, alpha), (m, beta), (n, gamma) )
    def affine3DFromVectorAndPoint(self, vector, point):
        xTuple = (point[0] , vector[0])
        yTuple = (point[1] , vector[1])
        zTuple = (point[2] , vector[2])

        return (xTuple, yTuple, zTuple)



if __name__ == "__main__":
    v1 = (1, 0, 0)
    v2 = (0, 1, 0)
    v3 = (1, 1, 1)

    vt = VectorTools()

    cross = vt.crossProduct(v1, v2)
    print(cross)

    v3Normalized = vt.normalize(v3)
    print(v3Normalized)
