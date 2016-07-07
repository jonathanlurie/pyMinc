import MincData
import Plane
import ObliqueSampler


md = MincData.MincData("data/full8_400um_optbal.mnc")

#md.exportSlice(120, "hello2.jpg")
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
p.makeFromThreePoints( (0, 0, 0), (386, 0, 0), (0, 303, 348)) #OK
#p.makeFromThreePoints( (0, 0, 0), (386, 0, 0), (100, 303, 348)) #OK
#p.makeFromThreePoints( (0, 0, 0), (386, 0, 0), (0, 303, 100)) #OK
#p.makeFromThreePoints( (3, 280, 5), (9, 295, 52), (32, 295, 2)) #OK

#p.makeFromThreePoints( (0, 303, 300), (350, 303, 0), (350, 0, 0)) #OK
#p.makeFromThreePoints( (0, 303, 300), (350, 303, 0), (0, 10, 0)) #OK



os = ObliqueSampler.ObliqueSampler(md, p)
os.computeCubePlaneHitPoints()
os.startSampling("out.jpg")
