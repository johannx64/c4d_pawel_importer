#Coded by johann9616@gmail.com
#version 0.3

import c4d, re
from c4d import gui
import os
import pathlib

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

# Main function

#2. Edit models human material ex.
	#a) Change specular to GGX
	#b) Change roughness to 100%
	#c) Change Color Profile of roughness map to Linear (ex. Humano_Posed_000111_Roughness_8K.png)
	#d) Change reflection Strenght to 100%
	#e) Add Specular map to Reflection Strenght texture slot (name of the filee is same as the roughness, just there is a name change Rougness>Specular (ex. Humano_Posed_000111_Specular_8K.png))
	#e2) Change Color Profile to Linear
	#f) Change Specular Strenght to 25%
	#g) Change Fresnel to Dielectric
	#h) Change NormalMap Color Profile to Linear
	#EXTRA
    #Black Point (Default 0)
    #White Point (Default 1)
    #For Specular & Roughness maps (in the same place when the Color Profile is changed)
#Version 0.3Right now we've introduced new type of models called Posed Plus. They also have 3d Hair (made with haircards).
# a) The Hair have separate material (that shold have connected following maps: Color, Specular, Roughness, Normal & Alpha - it doesnt work now)(it follows same naming scheme like Accessories).
# b) Now also the Human material has Alpha map - that should be assigned to human material (like for accessories)
# c) both Human & Hair have now also Ambient Occlusion maps - these should be mixed with Color maps with multiply mode (0,3 value / 30%)

def materialEditor():
    return None
    #a
    # Retrieves the selected object in the current document.
#6. All objects should be groupped into one, the name of the group should be same as of the BX file (ex. Humano_Posed_000111_01_LOD0)
def groupObjects():
    doc = c4d.documents.GetActiveDocument()
    c4d.CallCommand(12112) # Select All
    sel=doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_SELECTIONORDER)
    if not sel: 
        print("not objects for selecting")
        return

    null=c4d.BaseObject(c4d.Onull)

    doc.StartUndo()
    doc.AddUndo(c4d.UNDOTYPE_NEW, null)
    doc.InsertObject(null)
    null.InsertBefore(sel[0])

    for x in sel:
        layer=x.GetLayerObject(doc)
        name=x.GetName()
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, x)
        x.InsertUnder(null)

    if layer:
        null.SetLayerObject(layer)
    null.SetName(name)
    doc.SetSelection(null, c4d.SELECTION_NEW)
    doc.EndUndo()
    c4d.EventAdd()

#Merge materials with same name
class matObject:
    matList = []
    def __init__(self, name):
        self.name = name
        self.mats = []
        matObject.matList.append(self)
    def addMat(self, newMat):
        self.mats.append(newMat)

# Functions
def GetNextObject(op):
    if op == None:
        return None
    if op.GetDown():
        return op.GetDown()
    while not op.GetNext() and op.GetUp():
        op = op.GetUp()
    return op.GetNext()

def CollectTextureTags(op):
    tTags = []
    if op is None:
        return
    while op:
        tags = op.GetTags()
        for t in tags:
            if t.IsInstanceOf(c4d.Ttexture):
                tTags.append(t)
        op = GetNextObject(op)
    return tTags

def mergeMats():
    result = ""
    check = False
    errors = ""
    doc = c4d.documents.GetActiveDocument() # Get active Cinema 4D document
    doc.StartUndo() # Start recording undos
    materials = doc.GetMaterials() # Get materials

    # Collect materials
    matObjs = {}
    for i, m in enumerate(materials): # Iterate through materials
        name = re.split("\\.\\d$", m.GetName())[0] # Get name of the material
        #Delete prefix from Export
        exportIndx = name.rfind("ExportMaterial - ")
        if exportIndx > -1: #checking prefix ExportMaterial
            m.SetName(name[name.rfind(" ")+1:])
            name = re.split("\\.\\d$", m.GetName())[0] # Get name of the material
            print(name)
        if name not in matObjs: # If material name not already in matObjs list
            matObjs[name] = matObject(name) # Create a new material
        matObjs[name].addMat(m) # Add material to the material object

    # Assign new materials
    tTags = CollectTextureTags(doc.GetFirstObject()) # Collect all texture tags
    for t in tTags: # Iterate through texture tags
        mat = t[c4d.TEXTURETAG_MATERIAL] # Get material of the texture tag
        for m in matObjs: # Iterate through material objects

            currentName = re.split("\\.\\d$", mat.GetName())[0]
            if matObjs[m].name == currentName:
                doc.AddUndo(c4d.UNDOTYPE_CHANGE, t) # Record undo
                t[c4d.TEXTURETAG_MATERIAL] = matObjs[m].mats[0] # Set new material
                result += "Material with same name merged: " + currentName + "\n"
                check = True

    if check == False:
        errors+="Materials with the same name cannot be found"

    # Deleting materials
    for m in matObjs: # Iterate through material objects
        cnt = len(matObjs[m].mats) # Get count of materials
        for i in range(1, cnt): # Iterate through materials, skipping first one
            mat = matObjs[m].mats[i] # Get the material
            doc.AddUndo(c4d.UNDOTYPE_DELETE, mat) # Record undo
            mat.Remove() # Detele material

    doc.EndUndo() # Stop recording undos
    c4d.EventAdd() # Refresh Cinema 4D
    c4d.CallCommand(12168) # Delete Unused Materials
    print("Merge material with same name result: "+result+ "\n")
    print("Errors: "+errors+ "\n")
    return result, errors

def getExportMats(path):
    #return path[:path.rfind("03_C4D")]+"03_C4D\\03_ExportMaterials\\Humano_MaterialsAR.c4d"    
    #return "C:\\03_C4D\\03_ExportMaterials\\Humano_MaterialsAR.c4d"
    return str(pathlib.Path().resolve()) + "\\03_ExportMaterials\\Humano_MaterialsAR.c4d"
    


