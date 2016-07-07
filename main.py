import MincData
import Plane
import ObliqueSampler


md = MincData.MincData("data/full8_400um_optbal.mnc")

#md.exportNativeSlice(120, "out/nativeSlice.jpg")
#md.exportNativeSlice(1020, "out/nativeSlice2.jpg")

#md.exportZRotatedSlice(120 , "out/rotateZSlice.jpg")
#md.exportZRotatedSlice2(120 , "out/rotateZSlice2.jpg")

#md.exportYRotatedSlice(120, "yrotate.jpg")
#md.exportZRotatedSlice(120, "zrotate.jpg")
#print md.getSize()
#print md.getValue(200, 150, 165)
#npArray = md.exportToJson("lklk")
#print npArray[200, 150, 165]
#md.exportToJson("data/full8_400um_optbal_2.json")
#print md.getValue(200.5, 150.2, 165.8)
#print md.getValue(200.99, 150.01, 165.99)


p = Plane.Plane()
#p.makeFromThreePoints( (0, 0, 0), (386, 303, 0), (386, 303, 348)) #OK
#p.makeFromThreePoints( (0, 0, 0), (386, 0, 0), (0, 303, 348)) #OK
#p.makeFromThreePoints( (386, 303, 0), (0, 303, 348), (0, 0, 0)) #OK, big triangle
p.makeFromThreePoints( (500, 303, 0), (0, 303, 500), (120, 0, 0)) #OK hexagon



os = ObliqueSampler.ObliqueSampler(md, p)
os.computeCubePlaneHitPoints()
os.startSampling("out/oblique2.jpg")
