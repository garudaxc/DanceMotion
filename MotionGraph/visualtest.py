from vpython import *
import skeleton

ball = sphere(pos=vector(-5,0,0), radius=0.5,color=color.cyan, make_trail=True, retain=200)
wallR = box(pos=vector(6,0,0), size=vector(0.2,12,12), color=color.green)
ball.velocity = vector(25,0,0)
deltat = 0.05
t = 0
ball.pos = ball.pos + ball.velocity*deltat
while True:
    rate(200)
    ball.velocity.x = -ball.velocity.x
    ball.pos = ball.pos + ball.velocity*deltat
    t = t + deltat 

# def DrawJoints(skel):
#     size = len(skel)
#     x = np.zeros(size)
#     y = np.zeros(size)
#     z = np.zeros(size)
#     for i, bone in enumerate(skel):
#         pos = bone.mWorld_.GetT()
#         x[i], y[i], z[i] = pos[0], pos[1], pos[2]
        
#     #print(x, y)
#     mlab.points3d(x, y, z, colormap="copper", scale_factor=2)



if __name__ == '__main__':

    path = '''resource/playingwithfire/playingwithfire.FBX'''
    path = '''resource/test.FBX'''
    path = '''resource/MrChu/MrChu.FBX'''

    # skel = skeleton.load_skeleton(path)