def listMats(filename ,path):
    """
    find a file in specific folder
    """
    print("File location using os.getcwd():", os.getcwd())
    pathClean = path[:path.rfind("\\")]
    search_path =  pathClean+"{0}".format("\\")
    result = "Result for Humano Mat "+ filename +" :\n"
    print ("Result for Humano Mat "+ filename)
    # Wlaking top-down from the root
    for root, dir, files in os.walk(search_path):
        files = [x.lower() for x in files]
        for file in files:
            if file.rfind(filename) > 0:
                result=search_path+"{0}".format(file)
    return result

def listMatsAlpha(filename ,path):
    """
    find a file in specific folder
    """
    print("File location using os.getcwd():", os.getcwd())
    pathClean = path[:path.rfind("\\")]
    search_path =  pathClean+"{0}".format("\\")
    result = "Result for Humano Mat "+ filename +" :\n"
    print ("Result for Humano Mat "+ filename)
    # Wlaking top-down from the root
    for root, dir, files in os.walk(search_path):
        files = [x.lower() for x in files]
        for file in files:
            if file.rfind(filename) > 0 and file.rfind("hair") == -1:
                result=search_path+"{0}".format(file)
    return result

def listMatsAcc(filename ,path):
    """
    find a file in specific folder
    """
    #clean name
    nameClean = filename[filename.find("Accessories"):]
    filename = nameClean[:nameClean.find("_")]
    filename = filename.lower()+"_specular"
    print("File location using os.getcwd():", os.getcwd())
    pathClean = path[:path.rfind("\\")]
    search_path =  pathClean+"{0}".format("\\")
    result = ""
    # Wlaking top-down from the root
    for root, dir, files in os.walk(search_path):
        files = [x.lower() for x in files]
        for file in files:
            if file.rfind(filename) > 0:
                result=search_path+"{0}".format(file)
        if result == "":
            for file in files:
                if file.rfind("accessories_specular") > 0:
                    result=search_path+"{0}".format(file)
    print(result)
    return result

def listMatsAccALpha(filename ,path):
    """
    find a file in specific folder
    """
    #clean name
    nameClean = filename[filename.find("Accessories"):]
    filename = nameClean[:nameClean.find("_")]
    filename = filename.lower()+"_alpha"
    print("File location using os.getcwd() for Alpha:", os.getcwd())
    print("#####################")
    print(filename)
    pathClean = path[:path.rfind("\\")]
    search_path =  pathClean+"{0}".format("\\")
    result = ""
    # Wlaking top-down from the root
    for root, dir, files in os.walk(search_path):
        files = [x.lower() for x in files]
        for file in files:
            if file.rfind(filename) > 0:
                result=search_path+"{0}".format(file)
        if result == "":
            for file in files:
                if file.rfind("accessories_alpha") > 0:
                    result=search_path+"{0}".format(file)
    print("Alpha for accesories: "+result)
    return result

def listMatsHair(filename ,path, map):
    """
    find a file in specific folder
    """
    #clean name
    nameClean = filename[filename.find("Hair"):]
    filename = nameClean[:nameClean.find("_")]
    filename = filename.lower()+"_"+map.lower()
    print("File location using os.getcwd() for AO:", os.getcwd())
    print("#####################")
    print(filename)
    pathClean = path[:path.rfind("\\")]
    search_path =  pathClean+"{0}".format("\\")
    result = ""
    # Wlaking top-down from the root
    for root, dir, files in os.walk(search_path):
        files = [x.lower() for x in files]
        for file in files:
            if file.rfind(filename) > 0:
                result=search_path+"{0}".format(file)
        if result == "":
            for file in files:
                if file.rfind("hair"+map.lower()):
                    result=search_path+"{0}".format(file)
    print("AO for Hair: "+result)
    return result


from c4d import storage as s

# Functions
def GetFolderSeparator():
    if c4d.GeGetCurrentOS() == c4d.OPERATINGSYSTEM_WIN: # If operating system is Windows
        return "\\"
    else: # If operating system is Mac or Linux
        return "/"

def main():
    """
    filename = c4d.storage.LoadDialog(c4d.FILESELECTTYPE_SCENES)
    if not filename or not os.path.isfile(filename):
        return


    doc = c4d.documents.LoadDocument(filename, flags)
    if not doc:
        c4d.gui.MessageDialog("The document could not be loaded.")
        return
        
    c4d.documents.InsertBaseDocument(doc)
    c4d.documents.SetActiveDocument(doc)
    c4d.EventAdd()
"""
def createTemplate(path):
    ty = ["\\model_type_1"]
    maps = "\\Maps"
    root = "\\03_C4D"
    sub = "\\01_models"
    exp = "\\03_ExportMaterials"
    fol = ["\\humano_1"]
    #making root folder
    os.mkdir(path+root)
    os.mkdir(path+root+sub)

    #making root folder mats
    os.mkdir(path+root+exp)
    f = open(path+root+exp+"\\PUT MATERIAL TEMPLATE HERE.txt", "x")
    f.close()
    #making model type folders
    for f in ty:
        os.mkdir(path+root+sub+f)
        for m in fol:
            os.mkdir(path+root+sub+f+m)
            ff = open(path+root+sub+f+m+"\\PUT .FBX FILES HERE.txt", "x")
            ff.close()
    for n in fol:
        os.mkdir(path+root+sub+f+n+maps)
    

