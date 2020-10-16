from vpython import *
import fbx
import skeleton


def ToVector(self):
    return vector(self[0], self[1], self[2])

setattr(fbx.FbxVector4, 'ToVector', ToVector)


scene.caption = """To rotate "camera", drag with right button or Ctrl-drag.
To zoom, drag with middle button or Alt/Option depressed, or use scroll wheel.
  On a two-button mouse, middle is left + right.
To pan left/right and up/down, Shift-drag.
Touch screen: pinch/extend to zoom, swipe or two-finger rotate."""



def DrawJoints(skel):
    size = len(skel)
    for i, bone in enumerate(skel):
        pos = bone.mWorld_.GetT().ToVector()
        s = sphere(pos=pos, pos[2]), radius=1)

    for i in range(1, size):
        p0 = skel[i].mWorld_.GetT().ToVector()
        p = skel[i].parent_
        p1 = skel[p].mWorld_.GetT().ToVector()

        c = curve(p0, p1)
        
    #print(x, y)
    #mlab.points3d(x, y, z, colormap="copper", scale_factor=2)






if __name__ == '__main__':

    path = '''resource/playingwithfire/playingwithfire.FBX'''
    path = '''resource/test.FBX'''
    path = '''resource/MrChu/MrChu.FBX'''

    skel = skeleton.load_skeleton(path)

    DrawJoints(skel)