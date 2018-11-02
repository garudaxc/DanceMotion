import tensorflow as tf
from tensorflow.contrib import rnn
import os.path



root = 'i:/work/DanceMotion/Assets/DanceMotion/resource/'




def PrepareTrainData():
    files = os.listdir(root)

    mp3files = []
    for f in files:
        name = os.path.join(root, f)
        if not os.path.isdir(name):
            continue
        name = os.path.join(root, f, f) + '.mp3'
        if not os.path.exists(name):
            print('error, can not find file ', name)
            continue



        mp3files.append(name)
        print(name)






def Test():
    PrepareTrainData()


if __name__ == '__main__':
    Test()