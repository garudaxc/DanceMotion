from mayavi import mlab

import fbx
from FbxCommon import *



class BoneInfo:
    parent_ = -1

    def __init__(self, node):
        self.node_ = node
        self.name_ = node.GetName()
        self.mLocal_ = node.EvaluateLocalTransform()
        self.mWorld_ = node.EvaluateGlobalTransform()

        # r = node.EvaluateLocalTranslation()
        # print(self.name_, r[0], r[1], r[2])
    def GetTransformAt(self, t):
        time = fbx.FbxTime()
        time.SetSecondDouble(t)

        trans = self.node_.EvaluateGlobalTransform(time)
        return trans



def DisplayTransformPropagation(pNode):
    print("    Transformation Propagation")
    
    # Rotation Space
    lRotationOrder = pNode.GetRotationOrder(fbx.FbxNode.eSourcePivot)

    print("        Rotation Space:",)

    if lRotationOrder == fbx.eEulerXYZ:
        print("Euler XYZ")
    elif lRotationOrder == fbx.eEulerXZY:
        print("Euler XZY")
    elif lRotationOrder == fbx.eEulerYZX:
        print("Euler YZX")
    elif lRotationOrder == fbx.eEulerYXZ:
        print("Euler YXZ")
    elif lRotationOrder == fbx.eEulerZXY:
        print("Euler ZXY")
    elif lRotationOrder == fbx.eEulerZYX:
        print("Euler ZYX")
    elif lRotationOrder == fbx.eSphericXYZ:
        print("Spheric XYZ")
    
    # Use the Rotation space only for the limits
    # (keep using eEULER_XYZ for the rest)
    if pNode.GetUseRotationSpaceForLimitOnly(fbx.FbxNode.eSourcePivot):
        print("        Use the Rotation Space for Limit specification only: Yes")
    else:
        print("        Use the Rotation Space for Limit specification only: No")

    # Inherit Type
    lInheritType = pNode.GetTransformationInheritType()

    print("        Transformation Inheritance:",)

    if lInheritType == fbx.FbxTransform.eInheritRrSs:
        print("RrSs")
    elif lInheritType == fbx.FbxTransform.eInheritRSrs:
        print("RSrs")
    elif lInheritType == fbx.FbxTransform.eInheritRrs:
        print("Rrs")



def DisplaySkeleton(pNode):
    lSkeleton = pNode.GetNodeAttribute()

    print("Skeleton Name: ", pNode.GetName())

    lSkeletonTypes = [ "Root", "Limb", "Limb Node", "Effector" ]

    print("    Type: ", lSkeletonTypes[lSkeleton.GetSkeletonType()])

    if lSkeleton.GetSkeletonType() == fbx.FbxSkeleton.eLimb:
        print("    Limb Length: ", lSkeleton.LimbLength.Get())
    elif lSkeleton.GetSkeletonType() == fbx.FbxSkeleton.eLimbNode:
        print("    Limb Node Size: ", lSkeleton.Size.Get())
    elif lSkeleton.GetSkeletonType() == fbx.FbxSkeleton.eRoot:
        print("    Limb Root Size: ", lSkeleton.Size.Get())


def DisplayHierarchy(pScene):
    lRootNode = pScene.GetRootNode()

    for i in range(lRootNode.GetChildCount()):
        DisplayNodeHierarchy(lRootNode.GetChild(i), 0)

def DisplayNodeHierarchy(pNode, pDepth):
    lString = ""
    for i in range(pDepth):
        lString += "     "

    lString += pNode.GetName()

    print(lString)

    for i in range(pNode.GetChildCount()):
        DisplayNodeHierarchy(pNode.GetChild(i), pDepth + 1)



def FindBip(rootNode, prefix):

    for i in range(rootNode.GetChildCount()):
        child = rootNode.GetChild(i)

        #print(child.GetName(), child.GetNodeAttribute())

        if child.GetName().startswith(prefix):
        #      and \
        # child.GetNodeAttribute() != None and \
        # child.GetNodeAttribute().GetAttributeType() == fbx.FbxNodeAttribute.eSkeleton:
            return child

        #     continue
        
        # if child.GetNodeAttribute() == None:
        #     print("NULL Node Attribute\n")
        #     continue
        
        # lAttributeType = (child.GetNodeAttribute().GetAttributeType())

        # if lAttributeType == fbx.FbxNodeAttribute.eSkeleton:

        #     return child
        #     DisplaySkeleton(child)
        #     DisplayTransformPropagation(child)

        found = FindBip(child, prefix)
        if found != None:
            return found


### 收集骨架的骨骼列表
def ListSkeletonBones(boneList, rootNode, parentIndex):
    bone = BoneInfo(rootNode)
    bone.parent_ = parentIndex
    boneList.append(bone)
    index = len(boneList) - 1

    #r = rootNode.EvaluateLocalTranslation()

    for i in range(rootNode.GetChildCount()):
        node = rootNode.GetChild(i)
        ListSkeletonBones(boneList, node, index)


## get Transfrom
def PrintTransform(node):
    t = node.LclTranslation.Get()
    r = node.LclRotation.Get()

    m = node.EvaluateLocalTransform()
    t = m.GetT()
    r = m.GetQ()

    print(node.GetName(), m, t, r)