def main(d=0):
    flags = c4d.SCENEFILTER_OBJECTS | c4d.SCENEFILTER_MATERIALS  | \
            c4d.SCENEFILTER_PROGRESSALLOWED | c4d.SCENEFILTER_NONEWMARKERS | c4d.SCENEFILTER_SAVECACHES

    extensions = ["fbx"] # File extensions that will be imported
    separator = GetFolderSeparator() # Get path separator
    folder = s.LoadDialog(c4d.FILESELECTTYPE_ANYTHING,'Select folder to import',c4d.FILESELECT_DIRECTORY,'') # Load folder
    if not folder:
        gui.MessageDialog('Please select a valid folder')
        return # If there is no folder, stop the script
    #files = os.listdir(folder) # Get files

    #files = os.listdir(folder) # Get files
    print("folder "+folder)
    folders = os.listdir(folder) # Get folders
    folderList =[]
    files = []
    
    if folders == []:
        gui.MessageDialog('Selected folder for import is empty')
        val = c4d.gui.QuestionDialog("Do you want to create a folder template?")
        if val:
            fstruct = s.LoadDialog(c4d.FILESELECTTYPE_ANYTHING,'Select an output folder',c4d.FILESELECT_DIRECTORY,'') # Load folder
            if not fstruct:
                return
            else:
                createTemplate(fstruct)
                return
        else:
            return

    folderOut = s.LoadDialog(c4d.FILESELECTTYPE_ANYTHING,'Select Ouput folder, cancel to save the files in original folder',c4d.FILESELECT_DIRECTORY,'') # Load folder
    overWrite = False
    if not folderOut:
        overWrite = True
        gui.MessageDialog('All the files will saved on the original folder')

    for fol in folders:
        subfolder = os.listdir(folder+"\\"+fol)
        if subfolder == []:
            gui.MessageDialog('Folders are empty, must contain\n folders for each model')
            print('Folders are empty, must contain\n folders for each model')
        for sub in subfolder:
            folderList.append(folder+"\\"+fol+"\\"+sub)
                
    #getting all files
    for fil in folderList:
        fileTemp = os.listdir(fil)
        for ff in fileTemp:
            ext = ""
            ext = ff.rsplit(".",1) # Get file extension
            if len(ext) > 1:
                if ext[1] in extensions: # If extension matches
                    files.append(fil+"\\"+ff)
    for f in files:
        if files == []:
            gui.MessageDialog('Not .fbx files found')    
            return
        doc = c4d.documents.LoadDocument(f, flags)
        c4d.documents.InsertBaseDocument(doc)
        c4d.documents.SetActiveDocument(doc)
        c4d.EventAdd()
        fix_rotation()
        humanoMats()
        mergeMats()
        groupObjects()
        
        name = f[f.rfind("\\"):f.rfind(".")]+".c4d"
        if overWrite: 
            f = f[:f.rfind(".")]+".c4d"           
            print("File saved to : " + f)
            c4d.documents.SaveDocument(doc, f, c4d.SAVEDOCUMENTFLAGS_AUTOSAVE, c4d.FORMAT_C4DEXPORT)
        else:            
            print("File saved to : " + folderOut)
            c4d.documents.SaveDocument(doc, folderOut+name, c4d.SAVEDOCUMENTFLAGS_AUTOSAVE, c4d.FORMAT_C4DEXPORT)
        c4d.documents.KillDocument(doc)
    #c4d.EventAdd() # Update Cinema 4D

def find_material(doc, material_name):
    # Get all materials in the scene
    materials = doc.GetMaterials()

    # Loop through each material and check its name
    for material in materials:
        if material.GetName() == material_name:
            return material

    return None

def rotate_points(points, angle, axis):
    if axis == "y":
        # Create a rotation matrix for the specified angle around the Y axis
        rotation_matrix = c4d.utils.MatrixRotY(angle)

        # Rotate each point by applying the rotation matrix
        rotated_points = [rotation_matrix.Mul(p) for p in points]

        return rotated_points

    if axis == "x":
        # Create a rotation matrix for the specified angle around the Y axis
        rotation_matrix = c4d.utils.MatrixRotX(angle)

        # Rotate each point by applying the rotation matrix
        rotated_points = [rotation_matrix.Mul(p) for p in points]

        return rotated_points

def rotate_obj(obj):
    doc = c4d.documents.GetActiveDocument()
    doc.SetActiveObject(obj, c4d.SELECTION_NEW)
    op = doc.GetActiveObject()
    
    if op is None:
        return

    # Get the points of the object in local coordinates
    ps = op.GetAllPoints()

    # Define the rotation angle (180 degrees in radians)
    rotation_angle = c4d.utils.Rad(180)

    # Rotate the points
    rotated_points = rotate_points(ps, rotation_angle, "y")

    # Set the rotated points back to the object
    op.SetAllPoints(rotated_points)

    # Update the Cinema 4D UI
    c4d.EventAdd()

    # Get the points of the object in local coordinates
    ps = op.GetAllPoints()

    # Define the rotation angle (180 degrees in radians)
    rotation_angle = c4d.utils.Rad(90)

    # Rotate the points
    rotated_points = rotate_points(ps, rotation_angle, "x")

    # Set the rotated points back to the object
    op.SetAllPoints(rotated_points)

    # Update the Cinema 4D UI
    c4d.EventAdd()

    # Update the Cinema 4D UI
    c4d.EventAdd()

def fix_rotation():
    doc = c4d.documents.GetActiveDocument()
    human = doc.GetFirstObject()
    rotate_obj(human)
    # Iterate over the children of the given parent object
    child = human.GetDown()
    while child:
        # Check if the child is valid for your rotation (you can add more conditions)
        if child and child.GetType() == c4d.Opolygon:
            # Rotate the child object
            rotate_obj(child)

        # Move to the next child
        child = child.GetNext()  
    
