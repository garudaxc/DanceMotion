import sys
sys.path.append('I:/librosa/MusicLevelAutoGen/')

import google.protobuf
import animation_data_pb2
from struct import *
import numpy as np
import os
import matplotlib.pyplot as plt
import postprocess
import DownbeatTracking
import LevelInfo
import myprocesser


def Test():
    clip = animation_data_pb2.ClipData()

    #print(type(a))
    #print(type(a.path))

    #print(type(a.data))

    #a.path = '123'
    #a.data.append(1.0)
    #print(a)

    #buf = a.SerializeToString()
    #print(buf)

    print(dict(clip.joints))
    with open('I:/clipData.bin', 'rb') as f:
        a = f.read()
    clip.ParseFromString(a)
    print(clip.joints[0])


def UnpackData(fmt, buffer, offset):
    adv = calcsize(fmt)
    return unpack_from(fmt, buffer, offset), offset + adv

def GetMp3PathName(song):
    path = 'i:/work/DanceMotion/Assets/DanceMotion/resource/%s/%s.mp3' % (song, song)
    return path

def GetMotionFeature(song):
    pathname = 'i:/work/DanceMotion/Assets/DanceMotion/resource/%s/motion_feature.bin' % (song)
    with open(pathname, 'rb') as file:
        data = file.read()

    return data


def PrepareMusicFeature():
    song = 'loveydovey'        

    # music info
    pathname = GetMp3PathName(song)
    
    pathname = 'i:/DanceMotion/Mixdown.mp3'

    #duration, bpm, et = LevelInfo.LoadMusicInfo(pathname)
    #print(duration, bpm, et)
    #duration = duration / 1000.0
    #et = et / 1000.0
    #print('diring', duration)

    processer = myprocesser.CreateMFCCProcesserForMotion()
    feature = processer(pathname)
    print('feature', feature.shape)

    print(feature[0:50, [0, 1]])


def VisualMotionFeature():
    song = 'loveydovey'        

    # music info
    pathname = GetMp3PathName(song)    
    duration, bpm, et = LevelInfo.LoadMusicInfo(pathname)
    print(duration, bpm, et)
    duration = duration / 1000.0
    et = et / 1000.0

    beatInt = 60.0 / bpm
    beats = np.arange(et, duration, beatInt)
    numBeats = beats.shape[0]
    print('numBeat', numBeats)
    PrintTimePosToFile(beats, 'beat')

    data = GetMotionFeature(song)

    offset = 0
    (numSamples, floatsPerSample), offset = UnpackData('2i', data, offset)
    (startTime, deltaT, samplePerBeat), offset = UnpackData('2fi', data, offset)

    print('samples', numSamples, 'floatsPerSample', floatsPerSample, 'deltaT', deltaT, 'samplePerBeat', samplePerBeat)

    numBeats = int(numSamples / samplePerBeat)

    fmt = str(numSamples * floatsPerSample)+'f'
    featureData, offset = UnpackData('%df' % (numSamples * floatsPerSample), data, offset)
    #print('read data size ', len(data), 'unpack offset', offset)
    featureData = np.array(featureData)
    # reshape to [samples, dof-data]
    featureData = featureData.reshape(-1, floatsPerSample)

    featureData = featureData[:, [1, 3, 5, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]]
    floatsPerSample = featureData.shape[1]

    # calc forward difference
    featureDiff = (featureData[1:, :] - featureData[:-1, :]) / deltaT
    featureData = np.hstack((featureData[:-1, :], featureDiff))
    floatsPerSample = featureData.shape[1]

    print('feature shape0', featureData.shape)

    windowsSize = (int)(2 * (samplePerBeat/7))

    #featureData = featureData[:-(numSamples%samplePerBeat),:]
    featureData = featureData[:numBeats*samplePerBeat,:]
    print('feature shape1', featureData.shape)

    newFeature = []
    step = samplePerBeat / 7.0
    stepTime = deltaT * step
    for i in range(numBeats*7):
        start = int((i-1) * step)
        end = int((i+1) * step)
        if start < 0:
            start = 0
            
        data = featureData[start:end, :]
        mean = np.mean(data, 0)
        med = np.median(data, 0)
        variance = np.var(data, 0)

        data = np.hstack((mean, med, variance))

        #print(data.shape)
        #break

        newFeature.append(data)

    featureData = np.array(newFeature)
    
    print('feature shape2', featureData.shape)
  
    smin = np.amin(featureData, 0)
    print('smin', smin.shape)
    smax = np.amax(featureData, 0)
    featureData = featureData - smin
    r = smax - smin
    r[r < 0.00001] = 1.0
    featureData = featureData / r
    
 
    #beatTimes = np.arange(startTime, numBeats * 7 * stepTime + startTime, stepTime)
    #mean = featureData[:, 0:21]
    #diffmean = featureData[:, 21:42]
    #variance = featureData[:, 84:105]

    #samples = np.vstack((beatTimes, mean[:, 6])).T
    #PrintFeatureToFile(samples, 'mean_6')
        
    #samples = np.vstack((beatTimes, diffmean[:, 6])).T
    #PrintFeatureToFile(samples, 'diffmean_6')

    #samples = np.vstack((beatTimes, mean[:, 14])).T
    #PrintFeatureToFile(samples, 'mean_14')
    #samples = np.vstack((beatTimes, mean[:, 16])).T
    #PrintFeatureToFile(samples, 'mean_16')
    #samples = np.vstack((beatTimes, variance[:, 6])).T
    #PrintFeatureToFile(samples, 'variance_6')
    #samples = np.vstack((beatTimes, variance[:, 14])).T
    #PrintFeatureToFile(samples, 'variance_14')
    #samples = np.vstack((beatTimes, variance[:, 16])).T
    #PrintFeatureToFile(samples, 'variance_16')

    #print(times)


    #start = 10
    #count = 10
    #for i in range(10):
    #    plt.subplot(count, 1, i+1)
    #    plt.plot(featureData[:, start + i])
    #plt.show()

    #for i in range(floatsPerSample):
    #    PrintFeatureToFile(featureData[:, i], str(i))



def PrintFeatureToFile(features, postfix):
    path = 'i:/DanceMotion/'

    filename = '%sfeature_%s.csv' % (path, str(postfix))
    with open(filename, 'w') as file:
        for i in range(features.shape[0]):
            s = '%f, %f\n' % (features[i, 0], features[i, 1])
            file.write(s)

    print('write file', filename)


    
def PrintTimePosToFile(time, postfix):
    path = 'i:/DanceMotion/'

    filename = '%sfeature_%s.csv' % (path, str(postfix))
    with open(filename, 'w') as file:
        for i in range(time.shape[0]):
            s = '%f\n' % (time[i])
            file.write(s)

    print('write file', filename)

def CalcDanceMusicInfo():
    path = 'i:/work/DanceMotion/Assets/DanceMotion/resource/'
    files = os.listdir(path)

    mp3files = []
    for f in files:
        name = os.path.join(path, f)
        if not os.path.isdir(name):
            continue
        name = os.path.join(path, f, f) + '.mp3'
        if not os.path.exists(name):
            print('error, can not find file ', name)
        else:
            mp3files.append(name)
            print(name)
    
    for f in mp3files:
        DownbeatTracking.CalcMusicInfoFromFile(f)

def ProcessSamples():
    pass


if __name__ == '__main__':
    #Test()
    VisualMotionFeature()
    #PrepareMusicFeature()

    #CalcDanceMusicInfo()


