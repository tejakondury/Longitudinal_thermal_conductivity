import os
tts=os.environ['tt']
tt=float(tts)
# Abaqus modules
from abaqus import *
from abaqusConstants import *
from caeModules import *

# Python modules
import os
import numpy as np
import pickle as pk

f=open('norm%d'%tt,'r')
cond_mat_var=f.read()
cond_mat_var=float(cond_mat_var)
f.close()

f=open('fib-cond%d'%tt,'r')
cond_fib_var=f.read()
cond_fib_var=float(cond_fib_var)
f.close()

# read coordinate values from reference space

Mdb

##############################################################
# Read from packing data
# import data1 and create arrays
data1 = np.loadtxt('ellipse_positions2' + '.txt',skiprows=2)
print data1
ctr = np.zeros(shape=(len(data1),3))
pt1 = np.zeros(shape=(len(data1),3))
pt2 = np.zeros(shape=(len(data1),3))
for i in xrange(len(data1)):
	ctr[i]=data1[i][0:3]
	pt1[i]=data1[i][3:6]
	pt2[i]=data1[i][6:9]


data2 = np.loadtxt('packing_info2' + '.txt',skiprows=0)
print data2
N_fiber = int(data2[0])
N_pore = int(data2[2])
N=N_fiber+N_pore

########################################################################3

flag=1

if flag==1:
    mdb.models['Model-1'].Material(name='Matrix')
    mdb.models['Model-1'].materials['Matrix'].Conductivity(table=((cond_mat_var,), ))
    mdb.models['Model-1'].Material(name='Fiber')
    mdb.models['Model-1'].materials['Fiber'].Conductivity(table=((cond_fib_var,), ))

else:
    theta_0=293.0
    temp=[]
    cond_fib1=[]
    cond_mat1=[]
    cond_pore1=[]
    tab_mat,tab_fib,tab_pore=[]
    for i in range(300):
        temp[i]=293.0+i
        cond_mat1.append(((temp[i]/theta_0)**0.5)*cond_mat)
        cond_fib1.append(((temp[i]/theta_0)**0.5)*cond_fib)
        cond_pore1.append(((temp[i]/theta_0)**0.5)*cond_pore)

        tab_mat.append((cond_mat1[i],temp[i]))
        tab_fib.append((cond_fib1[i],temp[i]))
        tab_pore.append((cond_pore1[i],temp[i]))

    tab_mat=tuple(tab_mat)
    tab_fib=tuple(tab_fib)
    tab_pore=tuple(tab_pore)

    # for temperature dependency of conductivity

    mdb.models['Model-1'].materials['Matrix'].Conductivity(temperatureDependency=ON,table=(tab_mat))
    mdb.models['Model-1'].materials['Fiber'].Conductivity(temperatureDependency=ON,table=(tab_fib))

##############################################################################
# rectangle
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
H=1.0
W=1.0
s.rectangle(point1=(0.0, 0.0), point2=(W, H))
p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=TWO_D_PLANAR,
type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Part-1']
p.BaseShell(sketch=s)

###############################################################################

for i in xrange(N_fiber):
    p = mdb.models['Model-1'].parts['Part-1']
    f1, e1, d2 = p.faces, p.edges, p.datums
    t = p.MakeSketchTransform(sketchPlane=f1.findAt(coordinates=(0.0, 0.0, 0.0), normal=(0.0, 0.0, 1.0)), sketchUpEdge=e1.findAt(
    coordinates=(W, H/2.0, 0.0)), sketchPlaneSide=SIDE1, origin=(0.0, 0.0,
    0.0))
    s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=2.82, gridSpacing=0.07, transform=t)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=SUPERIMPOSE)
    p = mdb.models['Model-1'].parts['Part-1']
    p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
    s.EllipseByCenterPerimeter(center=(ctr[i][0], ctr[i][1]), axisPoint1=(pt1[i][0],pt1[i][1]), axisPoint2=(pt2[i][0],pt2[i][1]))
    p = mdb.models['Model-1'].parts['Part-1']
    f = p.faces
    pickedFaces = f.findAt(((0.0, 0.0, 0.0), ))
    e, d1 = p.edges, p.datums
    p.PartitionFaceBySketch(faces=pickedFaces, sketch=s)


######################################################################

# Create sections

mdb.models['Model-1'].HomogeneousSolidSection(name='Section-1',
     material='Matrix', thickness=None)
mdb.models['Model-1'].HomogeneousSolidSection(name='Section-2',
     material='Fiber', thickness=None)

######################################################################

# Create sets
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.findAt(((0.0, 0.0, 0.0), ))
p.Set(faces=faces, name='Matrix')


# Create a set of the fibers
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.findAt(((ctr[0][0],ctr[0][1],0.0), ) )
for i in xrange(1,N_fiber):
	faces += f.findAt(((ctr[i][0],ctr[i][1],0.0), ) )
p.Set(faces=faces, name='Fiber')




####################################################################
# Assign sections
p = mdb.models['Model-1'].parts['Part-1']
region = p.sets['Matrix']
p = mdb.models['Model-1'].parts['Part-1']
p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0,
    offsetType=MIDDLE_SURFACE, offsetField='',
    thicknessAssignment=FROM_SECTION)

