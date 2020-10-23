from vpython import *
import fbx
import skeleton
import MotionData

def ToVector(self):
    return vector(self[0], self[1], self[2])

setattr(fbx.FbxVector4, 'ToVector', ToVector)


def OnNext(b):

    print("The button said this: ", b.text)





def InitGUI():
    pass
    #button( bind=OnNext, text='Next' )

#    return scene2



def DrawJoints(skel, time = None):


    scene2 = canvas(title='charactor animaton',
     width=800, height=600,
     center=vector(5,0,0), background=color.black)
        
    scene2.caption = """To rotate "camera", drag with right button or Ctrl-drag.
    To zoom, drag with middle button or Alt/Option depressed, or use scroll wheel.
    On a two-button mouse, middle is left + right.
    To pan left/right and up/down, Shift-drag.
    Touch screen: pinch/extend to zoom, swipe or two-finger rotate."""

    size = len(skel)

    if time == None:
        for i, bone in enumerate(skel):
            pos = bone.mWorld_.GetT().ToVector()
            bone.s = sphere(pos=pos, radius=1)

        for i in range(1, size):
            boneInfo = skel[i]

            p0 = boneInfo.mWorld_.GetT().ToVector()
            p = boneInfo.parent_
            p1 = skel[p].mWorld_.GetT().ToVector()

            boneInfo.c = curve(p0, p1)
    
    else:
        for i, bone in enumerate(skel):
            trans = bone.GetTransformAt(time)
            pos = trans.GetT().ToVector()
            bone.s.pos = pos

        for i in range(1, size):
            boneInfo = skel[i]

            p0 = boneInfo.GetTransformAt(time).GetT().ToVector()
            p1 = skel[boneInfo.parent_].GetTransformAt(time).GetT().ToVector()

            boneInfo.c.modify(0, pos = p0)
            boneInfo.c.modify(1, pos = p1)
            
    #print(x, y)
    #mlab.points3d(x, y, z, colormap="copper", scale_factor=2)


class PlayInfo:
    pass


CurrentPlayInfo = None

def Play(frameRate, step, CurrentAnim, AnimList):

    global CurrentPlayInfo    

    

    if CurrentPlayInfo == None:
        CurrentPlayInfo = PlayInfo()
        animInfo = AnimList[CurrentAnim]
        filePath = animInfo.fullName_

        skeleton.InitFbx(filePath)
        skel = skeleton.LoadSkeleton()
        CurrentPlayInfo.skel_ = skel
        
        DrawJoints(skel)
        anim = skeleton.LoadAnimation()
        CurrentPlayInfo.anim_ = anim

        print("loaded")

    
    # if CurrentPlayInfo.anim_ != None:


    #     t = CurrentPlayInfo.anim_.start_

    #     print(t)
    #     while True:
    #         rate(frameRate)
    #         DrawJoints(skel, t)
    #         t = t + step
    #         if t > CurrentPlayInfo.anim_.stop_:
    #             break
    


def TestDrawJoints(filePath):  
    skeleton.InitFbx(filePath)
    skel = skeleton.LoadSkeleton()    
    DrawJoints(skel)



def main():
    path = '''resource/playingwithfire/playingwithfire.FBX'''
    path = '''resource/test.FBX'''
    path = 'G:/code/mobile_dancer/x5_mobile/mobile_dancer_resource/Resources/美术资源/动作/fbx/art/role/dance_actions'

    
    scene = InitGUI()
    
    global frameRate, step

    frameRate = 30
    step = float(1.0 / frameRate)

    AnimList = MotionData.ListMotionSegment(path, MotionData.FilterTwoBars)
    CurrentAnim = 0

    #Play(frameRate, step, CurrentAnim, AnimList) 

    path = 'G:/code/mobile_dancer/x5_mobile/mobile_dancer_resource/Resources/美术资源/动作/fbx/art/role/dance_actions/BackToTheFuture/SD_128BPM_BackToTheFuture_04_1.FBX'
    #path = '''resource/MrChu/MrChu.fbx'''
    TestDrawJoints(path)

    # print("anim", anim.name_, anim.start_, anim.stop_)

    # skeleton.DestroyFbx()




if __name__ == '__main__':
    main()