# def EvaluateSkeletonTransform(skel):
#     for bone in skel:
#         if bone.parent_ == -1:
#             bone.position_ = bone.mLocal_.GetT()
#             bone.rotation_ = bone.mLocal_.GetQ()
#         else:
#             parent = skel[bone.parent_]
#             bone.rotation_ = 




def DisplayAnimation(pScene):
    for i in range(pScene.GetSrcObjectCount(FbxCriteria.ObjectType(FbxAnimStack.ClassId))):
        lAnimStack = pScene.GetSrcObject(FbxCriteria.ObjectType(FbxAnimStack.ClassId), i)

        print(type(lAnimStack))
        timeSpan = lAnimStack.GetLocalTimeSpan()
        start, stop = timeSpan.GetStart(), timeSpan.GetStop()
        print('time', start.GetSecondDouble(), stop.GetSecondDouble())

        lOutputString = "Animation Stack Name: "
        lOutputString += lAnimStack.GetName()
        lOutputString += "\n"
        print(lOutputString)

        DisplayAnimationStack(lAnimStack, pScene.GetRootNode(), True)
        DisplayAnimationStack(lAnimStack, pScene.GetRootNode(), False)

def DisplayAnimationStack(pAnimStack, pNode, isSwitcher):
    nbAnimLayers = pAnimStack.GetSrcObjectCount(FbxCriteria.ObjectType(FbxAnimLayer.ClassId))

    lOutputString = "Animation stack contains "
    lOutputString += str(nbAnimLayers)
    lOutputString += " Animation Layer(s)"
    print(lOutputString)

    for l in range(nbAnimLayers):
        lAnimLayer = pAnimStack.GetSrcObject(FbxCriteria.ObjectType(FbxAnimLayer.ClassId), l)

        lOutputString = "AnimLayer "
        lOutputString += str(l)
        print(lOutputString)

        # DisplayAnimationLayer(lAnimLayer, pNode, isSwitcher)


def InitFbx(path):    
    global fbxManager, fbxScene
    
    fbxManager = fbx.FbxManager.Create()
    fbxScene = fbx.FbxScene.Create( fbxManager, '' )
    importer = fbx.FbxImporter.Create(fbxManager, '')

    status = importer.Initialize(path, -1, fbxManager.GetIOSettings())

    if not status:
        err = importer.GetStatus().GetErrorString()
        print(err)

    status = importer.Import(fbxScene)

    if not status:
        err = importer.GetStatus().GetErrorString()
        print(err)
    #print(status)

    importer.Destroy()


def DestroyFbx():
    global fbxManager, fbxScene
    # Destroy the fbx manager explicitly, which recursively destroys
    # all the objects that have been created with it.

    try:
        fbxManager.Destroy()
        #
        # Once the memory has been freed, it is good practice to delete
        # the currently invalid references contained in our variables.
        del fbxManager, fbxScene
    except Exception as identifier:
        print(identifier)
        



def LoadSkeleton():

    rootNode = fbxScene.GetRootNode()
    rootBone = FindBip(rootNode, 'Bip') 

    print('root bone ', rootBone)

    if rootBone != None:
        boneList = []    
        ListSkeletonBones(boneList, rootBone, -1)

        # for b in boneList:
        #     PrintTransform(b.node_)
    
    # for i, b in enumerate(boneList):
    #     print(i, b.name_, b.parent_)
        
    # DisplayAnimation(fbxScene)

        return boneList



class AnimationInfo:
    def __init__(self, fbxScene, index):
        
        #for i in range(pScene.GetSrcObjectCount(FbxCriteria.ObjectType(FbxAnimStack.ClassId))):
        lAnimStack = fbxScene.GetSrcObject(FbxCriteria.ObjectType(FbxAnimStack.ClassId), index)

        self.name_ = lAnimStack.GetName()

        timeSpan = lAnimStack.GetLocalTimeSpan()
        self.start_ = timeSpan.GetStart().GetSecondDouble()
        self.stop_ = timeSpan.GetStop().GetSecondDouble()


        # start, stop = timeSpan.GetStart(), timeSpan.GetStop()
        # print('time', start.GetSecondDouble(), stop.GetSecondDouble())

        # lOutputString = "Animation Stack Name: "
        # lOutputString += lAnimStack.GetName()
        # lOutputString += "\n"
        # print(lOutputString)




def LoadAnimation():
    global fbxManager, fbxScene

    numAnimStack = fbxScene.GetSrcObjectCount(FbxCriteria.ObjectType(FbxAnimStack.ClassId))
    if numAnimStack == 0:
        return

    animInfo = AnimationInfo(fbxScene, 0)
    return animInfo



if __name__ == '__main__':

    path = '''resource/playingwithfire/playingwithfire.FBX'''
    path = '''resource/MrChu/MrChu.FBX'''
    path = '''resource/test.FBX'''  
    path = 'G:/code/mobile_dancer/x5_mobile/mobile_dancer_resource/Resources/美术资源/动作/fbx/art/role/dance_actions/BackToTheFuture/SD_128BPM_BackToTheFuture_04_1.FBX'
    

    InitFbx(path)
    skel = LoadSkeleton()

    print(len(skel))

    anim = LoadAnimation()
    print(anim.start_, anim.stop_)

    t = skel[0].GetTransformAt(1.5)
    print(t)

    DestroyFbx()