def humanoMats(blackPRou=0, whitePRou=1, blackPSpec=0, whitePSpec=1):
    result = ""
    c4d.CallCommand(12112) # Select All
    doc = c4d.documents.GetActiveDocument()

    matList = doc.GetMaterials()
    print(matList)
    matHumano = None
    matHair = []
    matAccList = []
    matExport= []
    for mat in matList:
        matStr = str(mat)
        #Setup humano material
        if matStr.rfind("Accessories")== -1 and matStr.rfind("Export") == -1 and matStr.rfind("LOD") > 0 and matStr.rfind("Hair")== -1:
            matHumano = mat
            print("Human"+matStr)
            result+= "Humano Materials: " + str(matStr)+"\n"
        #finding hair mat
        if matStr.rfind("Hair") > 0 and matStr.rfind("Export") == -1 and matStr.rfind("LOD") > 0 and matStr.rfind("Accessories")== -1:
            matHair.append(mat)
            print("Human Hair material"+matStr)
            result+= "Humano Hair Materials: " + str(matStr)+"\n"
        if matStr.rfind("Accessories") > 0 and matStr.rfind("Export") == -1 and matStr.rfind("LOD") > 0 and matStr.rfind("Hair")== -1:
            matAccList.append(mat)
            print("Accessories"+str(matAccList))
        if matStr.rfind("ExportMaterial") > 0 and matStr.rfind("Accessories") == -1 and matStr.rfind("Hair")== -1:
            matExport.append(mat)
            print("Export Material"+str(matExport))

    #a) Change specular to GGX
    if matHumano == None:
        result += "Warning: Not humano materials found!\n"
    layer = matHumano.GetReflectionLayerIndex(0)
    doc.InsertMaterial(matHumano)
    matHumano[layer.GetDataID()+c4d.REFLECTION_LAYER_MAIN_DISTRIBUTION]=3
    doc.InsertMaterial(matHumano)
    c4d.EventAdd()

    result += "Specular type: {0}".format(str(matHumano[layer.GetDataID()+c4d.REFLECTION_LAYER_MAIN_DISTRIBUTION])+"\n")
    #b Change roughness to 100%
    matHumano[layer.GetDataID()+c4d.REFLECTION_LAYER_MAIN_VALUE_ROUGHNESS] = 1
    result += "Roughness: {0}".format(str(matHumano[layer.GetDataID()+c4d.REFLECTION_LAYER_MAIN_VALUE_ROUGHNESS])+"\n")


    m = matHumano[layer.GetDataID()+c4d.REFLECTION_LAYER_MAIN_SHADER_ROUGHNESS]
    #set Color Profile, flag, value
    #c) Change Color Profile of roughness map to Linear (ex. Humano_Posed_000111_Roughness_8K.png)
    rou = m.SetParameter(c4d.BITMAPSHADER_COLORPROFILE, 1, 1)

    #EXTRA flag, value
    m.SetParameter(c4d.BITMAPSHADER_BLACKPOINT, blackPRou, 1)
    m.SetParameter(c4d.BITMAPSHADER_WHITEPOINT, whitePRou, 1)
    result += "Color Profile: {0}".format(str(m.GetParameter(c4d.BITMAPSHADER_COLORPROFILE,1))+"\n")
    result += "Roughness Black Point: {0}".format(str(m.GetParameter(c4d.BITMAPSHADER_BLACKPOINT,1))+"\n")
    result += "Roughness White Point: {0}".format(str(m.GetParameter(c4d.BITMAPSHADER_WHITEPOINT,1))+"\n")

    #d) Change reflection Strenght to 100%
    matHumano[layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_VALUE_REFLECTION] = 1
    result += "Reflection Strength: {0}".format(str(matHumano[layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_VALUE_REFLECTION])+"\n")

    #e) Add Specular map to Reflection Strenght texture slot
    refStr = matHumano[layer.GetDataID() +c4d.REFLECTION_LAYER_MAIN_SHADER_REFLECTION]

    #get specular mats for humano
    matFolder = m.GetParameter(c4d.BITMAPSHADER_FILENAME, 1)
    specPath = listMats("specular",matFolder)
    
    if specPath != "":
        print("Specular Map for Material " + matHumano.GetName())
        print(specPath)
        mat = find_material(doc, matHumano.GetName())
        layer = mat.GetReflectionLayerIndex(0)
        # 2. The bitmap shader.
        shader = c4d.BaseShader(c4d.Xbitmap)
        shader[c4d.BITMAPSHADER_FILENAME] = specPath
        
        # 3. Add the shader to the material.
        #matHumano[layer.GetDataID() +c4d.REFLECTION_LAYER_MAIN_SHADER_REFLECTION] = shader
        mat[layer.GetDataID() +c4d.REFLECTION_LAYER_MAIN_SHADER_SPECULAR] = shader
        #Setup Specular Strength value
        mat[layer.GetDataID()+c4d.REFLECTION_LAYER_MAIN_VALUE_SPECULAR] = 0.4
        mat.InsertShader(shader)
        #set specular map
        #refStr.SetParameter(c4d.BITMAPSHADER_FILENAME, 1, specPath)
        #e2) Change Color Profile to Linear
        refStr = matHumano[layer.GetDataID() +c4d.REFLECTION_LAYER_MAIN_SHADER_SPECULAR]
        refStr.SetParameter(c4d.BITMAPSHADER_COLORPROFILE, 1, 1)
        c4d.EventAdd()
        
        result += "Color Profile: {0}".format(str(refStr.GetParameter(c4d.BITMAPSHADER_COLORPROFILE, 1))+"\n")
    else:
        result += "No shader map for Reflection Strength"

    #get specular mats for humano

    #EXTRA WHITE / BLACK POINT
    refStr.SetParameter(c4d.BITMAPSHADER_BLACKPOINT, blackPSpec, 1)
    refStr.SetParameter(c4d.BITMAPSHADER_WHITEPOINT, whitePSpec, 1)
    result += "Reflection Black Point: {0}".format(str(refStr.GetParameter(c4d.BITMAPSHADER_BLACKPOINT,1))+"\n")
    result += "Reflection White Point: {0}".format(str(refStr.GetParameter(c4d.BITMAPSHADER_WHITEPOINT,1))+"\n")
    #f
    matHumano[layer.GetDataID()+c4d.REFLECTION_LAYER_MAIN_VALUE_SPECULAR] = 0.25
    result += "Specular Strenght: {0}".format(str(matHumano[layer.GetDataID()+c4d.REFLECTION_LAYER_MAIN_VALUE_SPECULAR])+"\n")

    #g
    matHumano[layer.GetDataID()+c4d.REFLECTION_LAYER_FRESNEL_MODE] = 1
    result += "Fresnel: {0}".format(str(matHumano[layer.GetDataID()+c4d.REFLECTION_LAYER_FRESNEL_MODE])+"\n")

    #extra setup color layer brigh
    matHumano[layer.GetDataID()+c4d.REFLECTION_LAYER_COLOR_BRIGHTNESS] = 0.25
    result += "Color Brightness: {0}".format(str(matHumano[layer.GetDataID()+c4d.REFLECTION_LAYER_FRESNEL_MODE])+"\n")

    #h NormalMap Color Profile MATERIAL_NORMAL_STRENGTH MATERIAL_NORMAL_SHADER
    #print(result)
    normalShader = matHumano.GetParameter(c4d.MATERIAL_NORMAL_SHADER, 1)
    normalShader.SetParameter(c4d.BITMAPSHADER_COLORPROFILE, 1, 1)
    result += "Normal Color Profile: {0}".format(str(normalShader.GetParameter(c4d.BITMAPSHADER_COLORPROFILE, 1))+"\n\n")

    #Alpha channel for Humano
    humano_alpha_path = listMatsAlpha("alpha",matFolder)

    if humano_alpha_path != "":
        if matHumano[c4d.MATERIAL_USE_ALPHA] == False:
            matHumano[c4d.MATERIAL_USE_ALPHA] = True
            print("Alpha channel Enabled")

        alpha = c4d.BaseShader(c4d.Xbitmap)
        alpha[c4d.BITMAPSHADER_FILENAME] = humano_alpha_path

        print("ALPHA ALERT")
        print(alpha)
