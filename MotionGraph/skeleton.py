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



def FindBip(scene, prefix):
    lRootNode = scene.GetRootNode()

    for i in range(lRootNode.GetChildCount()):
        child = lRootNode.GetChild(i)
        print(child.GetName())

        if not child.GetName().startswith(prefix):
            continue
    
        print(child.GetName())
        
        if child.GetNodeAttribute() == None:
            print("NULL Node Attribute\n")
            continue
        
        lAttributeType = (child.GetNodeAttribute().GetAttributeType())

        if lAttributeType == fbx.FbxNodeAttribute.eSkeleton:

            return child
            DisplaySkeleton(child)
            DisplayTransformPropagation(child)


### 收集骨架的骨骼列表
def ListSkeletonBones(boneList, rootNode, parentIndex):
    bone = BoneInfo(rootNode)
    bone.parent_ = parentIndex
    boneList.append(bone)
    index = len(boneList) - 1

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




def load_skeleton(path):
    
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

    rootBone = FindBip(fbxScene, 'Bip')
    print(rootBone)

    boneList = []    
    if rootBone != None:
        ListSkeletonBones(boneList, rootBone, -1)

        # for b in boneList:
        #     PrintTransform(b.node_)
    
    # Destroy the fbx manager explicitly, which recursively destroys
    # all the objects that have been created with it.
    fbxManager.Destroy()
    #
    # Once the memory has been freed, it is good practice to delete
    # the currently invalid references contained in our variables.
    del fbxManager, fbxScene

    return boneList



if __name__ == '__main__':

    path = '''resource/playingwithfire/playingwithfire.FBX'''
    path = '''resource/MrChu/MrChu.FBX'''
    path = '''resource/test.FBX'''

    load_skeleton(path)