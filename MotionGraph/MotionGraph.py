import numpy as np
from mayavi import mlab
import skeleton


def ConvertFbxVector3(v):
    return float(v[0]), float(v[1]), float(v[2])


def DrawJoints(skel):
    size = len(skel)
    x = np.zeros(size)
    y = np.zeros(size)
    z = np.zeros(size)
    for i, bone in enumerate(skel):
        pos = bone.mWorld_.GetT()
        x[i], y[i], z[i] = pos[0], pos[1], pos[2]
        
    #print(x, y)
    mlab.points3d(x, y, z, colormap="copper", scale_factor=2)


def DrawBones(skel):
    size = len(skel)

    for i in range(1, size):
        x = np.zeros(2)
        y = np.zeros(2)
        z = np.zeros(2)
        start = skel[i].mWorld_.GetT()
        #print(skel[i].name_, skel[i].parent_)
        end = skel[skel[i].parent_].mWorld_.GetT()

        x[0], y[0], z[0] = start[0], start[1], start[2]
        x[1], y[1], z[1] = end[0], end[1], end[2]

        if (start - end).SquareLength() > 1 :
            mlab.plot3d(x, y, z, colormap="copper", line_width=2)






def dummy():

    mlab.figure(fgcolor=(0, 0, 0), bgcolor=(1, 1, 1))

    t = np.linspace(0, 4 * np.pi, 20)
    x = np.sin(2 * t)
    y = np.cos(t)
    z = np.cos(2 * t)
    s = 2 + np.sin(t)
    mlab.points3d(x, y, z, s, colormap="copper", scale_factor=.25)

    # u, v = mgrid[- 0.035:pi:0.01, - 0.035:pi:0.01]

    # X = 2 / 3. * (cos(u) * cos(2 * v) + sqrt(2) * sin(u) * cos(v)) * cos(u) / (sqrt(2) -  sin(2 * u) * sin(3 * v))
    # Y = 2 / 3. * (cos(u) * sin(2 * v) - sqrt(2) * sin(u) * sin(v)) * cos(u) / (sqrt(2) - sin(2 * u) * sin(3 * v))
    # Z = -sqrt(2) * cos(u) * cos(u) / (sqrt(2) - sin(2 * u) * sin(3 * v))
    # S = sin(u)

    # mlab.mesh(X, Y, Z, scalars=S, colormap='YlGnBu', )

    # Nice view from the front
    mlab.view(.0, - 5.0, 'auto')
    mlab.show()





def ConvertSkeletonJoint(skel):

    mlab.figure(fgcolor=(0, 0, 0), bgcolor=(1, 1, 1), size=(800, 600))

    DrawBones(skel)
    DrawJoints(skel)

    mlab.view(.0, - 5.0, 100)
    mlab.show()





if __name__ == '__main__':

    path = '''resource/playingwithfire/playingwithfire.FBX'''
    path = '''resource/test.FBX'''
    path = '''resource/MrChu/MrChu.FBX'''

    skel = skeleton.load_skeleton(path)

    ConvertSkeletonJoint(skel)