#            matHumano.InsertShader(alpha)
        matHumano.Message(c4d.MSG_UPDATE)
        matHumano.Update(1,1)
        c4d.EventAdd()
        # 3. Add the shader to the material.
        matHumano[layer.GetDataID() +c4d.MATERIAL_ALPHA_SHADER] = alpha
        #set specular map
        matHumano.SetParameter(c4d.MATERIAL_ALPHA_SHADER, alpha, c4d.DESCFLAGS_SET_NONE)
        matHumano.InsertShader(alpha)
        c4d.EventAdd()

        #e2) Change Color Profile to Linear
        refStrAlpha = matHumano[layer.GetDataID() +c4d.MATERIAL_ALPHA_SHADER]
        refStrAlpha.SetParameter(c4d.BITMAPSHADER_COLORPROFILE, 1, 1)
        result += "Color Profile Alpha: {0}".format(str(refStrAlpha.GetParameter(c4d.BITMAPSHADER_COLORPROFILE, 1))+"\n")
    else:
        result += "No Alpha map for alpha channel\n"

    #AO channel for Humano
    humano_AO_path = listMatsAlpha("_ao_",matFolder)

    if humano_AO_path != "":
        if matHumano[c4d.MATERIAL_USE_DIFFUSION] == False:
            matHumano[c4d.MATERIAL_USE_DIFFUSION] = True
            print("AO (Difusse) channel Enabled")

        diffuse_AO = c4d.BaseShader(c4d.Xbitmap)
        diffuse_AO[c4d.BITMAPSHADER_FILENAME] = humano_AO_path

        print("AO ALERT")
        print(diffuse_AO)