p = mdb.models['Model-1'].parts['Part-1']
region = p.sets['Fiber']
p = mdb.models['Model-1'].parts['Part-1']
p.SectionAssignment(region=region, sectionName='Section-2', offset=0.0,
    offsetType=MIDDLE_SURFACE, offsetField='',
    thicknessAssignment=FROM_SECTION)

#################################################################################


# Create instance
a = mdb.models['Model-1'].rootAssembly
a.DatumCsysByDefault(CARTESIAN)
p = mdb.models['Model-1'].parts['Part-1']
a.Instance(name='Part-1-1', part=p, dependent=OFF)

#############################################################################


# Assign element types
elemType1=mesh.ElemType(elemCode=DC2D4,elemLibrary=STANDARD)
elemType2=mesh.ElemType(elemCode=DC2D3,elemLibrary=STANDARD)
p=mdb.models['Model-1'].parts['Part-1']
a = mdb.models['Model-1'].rootAssembly
f1 =a.instances['Part-1-1'].faces
#faces1=f1.findAt(((0.0,0.0,0.0),),((0.2,0.2,0.0),),((0.8,0.2,0.0),),((0.2,0.7,0.0),))
faces1 = f1.getByBoundingBox(0.0,0.0,0.0, 1.0, 1.0, 0.0) # (xmin, ymin, zmin, xmax, ymax, zmax) make this so these will adjust with the RVE size
pickedRegions=(faces1,)
a.setElementType(regions=pickedRegions,elemTypes=(elemType1,elemType2))

##################################################################################

# Generate mesh
a = mdb.models['Model-1'].rootAssembly
partInstances =(a.instances['Part-1-1'], )
a.seedPartInstance(regions=partInstances, size=0.01,deviationFactor=0.1,
    minSizeFactor=0.1)
a = mdb.models['Model-1'].rootAssembly
f1 =a.instances['Part-1-1'].faces
faces1 = f1.getByBoundingBox(0.0,0.0,0.0, 1.0, 1.0, 0.0)
a.setMeshControls(elemShape=TRI,regions=faces1)
a = mdb.models['Model-1'].rootAssembly
partInstances =(a.instances['Part-1-1'], )
a.generateMesh(regions=partInstances)

###################################################################################



# Create edge sets
a = mdb.models['Model-1'].rootAssembly
e1 = a.instances['Part-1-1'].edges
edges1 = e1.findAt(((0.0, H/2, 0.0), ))

a.Set(edges=edges1, name='left')

a = mdb.models['Model-1'].rootAssembly
e1 = a.instances['Part-1-1'].edges
edges1 = e1.findAt(((W, H/2, 0.0), ))
a.Set(edges=edges1, name='right')

# top set
a = mdb.models['Model-1'].rootAssembly
e1 = a.instances['Part-1-1'].edges

edges1=e1.findAt(((W/2,H,0.0),))
xv1 = a.instances['Part-1-1'].vertices

xVerts1=xv1.findAt(((0.0,H,0.0),),((W,H,0.0),))
a.Set(edges=edges1, xVertices=xVerts1, name='top')

# bottom set

a = mdb.models['Model-1'].rootAssembly
a = mdb.models['Model-1'].rootAssembly
e1 = a.instances['Part-1-1'].edges

edges1=e1.findAt(((W/2,0.0,0.0),))
xv1 = a.instances['Part-1-1'].vertices
xVerts1=xv1.findAt(((0.0,0.0,0.0),),((W,0.0,0.0),))
a.Set(edges=edges1, xVertices=xVerts1, name='bottom')

#Create individual nodes from the set
    # left side
n1 = []
for i in a.sets['left'].nodes:
    n1.append((i.coordinates[0],i.coordinates[1],i.coordinates[2],i.label))
n1.sort()

#Create a set from individual nodes in set above
nodeno1 = 1
for i in n1:
    setName = 'LeftNode-' + str(nodeno1)
    nodeset = a.SetFromNodeLabels(name = setName,nodeLabels = (('Part-1-1', (i[3],),),),)
    nodeno1 += 1

    # right side
n2 = []
for i in a.sets['right'].nodes:
    n2.append((i.coordinates[0],i.coordinates[1],i.coordinates[2],i.label))
n2.sort()

#Create a set from individual nodes in set above
nodeno2 = 1
for i in n2:
    setName = 'RightNode-' + str(nodeno2)
    nodeset = a.SetFromNodeLabels(name = setName,nodeLabels = (('Part-1-1', (i[3],),),),)
    nodeno2 += 1

    #top
n3 = []
for i in a.sets['top'].nodes:
    n3.append((i.coordinates[0],i.coordinates[1],i.coordinates[2],i.label))
n3.sort()

nodeno3 = 1
for i in n3:
    setName = 'TopNode-' + str(nodeno3)
    nodeset = a.SetFromNodeLabels(name = setName,nodeLabels = (('Part-1-1', (i[3],),),),)
    nodeno3 += 1

    #bottom
