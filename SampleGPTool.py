import arcpy, os, arcgis, zipfile
from arcgis import GIS
from arcpy import env

inFeature = arcpy.GetParameterAsText(0)
clipFeature = arcpy.GetParameterAsText(1)
buffDist = arcpy.GetParameterAsText(2)
localDir = arcpy.GetParameterAsText(3)
portal = arcpy.GetParameterAsText(4)
user = arcpy.GetParameterAsText(5)
pw = arcpy.GetParameterAsText(6)
outName = arcpy.GetParameterAsText(7)

env.overwriteOutput = 1

if os.path.exists(r'C:\temp') == False:
    os.mkdir(r'C:\temp')

tempWS = env.scratchWorkspace
stageFolder = r'C:\temp'
tempClip = os.path.join(tempWS, "tempClip")
tempBuff = os.path.join(tempWS, "tempBuff")
tempShp = os.path.join(stageFolder, "tempShp.shp")
outZip = ''

arcpy.AddMessage("Clipping...")
arcpy.Clip_analysis(inFeature, clipFeature, tempClip)
arcpy.AddMessage("Buffering...")
arcpy.Buffer_analysis(tempClip, tempBuff, buffDist)
arcpy.AddMessage("Creating temp file...")
arcpy.CopyFeatures_management(tempBuff, tempShp)


def zipShapefilesInDir(inDir, outDir):
    if not os.path.exists(inDir):
        print("Input directory %s does not exist!" % inDir)
        return False

    if not os.path.exists(outDir):
        print("Creating output directory %s" % outDir)
        os.mkdir(outDir)

    print("Zipping shapefile(s) in folder %s to output folder %s" % (inDir, outDir))

    for inShp in glob.glob(os.path.join(inDir, "*.shp")):
        global outZip
        outZip = os.path.join(outDir, os.path.splitext(os.path.basename(inShp))[0] + ".zip")

        zipShapefile(inShp, outZip)
    return True


def zipShapefile(inShapefile, newZipFN):
    print('Starting to Zip ' + (inShapefile) + ' to ' + (newZipFN))

    if not (os.path.exists(inShapefile)):
        print(inShapefile + ' Does Not Exist')
        return False

    if (os.path.exists(newZipFN)):
        print('Deleting ' + newZipFN)
        os.remove(newZipFN)

    if (os.path.exists(newZipFN)):
        print('Unable to Delete' + newZipFN)
        return False

    zipobj = zipfile.ZipFile(newZipFN, 'w')

    for infile in glob.glob(inShapefile.lower().replace(".shp", ".*")):
        if os.path.splitext(infile)[1].lower() != ".zip":
            print("Zipping %s" % (infile))
            zipobj.write(infile, os.path.basename(infile), zipfile.ZIP_DEFLATED)

    zipobj.close()
    return True

arcpy.AddMessage("Zipping temp file...")
zipShapefilesInDir(stageFolder, localDir)

arcpy.AddMessage("Connecting to portal...")
gis = GIS(url=portal, username=user, password=pw)
arcpy.AddMessage("Adding temp item to portal...")
tempItem = gis.content.add({"title":outName}, outZip)
arcpy.AddMessage("Publishing temp file...")
tempLyr= tempItem.publish(None)

arcpy.AddMessage("Deleting unnecessary files...")
del outZip
arcpy.Delete_management(tempBuff)
arcpy.Delete_management(tempClip)
arcpy.Delete_management(tempShp)