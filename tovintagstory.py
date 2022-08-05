﻿import c4d
from c4d import gui
from c4d import documents
#Cinema4d -> Vintage Story Model Creator Script v1.0
#Created by Quentin of QPTech
#polygon objects will be exported as cuboids, basicaly by there AABB
#textures are currently assigned by the name of the material tag, note only one directory level is currently accepted (ie just block/mytexture)
#  uvs not supported yet - but if you name a texture tag a direction (north, east, south, west, up, or down), that material/texture will only be applied to that face in VSMC
#anything you don't want exported - make sure it is named scene or at least its parent is
#any non polygon objects will be exported as a zero size, no face cuboid and can be used for grouping
#results are written to the console and can be pasted into your json file (just remove the >>> from end of file)
objectnumber=0
radtodeg=57.2958
def test(texty):
    gui.MessageDialog(texty)

def getfromv(points):
    minx=9999
    miny=9999
    minz=9999
    maxx=-9999
    maxy=-9999
    maxz=-9999
    for p in points:
        if p.x<minx: minx=p.x
        if p.y<miny: miny=p.y
        if p.z<minz: minz=p.z
        if p.x>maxx: maxx=p.x
        if p.y>maxy: maxy=p.y
        if p.z>maxz: maxz=p.z
    retvector=c4d.Vector(minx,miny,minz)
    return retvector
def gettov(points):
    minx=9999
    miny=9999
    minz=9999
    maxx=-9999
    maxy=-9999
    maxz=-9999
    for p in points:
        if p.x<minx: minx=p.x
        if p.y<miny: miny=p.y
        if p.z<minz: minz=p.z
        if p.x>maxx: maxx=p.x
        if p.y>maxy: maxy=p.y
        if p.z>maxz: maxz=p.z
    retvector=c4d.Vector(maxx,maxy,maxz)
    return retvector
def addelement(c,offset):
    global objectnumber
    global radtodeg
    json=""
    json+=' {\n'
    json+='  "name" : "%s%i",\n'%(c.GetName(),objectnumber)
    objectnumber+=1

    #find all the coordinates information (sort of a bounding box)
    startpos=c.GetAbsPos()
    tov = c4d.Vector(0)+offset
    fromv = c4d.Vector(0)+offset
    size = c4d.Vector(0)
    enabled="false"
    if type(c)==c4d.PolygonObject:
        points=c.GetAllPoints()
        fromv = getfromv(points)
        tov = gettov(points)
        enabled="true"
    else:
        fromv=0
        tov=0
    fromv+=startpos+offset
    tov+=startpos+offset
    size=tov-fromv
    #face information

    #handle rotation information
    rotation=c.GetAbsRot()
    rotation.x*=-radtodeg #H or y rotation in VS
    rotation.y*=-radtodeg #P or x rotation in VS
    rotation.z*=-radtodeg #B or z rotation in VS
    origin=startpos+offset
    #find texture information
    tags=c.GetTags()
    texture =''
    northtexture=''
    easttexture=''
    southtexture=''
    westtexture=''
    uptexture=''
    downtexture=''
    for tag in tags:
       if type(tag)==c4d.TextureTag:
           tagname=tag.GetName()
           t=tag.GetMaterial().GetName()
           t=t.split("/",1)[1]
           if tagname=='north':northtexture=t
           elif tagname=='east':easttexture=t
           elif tagname=='south':southtexture=t
           elif tagname=='west':westtexture=t
           elif tagname=='up':uptexture=t
           elif tagname=='down':downtexture=t
           else: texture=t
       if northtexture=='':northtexture=texture
       if easttexture=='':easttexture=texture
       if southtexture=='':southtexture=texture
       if westtexture=='':westtexture=texture
       if uptexture=='':uptexture=texture
       if downtexture=='':downtexture=texture
    json+=('  "from": [ %f, %f, %f ],\n'%(fromv.x,fromv.y,fromv.z))
    json+='  "to": [ %f, %f, %f ],\n'%(tov.x,tov.y,tov.z)
    json+='  "rotationOrigin": [ %f, %f, %f ],\n'%(origin.x,origin.y,origin.z)
    json+='  "rotationY": %f,\n'%rotation.x
    json+='  "rotationX": %f,\n'%rotation.y
    json+='  "rotationZ": %f,\n'%rotation.z
    json+='  "faces": {\n'
    json+='    "north": { "texture": "#%s", "uv": [ 0.0, 0.0, 16.0, 16.0 ], "enabled": %s },\n'%(northtexture,enabled)
    json+='    "east": { "texture": "#%s", "uv": [ 0.0, 0.0, 16.0, 16.0 ], "enabled": %s },\n'%(easttexture,enabled)
    json+='    "south": { "texture": "#%s", "uv": [ 0.0, 0.0, 16.0, 16.0 ], "enabled": %s },\n'%(southtexture,enabled)
    json+='    "west": { "texture": "#%s", "uv": [ 0.0, 0.0, 16.0, 16.0 ], "enabled": %s },\n'%(westtexture,enabled)
    json+='    "up": { "texture": "#%s", "uv": [ 0.0, 0.0, 16.0, 16.0 ], "enabled": %s },\n'%(uptexture,enabled)
    json+='    "down": { "texture": "#%s", "uv": [ 0.0, 0.0, 16.0, 16.0 ], "enabled": %s }\n'%(downtexture,enabled)
    json+='   }\n'
    #check for children
    children=c.GetChildren()
    if len(children)>0:
        json+=',"children": ['
        for child in children:
            if child.GetName()=="scene": continue
            childoffset=size/2
            json+=addelement(child,childoffset)
        json +="]"
    json+='  }'
    json+=","
    return json
def main():

    #start of json and header
    json="{\n"
    json+='"editor": {"allAngles": false,"entityTextureMode": false},\n'
    json+='"textureWidth": 16,\n"textureHeight": 16,\n"textureSizes": {},\n'

    #material definition
    json+='"textures": {\n'
    actmat = c4d.documents.GetActiveDocument().GetMaterials()
    listctr=0;
    for x in actmat:
      fullname=x.GetName()
      json += ' "'+fullname.split("/",1)[1]+'" :'+'"'+fullname+'"'
      listctr+=1
      if (listctr<len(actmat)):
          json+=',\n'
      else:
          json+='\n'
    json+='},\n'

    #elements - will have to also go thru each sub element
    json+='"elements": [\n'
    actsel = c4d.documents.GetActiveDocument().GetObjects()
    listctr=0;

    for c in actsel:
        if c.GetName()=="scene": continue
        json+=addelement(c,c4d.Vector(0))

        #setup each object as a cuboid

    json+='\n]\n'
    #end of json
    json+="}"

    #final output
    print (json);

if __name__=='__main__':
    main()