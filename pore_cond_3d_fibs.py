#import os
#print('this is the env variable:', os.environ['tt'])
#tts=os.environ['tt']
#tt=float(tts)
#mat_vol=float(os.environ['mat_vol'])
#pore_vol=float(os.environ['pr_vol'])

# Abaqus modules
from abaqus import *
from abaqusConstants import *
from caeModules import *

# Python modules
import os
import numpy as np
import pickle as pk

# get initial data
from __main__ import *
# read conductivity values from previous step
f=open('norm%d'%tt,'r')
cond_mat_var=f.read()
cond_mat_var=float(cond_mat_var)
f.close()

f=open('fib-cond%d'%tt,'r')
cond_fib_var=f.read()
cond_fib_var=float(cond_fib_var)
f.close()


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

# Create material properties
mdb.models['Model-1'].Material(name='Matrix')
mdb.models['Model-1'].materials['Matrix'].Conductivity(table=((cond_mat_var,), ))
#mdb.models['Model-1'].Material(name='Pore')
#mdb.models['Model-1'].materials['Pore'].Conductivity(table=((cond_pore_var,), ))
mdb.models['Model-1'].Material(name='Fiber')
mdb.models['Model-1'].materials['Fiber'].Conductivity(table=((cond_fib_var,), ))

# Make a cube
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
# RVE Geometry
H=1.0
W=1.0
D=1.0
s.rectangle(point1=(0.0, 0.0), point2=(W, H))
p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=THREE_D,
type=DEFORMABLE_BODY)
mdb.models['Model-1'].parts['Part-1'].BaseSolidExtrude(depth=D, sketch= mdb.models['Model-1'].sketches['__profile__'])

###############################################################################
# make fibers
k=0
for i in xrange(N_fiber):
    p = mdb.models['Model-1'].parts['Part-1']
    f1, e1, d2 = p.faces, p.edges, p.datums
    t = p.MakeSketchTransform(sketchPlane=f1.findAt(coordinates=(W/2.0, H/2.0,D)), sketchUpEdge=e1.findAt(
    coordinates=(W, H/2.0, D)), sketchPlaneSide=SIDE1,origin=(0.0,0.0,D))
    s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=2.82, gridSpacing=0.07, transform=t)
    s.setPrimaryObject(option=SUPERIMPOSE)
    mdb.models['Model-1'].parts['Part-1'].projectReferencesOntoSketch(filter= COPLANAR_EDGES, sketch=s)
    s.EllipseByCenterPerimeter(center=(ctr[i][0], ctr[i][1]), axisPoint1=(pt1[i][0],pt1[i][1]), axisPoint2=(pt2[i][0],pt2[i][1]))
    f = p.faces
    pickedFaces = f.findAt(((0.0, 0.0, D), ))
    p.PartitionFaceBySketch(faces=pickedFaces, sketch=s)
    p.PartitionCellBySweepEdge(cells= p.cells[k],edges=(p.edges.findAt(coordinates=(pt1[i][0],pt1[i][1],D)),), sweepPath= p.edges.findAt(coordinates=(0.0,0.0,D/2.0)) )
    k=k+1

mdb.saveAs('/home/u23/tejakondury/RUBY1/mod%d' %tt)

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
faces = f.findAt(((ctr[N_fiber+1][0],ctr[N_fiber+1][1],0.0), ) )
for i in xrange(N_fiber):
    faces += f.findAt(((ctr[i][0],ctr[i][1],0.0), ) )
p.Set(faces=faces, name='Fiber')