#            matHumano.InsertShader(diffuse_AO)
        matHumano.Message(c4d.MSG_UPDATE)
        matHumano.Update(1,1)
        c4d.EventAdd()
        # 3. Add the shader to the material.
        matHumano[layer.GetDataID() +c4d.MATERIAL_DIFFUSION_SHADER] = diffuse_AO
        #set diffuse AO
        matHumano.SetParameter(c4d.MATERIAL_DIFFUSION_SHADER, diffuse_AO, c4d.DESCFLAGS_SET_NONE)
        matHumano.SetParameter(c4d.MATERIAL_DIFFUSION_TEXTUREMIXING, 3 , 1)
        matHumano.SetParameter(c4d.MATERIAL_DIFFUSION_TEXTURESTRENGTH, 0.3, 1)
        matHumano.InsertShader(diffuse_AO)
        c4d.EventAdd()

        #e2) Change Color Profile to sRGB
        refStrAlpha = matHumano[layer.GetDataID() +c4d.MATERIAL_DIFFUSION_SHADER]
        refStrAlpha.SetParameter(c4d.BITMAPSHADER_COLORPROFILE, 2, 1)
        result += "Color Profile AO (Diffuse): {0}".format(str(refStrAlpha.GetParameter(c4d.BITMAPSHADER_COLORPROFILE, 1))+"\n")
    else:
        result += "No AO (Diffuse) map for channel\n"
    #------------------------------------------------#
    #Accesories setup
    for matAcc in matAccList:
        matAcc[layer.GetDataID()+c4d.REFLECTION_LAYER_MAIN_DISTRIBUTION]=3
        result += "Result for Accesories Mat :"+str(matAcc)+"\n"

        #a) Change specular to GGX
        layer = matAcc.GetReflectionLayerIndex(0)
        doc.InsertMaterial(matAcc)
        doc.InsertMaterial(matAcc)
        c4d.EventAdd()

        result += "Specular type: {0}".format(str(matAcc[layer.GetDataID()+c4d.REFLECTION_LAYER_MAIN_DISTRIBUTION])+"\n")

        #b Change roughness to 100%
        matAcc[layer.GetDataID()+c4d.REFLECTION_LAYER_MAIN_VALUE_ROUGHNESS] = 1
        result += "Roughness: {0}".format(str(matAcc[layer.GetDataID()+c4d.REFLECTION_LAYER_MAIN_VALUE_ROUGHNESS])+"\n")

        m = matAcc[layer.GetDataID()+c4d.REFLECTION_LAYER_MAIN_SHADER_ROUGHNESS]
        #set Color Profile, flag, value
        #c) Change Color Profile of roughness map to Linear (ex. Humano_Posed_000111_Roughness_8K.png)
        specPath = ""
        alpPath = ""
        if m != None:
            rou = m.SetParameter(c4d.BITMAPSHADER_COLORPROFILE, 1, 1)

            #EXTRA flag, value
            m.SetParameter(c4d.BITMAPSHADER_BLACKPOINT, blackPRou, 1)
            m.SetParameter(c4d.BITMAPSHADER_WHITEPOINT, whitePRou, 1)
            result += "Color Profile: {0}".format(str(m.GetParameter(c4d.BITMAPSHADER_COLORPROFILE,1))+"\n")
            result += "Roughness Black Point: {0}".format(str(m.GetParameter(c4d.BITMAPSHADER_BLACKPOINT,1))+"\n")
            result += "Roughness White Point: {0}".format(str(m.GetParameter(c4d.BITMAPSHADER_WHITEPOINT,1))+"\n")

            #d) Change reflection Strenght to 100%
            matAcc[layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_VALUE_REFLECTION] = 1
            result += "Reflection Strength: {0}".format(str(matAcc[layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_VALUE_REFLECTION])+"\n")

            #e) Add Specular map to Reflection Strenght texture slot
            refStr = matAcc[layer.GetDataID() +c4d.REFLECTION_LAYER_MAIN_SHADER_REFLECTION]
            refStrAlpha = matAcc[layer.GetDataID() +c4d.MATERIAL_ALPHA_SHADER]
            #get folder
            matFolder = m.GetParameter(c4d.BITMAPSHADER_FILENAME, 1)
            specPath = listMatsAcc(str(matAcc),matFolder)
            print(specPath)

            alpPath = listMatsAccALpha(str(matAcc),matFolder)
            print(alpPath)
        # 2. The bitmap shader.
        if specPath != "":
            shader = c4d.BaseShader(c4d.Xbitmap)
            shader[c4d.BITMAPSHADER_FILENAME] = specPath
            matAcc.InsertShader(shader)
            # 3. Add the shader to the material.
            matAcc[layer.GetDataID() +c4d.REFLECTION_LAYER_MAIN_SHADER_REFLECTION] = shader
            #set specular map
            #refStr.SetParameter(c4d.BITMAPSHADER_FILENAME, 1, specPath)
            #e2) Change Color Profile to Linear
            refStr = matAcc[layer.GetDataID() +c4d.REFLECTION_LAYER_MAIN_SHADER_REFLECTION]
            refStr.SetParameter(c4d.BITMAPSHADER_COLORPROFILE, 1, 1)
            result += "Color Profile: {0}".format(str(refStr.GetParameter(c4d.BITMAPSHADER_COLORPROFILE, 1))+"\n")
        else:
            result += "No shader map for Reflection Strength\n"
        # 2. The bitmap alpha.
        if alpPath != "":
            if matAcc[c4d.MATERIAL_USE_ALPHA] == False:
                matAcc[c4d.MATERIAL_USE_ALPHA] = True
                print("Alpha channel Enabled")
            alpha = c4d.BaseShader(c4d.Xbitmap)
            alpha[c4d.BITMAPSHADER_FILENAME] = alpPath

            print("ALPHA ALERT")
            print(alpha)