n4 = []
for i in a.sets['bottom'].nodes:
    n4.append((i.coordinates[0],i.coordinates[1],i.coordinates[2],i.label))
n4.sort()

nodeno4 = 1
for i in n4:
    setName = 'BottomNode-' + str(nodeno4)
    nodeset = a.SetFromNodeLabels(name = setName,nodeLabels = (('Part-1-1', (i[3],),),),)
    nodeno4 += 1
###########################################################################################
# Create dummy node
a = mdb.models['Model-1'].rootAssembly
a.ReferencePoint(point=(-0.5, 1.0, 0.0))
mdb.models['Model-1'].rootAssembly.features.changeKey(fromName='RP-1',
    toName='dummy')

#Apply PBC nodal constraint equations
r1 = a.referencePoints
keys = r1.keys()
val1 = keys[0]
dummy=(r1[val1], )
a.Set(referencePoints=dummy, name='dummy')

# Create dummy node
a = mdb.models['Model-1'].rootAssembly
a.ReferencePoint(point=(0, 1.5, 0.0))
mdb.models['Model-1'].rootAssembly.features.changeKey(fromName='RP-1',
    toName='dummy2')

#Apply PBC nodal constraint equations
r1 = a.referencePoints
keys = r1.keys()
val2 = keys[0]     # last reference point created is present in the first place in the array of 'keys'
dummy=(r1[val2], )
a.Set(referencePoints=dummy, name='dummy2')


#########################################################################################

#Apply constraint equation to each corresponding node for Periodic Boundary Condition (left to right faces, x faces)
for j in range(1,nodeno1):

    mdb.models['Model-1'].Equation(name='LeftRight-temp-Constraint-%d'%(j), terms=((1.0, 'LeftNode-%d'%(j), 11), (-1.0, 'RightNode-%d'%(j), 11),(-1.0, 'dummy', 11)))


#Apply constraint equation to each corresponding node for Periodic Boundary Condition (top to bottom faces, y faces)
for j in range(1,nodeno3):

    mdb.models['Model-1'].Equation(name='TopBottom-temp-Constraint-%d'%(j), terms=((1.0, 'TopNode-%d'%(j), 11), (-1.0, 'BottomNode-%d'%(j), 11),(-1.0, 'dummy2', 11)))



###################################################################################
# Create step
a = mdb.models['Model-1'].rootAssembly
mdb.models['Model-1'].HeatTransferStep(name='Step-1', previous='Initial',response=STEADY_STATE, amplitude=RAMP)

######################################################################################

# Apply BCs
a = mdb.models['Model-1'].rootAssembly
r1 = a.referencePoints
refPoints1=dummy=(r1[val1], )
region = regionToolset.Region(referencePoints=refPoints1)
mdb.models['Model-1'].TemperatureBC(name='BC-1', createStepName='Step-1',
    region=region, amplitude=UNSET, fixed=OFF,
    distributionType=UNIFORM, fieldName='', magnitude=500.0)

# Apply BC on the second dummy node as 0
a = mdb.models['Model-1'].rootAssembly
r1 = a.referencePoints
refPoints2=dummy=(r1[val2], )
region = regionToolset.Region(referencePoints=refPoints2)
mdb.models['Model-1'].TemperatureBC(name='BC-2', createStepName='Step-1',
    region=region, amplitude=UNSET, fixed=OFF,
    distributionType=UNIFORM, fieldName='', magnitude=0.0)




#######################################################################################

# Create a job
mdb.Job(name='Job%d' %tt, model='Model-1', description='', type=ANALYSIS,
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
    scratch='', multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)
#mdb.jobs['Job%d' %tt].setValues(multiprocessingMode=MPI,numCpus=3, numDomains=3)

mdb.models['Model-1'].FieldOutputRequest(name='F-Output-2',
    createStepName='Step-1', variables=('IVOL', ))

mdb.saveAs('/home/u23/tejakondury/SAPHYR3/mod_2%d' %tt)
###########################################################################################

#Submit job
mdb.jobs['Job%d' %tt].submit(consistencyChecking=OFF)
mdb.jobs['Job%d' %tt].waitForCompletion()

#############################################################################################
################
#Post processing
#################
#Import abaqus functions
from odbAccess import*

#odb job information
OdbName = 'Job%d.odb' %tt
myodb = openOdb(path=OdbName)

numFrames = len(myodb.steps['Step-1'].frames) #total number of frames

vol = myodb.steps['Step-1'].frames[-1].fieldOutputs['IVOL']
flux=myodb.steps['Step-1'].frames[-1].fieldOutputs['HFL']
temp=myodb.steps['Step-1'].frames[-1].fieldOutputs['NT11']

comp=0;
totVol = 0.0
totFlux=0.0
totTemp=0.0
gradt=500.0
for j in xrange(0,len(vol.values)):
    setVol = vol.values[j].data
    totVol += setVol
    totFlux +=flux.values[j].data[comp]*setVol

totFlux=totFlux/totVol
K_eff=(totFlux/gradt)


f=open('results_therm_cond_2step_5_5','a')
f.write(str(K_eff)+' '+str(tt)+"\n")
f.close()