mdb.saveAs('/home/u23/tejakondury/RUBY1/mod%d' %tt)


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
p.SectionAssignment(region=region, sectionName='Section-3', offset=0.0,
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
a.seedPartInstance(regions=partInstances, size=0.01,
minSizeFactor=0.1)
a = mdb.models['Model-1'].rootAssembly
partInstances =(a.instances['Part-1-1'], )
a.generateMesh(regions=partInstances)

###################################################################################

mdb.saveAs('/home/u23/tejakondury/RUBY1/mod%d' %tt)

# Use after generating mesh

# Create sets for faces

a=mdb.models['Model-1'].rootAssembly
f1=a.instances['Part-1-1'].faces
faces1=f1.findAt(((0.0,H/2.0,D/2.0),))
a.Set(faces=faces1,name='left-face')

faces2=f1.findAt(((W,H/2.0,D/2.0),))
a.Set(faces=faces2,name='right-face')

faces3=f1.findAt(((W/2.0,H,D/2.0),))
a.Set(faces=faces3, name='top-face')

faces4=f1.findAt(((W/2.0,0.0,D/2.0),))
a.Set(faces=faces4,name='bottom-face')

faces5=f1.findAt(((W/2.0,H/2.0,0.0),))
a.Set(faces=faces5,name='back-face')

faces6=f1.findAt(((W/2.0,H/2.0,D),))
a.Set(faces=faces6,name='front-face')

################################################################################
#Create individual nodes from the set
# left face
n1 = []
for i in a.sets['left-face'].nodes:
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
for i in a.sets['right-face'].nodes:
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
for i in a.sets['top-face'].nodes:
    n3.append((i.coordinates[0],i.coordinates[1],i.coordinates[2],i.label))
n3.sort()

nodeno3 = 1
for i in n3:
    setName = 'TopNode-' + str(nodeno3)
    nodeset = a.SetFromNodeLabels(name = setName,nodeLabels = (('Part-1-1', (i[3],),),),)
    nodeno3 += 1

#bottom
n4 = []
for i in a.sets['bottom-face'].nodes:
    n4.append((i.coordinates[0],i.coordinates[1],i.coordinates[2],i.label))
n4.sort()

nodeno4 = 1
for i in n4:
    setName = 'BottomNode-' + str(nodeno4)
    nodeset = a.SetFromNodeLabels(name = setName,nodeLabels = (('Part-1-1', (i[3],),),),)
    nodeno4 += 1

#front

n5 = []
for i in a.sets['front-face'].nodes:
    n5.append((i.coordinates[0],i.coordinates[1],i.coordinates[2],i.label))
n5.sort()

nodeno5 = 1
for i in n5:
    setName = 'FrontNode-' + str(nodeno5)
    nodeset = a.SetFromNodeLabels(name = setName,nodeLabels = (('Part-1-1', (i[3],),),),)
    nodeno5 += 1

#back face
n6 = []
for i in a.sets['back-face'].nodes:
    n6.append((i.coordinates[0],i.coordinates[1],i.coordinates[2],i.label))
n6.sort()

nodeno6 = 1
for i in n6:
    setName = 'BackNode-' + str(nodeno6)
    nodeset = a.SetFromNodeLabels(name = setName,nodeLabels = (('Part-1-1', (i[3],),),),)
    nodeno6 += 1
##########################################################################
# Create dummy nodes (3)

# Dummy node for left-right face
a = mdb.models['Model-1'].rootAssembly
a.ReferencePoint(point=(-W/2.0,H/2.0,D/2.0))
mdb.models['Model-1'].rootAssembly.features.changeKey(fromName='RP-1',
toName='dummy L-R')

# Create a set of dummy node
r1 = a.referencePoints
keys = r1.keys()
val1 = keys[0]
dummy=(r1[val1], )
a.Set(referencePoints=dummy, name='dummy L-R')

# Dummy node for Top-Bottom face
a = mdb.models['Model-1'].rootAssembly
a.ReferencePoint(point=(W/2.0,-H/2.0, D/2.0))
mdb.models['Model-1'].rootAssembly.features.changeKey(fromName='RP-1',
toName='dummy T-B')
# Create a set
r1 = a.referencePoints
keys = r1.keys()
val2 = keys[1]
dummy=(r1[val2], )
a.Set(referencePoints=dummy, name='dummy T-B')


# Dummy node for front-back face
a = mdb.models['Model-1'].rootAssembly
a.ReferencePoint(point=(W/2.0,H/2.0,-D/2.0))
mdb.models['Model-1'].rootAssembly.features.changeKey(fromName='RP-1',
toName='dummy F-B')

# Create a set of dummy node
r1 = a.referencePoints
keys = r1.keys()
val3 = keys[2]
dummy=(r1[val3], )
a.Set(referencePoints=dummy, name='dummy F-B')

mdb.saveAs('/home/u23/tejakondury/RUBY1/mod%d' %tt)
###############################################################################
# Applying constraint equations
#Apply constraint equation to each corresponding node for Periodic Boundary Condition (left to right faces, x faces)
for j in range(1,nodeno1):

    mdb.models['Model-1'].Equation(name='LeftRight-temp-Constraint-%d'%(j), terms=((1.0, 'LeftNode-%d'%(j), 11), (-1.0, 'RightNode-%d'%(j), 11),(-1.0, 'dummy L-R', 11)))

#Apply constraint equation to each corresponding node for Periodic Boundary Condition (top to bottom faces, y faces)
for j in range(1,nodeno3):

    mdb.models['Model-1'].Equation(name='TopBottom-temp-Constraint-%d'%(j), terms=((1.0, 'TopNode-%d'%(j), 11), (-1.0, 'BottomNode-%d'%(j), 11),(-1.0, 'dummy T-B', 11)))

#Apply constraint equation to each corresponding node for Periodic Boundary Condition (front to back faces, z faces)
for j in range(1,nodeno5):

    mdb.models['Model-1'].Equation(name='FrontBack-temp-Constraint-%d'%(j), terms=((1.0, 'FrontNode-%d'%(j), 11), (-1.0, 'BackNode-%d'%(j), 11),(-1.0, 'dummy F-B', 11)))

###################################################################################
# Create step
a = mdb.models['Model-1'].rootAssembly
mdb.models['Model-1'].HeatTransferStep(name='Step-1', previous='Initial',response=STEADY_STATE, amplitude=RAMP)

#####################################################################################
# Apply boundary conditions on dummy nodes
a = mdb.models['Model-1'].rootAssembly
r1 = a.referencePoints
refPoints1=dummy=(r1[val3], )                                        # applying on the Front-Back face
region = regionToolset.Region(referencePoints=refPoints1)
mdb.models['Model-1'].TemperatureBC(name='BC-1', createStepName='Step-1',
region=region, amplitude=UNSET, fixed=OFF,
distributionType=UNIFORM, fieldName='', magnitude=100.0)


a = mdb.models['Model-1'].rootAssembly
r1 = a.referencePoints
refPoints1=dummy=(r1[val1], )                                        # applying on the Left-Right face
region = regionToolset.Region(referencePoints=refPoints1)
mdb.models['Model-1'].TemperatureBC(name='BC-1', createStepName='Step-1',
region=region, amplitude=UNSET, fixed=OFF,
distributionType=UNIFORM, fieldName='', magnitude=0.0)

a = mdb.models['Model-1'].rootAssembly
r1 = a.referencePoints
refPoints1=dummy=(r1[val2], )                                        # applying on the Top-Bottom face
region = regionToolset.Region(referencePoints=refPoints1)
mdb.models['Model-1'].TemperatureBC(name='BC-1', createStepName='Step-1',
region=region, amplitude=UNSET, fixed=OFF,
distributionType=UNIFORM, fieldName='', magnitude=0.0)

mdb.saveAs('/home/u23/tejakondury/RUBY1/mod%d' %tt)

#######################################################################################

# Create a job
mdb.Job(name='Job%d'%tt, model='Model-1', description='', type=ANALYSIS,
atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
scratch='', multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)
#mdb.jobs['Job-1'].setValues(multiprocessingMode=MPI,numCpus=3, numDomains=3)
mdb.models['Model-1'].FieldOutputRequest(name='F-Output-2',
createStepName='Step-1', variables=('IVOL', ))

mdb.saveAs('/home/u23/tejakondury/RUBY1/mod%d' %tt)
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
gradt=100.0
for j in xrange(0,len(vol.values)):
    setVol = vol.values[j].data
    totVol += setVol
    totFlux +=flux.values[j].data[comp]*setVol

totFlux=totFlux/totVol
K_eff=(totFlux/gradt)


f=open('results_homogenized_composite_avg','a')
f.write(str(tt)+' '+str(K_eff)+' '+str(pore_vol)+' '+str(1-pore_vol) + "\n")
f.close()