#            matAcc.InsertShader(alpha)
            matAcc.Message(c4d.MSG_UPDATE)
            matAcc.Update(1,1)
            c4d.EventAdd()
            # 3. Add the shader to the material.
            matAcc[layer.GetDataID() +c4d.MATERIAL_ALPHA_SHADER] = alpha
            #set specular map
            matAcc.SetParameter(c4d.MATERIAL_ALPHA_SHADER, alpha, c4d.DESCFLAGS_SET_NONE)
            matAcc.InsertShader(alpha)
            c4d.EventAdd()

            #e2) Change Color Profile to Linear
            refStrAlpha = matAcc[layer.GetDataID() +c4d.MATERIAL_ALPHA_SHADER]
            refStrAlpha.SetParameter(c4d.BITMAPSHADER_COLORPROFILE, 1, 1)
            result += "Color Profile Alpha: {0}".format(str(refStrAlpha.GetParameter(c4d.BITMAPSHADER_COLORPROFILE, 1))+"\n")
        else:
            result += "No Alpha map for alpha channel\n"
            
        #EXTRA WHITE / BLACK POINT
        refStr.SetParameter(c4d.BITMAPSHADER_BLACKPOINT, blackPSpec, 1)
        refStr.SetParameter(c4d.BITMAPSHADER_WHITEPOINT, whitePSpec, 1)
        result += "Reflection Black Point: {0}".format(str(refStr.GetParameter(c4d.BITMAPSHADER_BLACKPOINT,1))+"\n")
        result += "Reflection White Point: {0}".format(str(refStr.GetParameter(c4d.BITMAPSHADER_WHITEPOINT,1))+"\n")

        #f
        refStr[layer.GetDataID()+c4d.REFLECTION_LAYER_MAIN_VALUE_SPECULAR] = 0.25
        result += "Specular Strenght: {0}".format(str(refStr[layer.GetDataID()+c4d.REFLECTION_LAYER_MAIN_VALUE_SPECULAR])+"\n")

        #g
        matAcc[layer.GetDataID()+c4d.REFLECTION_LAYER_FRESNEL_MODE] = 1
        result += "Fresnel: {0}".format(str(matAcc[layer.GetDataID()+c4d.REFLECTION_LAYER_FRESNEL_MODE])+"\n")

        #extra setup color layer brigh
        matAcc[layer.GetDataID()+c4d.REFLECTION_LAYER_COLOR_BRIGHTNESS] = 0.25
        result += "Color Brightness: {0}".format(str(matAcc[layer.GetDataID()+c4d.REFLECTION_LAYER_FRESNEL_MODE])+"\n")

        #h NormalMap Color Profile MATERIAL_NORMAL_STRENGTH MATERIAL_NORMAL_SHADER
        #print(result)
        normalShader = matAcc.GetParameter(c4d.MATERIAL_NORMAL_SHADER, 1)

        if normalShader != None:
            normalShader.SetParameter(c4d.BITMAPSHADER_COLORPROFILE, 1, 1)
            result += "Normal Color Profile: {0}".format(str(normalShader.GetParameter(c4d.BITMAPSHADER_COLORPROFILE, 1))+"\n\n")
        else:
            result+= "No Normal Map\n"
    #material humano / accessories result data  
    #----------------------------------------Accesories setup end------------------------------------------------#
    
    #----------------------Hair setup--------------------------#
    for matAcc in matHair:
        matAcc[layer.GetDataID()+c4d.REFLECTION_LAYER_MAIN_DISTRIBUTION]=3
        result += "Result for Accesories Mat :"+str(matAcc)+"\n"

        #a) Change specular to GGX
        layer = matAcc.GetReflectionLayerIndex(0)
        doc.InsertMaterial(matAcc)
        doc.InsertMaterial(matAcc)
        c4d.EventAdd()

        result += "Specular type: {0}".format(str(matAcc[layer.GetDataID()+c4d.REFLECTION_LAYER_MAIN_DISTRIBUTION])+"\n")

        #b Change roughness to 100%
        matAcc[layer.GetDataID()+c4d.REFLECTION_LAYER_MAIN_VALUE_ROUGHNESS] = 1
        result += "Roughness: {0}".format(str(matAcc[layer.GetDataID()+c4d.REFLECTION_LAYER_MAIN_VALUE_ROUGHNESS])+"\n")

        m = matAcc[layer.GetDataID()+c4d.REFLECTION_LAYER_MAIN_SHADER_ROUGHNESS]
        #set Color Profile, flag, value
        #c) Change Color Profile of roughness map to Linear (ex. Humano_Posed_000111_Roughness_8K.png)
        specPath = ""
        alpPath = ""
        if m != None:
            rou = m.SetParameter(c4d.BITMAPSHADER_COLORPROFILE, 1, 1)

            #EXTRA flag, value
            m.SetParameter(c4d.BITMAPSHADER_BLACKPOINT, blackPRou, 1)
            m.SetParameter(c4d.BITMAPSHADER_WHITEPOINT, whitePRou, 1)
            result += "Color Profile: {0}".format(str(m.GetParameter(c4d.BITMAPSHADER_COLORPROFILE,1))+"\n")
            result += "Roughness Black Point: {0}".format(str(m.GetParameter(c4d.BITMAPSHADER_BLACKPOINT,1))+"\n")
            result += "Roughness White Point: {0}".format(str(m.GetParameter(c4d.BITMAPSHADER_WHITEPOINT,1))+"\n")

            #d) Change reflection Strenght to 100%
            matAcc[layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_VALUE_REFLECTION] = 1
            result += "Reflection Strength: {0}".format(str(matAcc[layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_VALUE_REFLECTION])+"\n")

            #e) Add Specular map to Reflection Strenght texture slot
            refStr = matAcc[layer.GetDataID() +c4d.REFLECTION_LAYER_MAIN_SHADER_REFLECTION]
            refStrAlpha = matAcc[layer.GetDataID() +c4d.MATERIAL_ALPHA_SHADER]
            #get folder
            matFolder = m.GetParameter(c4d.BITMAPSHADER_FILENAME, 1)
        
            specPath = listMatsHair(str(matAcc),matFolder,"Specular")
            print(specPath)

            alpPath = listMatsHair(str(matAcc),matFolder, "Alpha")
            print(alpPath)
        # 2. The bitmap shader.
        if specPath != "":
            shader = c4d.BaseShader(c4d.Xbitmap)
            shader[c4d.BITMAPSHADER_FILENAME] = specPath
            matAcc.InsertShader(shader)
            # 3. Add the shader to the material.
            matAcc[layer.GetDataID() +c4d.REFLECTION_LAYER_MAIN_SHADER_REFLECTION] = shader
            #set specular map
            #refStr.SetParameter(c4d.BITMAPSHADER_FILENAME, 1, specPath)
            #e2) Change Color Profile to Linear
            refStr = matAcc[layer.GetDataID() +c4d.REFLECTION_LAYER_MAIN_SHADER_REFLECTION]
            refStr.SetParameter(c4d.BITMAPSHADER_COLORPROFILE, 1, 1)
            result += "Color Profile: {0}".format(str(refStr.GetParameter(c4d.BITMAPSHADER_COLORPROFILE, 1))+"\n")
        else:
            result += "No shader map for Reflection Strength\n"
        # 2. The bitmap alpha.
        if alpPath != "":
            if matAcc[c4d.MATERIAL_USE_ALPHA] == False:
                matAcc[c4d.MATERIAL_USE_ALPHA] = True
                print("Alpha channel Enabled")
            alpha = c4d.BaseShader(c4d.Xbitmap)
            alpha[c4d.BITMAPSHADER_FILENAME] = alpPath

            print("ALPHA ALERT")
            print(alpha)
