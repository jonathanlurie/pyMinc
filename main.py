import MincReader


mr = MincReader.MincReader("data/full8_400um_optbal.mnc")

#mr.exportSlice(120, "hello2.jpg")
#mr.exportYRotatedSlice(120, "yrotate.jpg")
#mr.exportZRotatedSlice(120, "zrotate.jpg")
#print mr.getSize()
#print mr.getValue(200, 150, 165)
#npArray = mr.exportToJson("lklk")
#print npArray[200, 150, 165]

#mr.exportToJson("data/full8_400um_optbal_2.json")


#print mr.getValue(200.5, 150.2, 165.8)

print mr.getValue(200.99, 150.01, 165.99)