#            matAcc.InsertShader(alpha)
            matAcc.Message(c4d.MSG_UPDATE)
            matAcc.Update(1,1)
            c4d.EventAdd()
            # 3. Add the shader to the material.
            matAcc[layer.GetDataID() +c4d.MATERIAL_ALPHA_SHADER] = alpha
            #set specular map
            matAcc.SetParameter(c4d.MATERIAL_ALPHA_SHADER, alpha, c4d.DESCFLAGS_SET_NONE)
            matAcc.InsertShader(alpha)
            c4d.EventAdd()

            #e2) Change Color Profile to Linear
            refStrAlpha = matAcc[layer.GetDataID() +c4d.MATERIAL_ALPHA_SHADER]
            refStrAlpha.SetParameter(c4d.BITMAPSHADER_COLORPROFILE, 1, 1)
            result += "Color Profile Alpha: {0}".format(str(refStrAlpha.GetParameter(c4d.BITMAPSHADER_COLORPROFILE, 1))+"\n")
        else:
            result += "No Alpha map for alpha channel\n"
        
        #AO channel for Hair
        hair_AO_path = listMatsHair(str(matAcc), matFolder, "AO_")

        if hair_AO_path != "":
            if matAcc[c4d.MATERIAL_USE_DIFFUSION] == False:
                matAcc[c4d.MATERIAL_USE_DIFFUSION] = True
                print("AO (Difusse) channel Enabled for Hair")

            diffuse_AO_hair = c4d.BaseShader(c4d.Xbitmap)
            diffuse_AO_hair[c4d.BITMAPSHADER_FILENAME] = hair_AO_path

            print("AO ALERT HAIR")
            print(diffuse_AO_hair)
    #            matAcc.InsertShader(diffuse_AO_hair)
            matAcc.Message(c4d.MSG_UPDATE)
            matAcc.Update(1,1)
            c4d.EventAdd()
            # 3. Add the shader to the material.
            matAcc[layer.GetDataID() +c4d.MATERIAL_DIFFUSION_SHADER] = diffuse_AO_hair
            #set diffuse AO
            matAcc.SetParameter(c4d.MATERIAL_DIFFUSION_SHADER, diffuse_AO_hair, c4d.DESCFLAGS_SET_NONE)
            #Blend mode normal
            matAcc.SetParameter(c4d.MATERIAL_DIFFUSION_TEXTUREMIXING, 0 , 1)
            matAcc.SetParameter(c4d.MATERIAL_DIFFUSION_TEXTURESTRENGTH, 0.3, 1)
            matAcc.InsertShader(diffuse_AO_hair)
            c4d.EventAdd()

            #e2) Change Color Profile to sRGB
            refStrAlpha = matAcc[layer.GetDataID() +c4d.MATERIAL_DIFFUSION_SHADER]
            refStrAlpha.SetParameter(c4d.BITMAPSHADER_COLORPROFILE, 2, 1)
            result += "Color Profile AO (Diffuse): {0}".format(str(refStrAlpha.GetParameter(c4d.BITMAPSHADER_COLORPROFILE, 1))+"\n")
        else:
            result += "No AO (Diffuse) map for channel\n"
        #EXTRA WHITE / BLACK POINT
        refStr.SetParameter(c4d.BITMAPSHADER_BLACKPOINT, blackPSpec, 1)
        refStr.SetParameter(c4d.BITMAPSHADER_WHITEPOINT, whitePSpec, 1)
        result += "Reflection Black Point: {0}".format(str(refStr.GetParameter(c4d.BITMAPSHADER_BLACKPOINT,1))+"\n")
        result += "Reflection White Point: {0}".format(str(refStr.GetParameter(c4d.BITMAPSHADER_WHITEPOINT,1))+"\n")

        #f
        refStr[layer.GetDataID()+c4d.REFLECTION_LAYER_MAIN_VALUE_SPECULAR] = 0.25
        result += "Specular Strenght: {0}".format(str(refStr[layer.GetDataID()+c4d.REFLECTION_LAYER_MAIN_VALUE_SPECULAR])+"\n")

        #g
        matAcc[layer.GetDataID()+c4d.REFLECTION_LAYER_FRESNEL_MODE] = 1
        result += "Fresnel: {0}".format(str(matAcc[layer.GetDataID()+c4d.REFLECTION_LAYER_FRESNEL_MODE])+"\n")

        #extra setup color layer brigh
        matAcc[layer.GetDataID()+c4d.REFLECTION_LAYER_COLOR_BRIGHTNESS] = 0.25
        result += "Color Brightness: {0}".format(str(matAcc[layer.GetDataID()+c4d.REFLECTION_LAYER_FRESNEL_MODE])+"\n")

        #h NormalMap Color Profile MATERIAL_NORMAL_STRENGTH MATERIAL_NORMAL_SHADER
        #print(result)
        normalShader = matAcc.GetParameter(c4d.MATERIAL_NORMAL_SHADER, 1)

        if normalShader != None:
            normalShader.SetParameter(c4d.BITMAPSHADER_COLORPROFILE, 1, 1)
            result += "Normal Color Profile: {0}".format(str(normalShader.GetParameter(c4d.BITMAPSHADER_COLORPROFILE, 1))+"\n\n")
        else:
            result+= "No Normal Map\n"
    #material humano / accessories result data  
    #----------------------------------------Accesories setup end------------------------------------------------#
    
    #4. Look for the Materials with "ExportMaterial" in its name,
    #if there is any, materials from Humano_MaterialsAR.c4d should be merged into the file
    if len(matExport) > 0:
        exportFile = getExportMats(matFolder)
        merge = c4d.documents.MergeDocument(doc,exportFile, c4d.SCENEFILTER_MATERIALS) # Load Materials...
        if merge == True:
            result += "Load Materials From: " + exportFile + "\n"
        else:
            result += "Unable to Load Materials From: " + exportFile + "\n"

    #
    print(result)
    return result
# Execute main()
#def main(data=1):
 #   print("ExporterMat running...")
  #  main()
    #humanoMats()
    #humanoMats(blackPRou=data["rouBlack"], whitePRou=["rouWhite"], blackPSpec=["refBlack"], whitePSpec=["refWhite"])
    #mergeMats()
    #groupObjects()

if __name__=='__main__':
    main()