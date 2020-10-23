import fbx
import os




class MotionSegmentInfo:
    pass


def FilterTwoBars(info):
    if(info.length_ < 2):
        return False

    return True



def ListMotionSegment(path, filter = None):

    segList = []
    
    for root, dirs, files in os.walk(path):
        for fileName in files:
            fullname = os.path.join(root, fileName)
            fileName = os.path.splitext(fileName)

            if fileName[-1].lower() != '.fbx':
                continue

            token = fileName[0].split('_')
            if  token[0].lower() != 'sd':
                continue

            if len(token) != 5:
                continue

            song = os.path.split(root)[-1]

            if token[2].lower() != song.lower():
                #print(token[2], song)
                continue
                        
            bpm = int(token[1][0:-3])
            segment = int(token[3])
            segLenth = int(token[4])

            info = MotionSegmentInfo()
            info.fullName_ = fullname
            info.bpm_ = bpm
            info.songName = song
            info.segment_ = segment
            info.length_ = segLenth

            if filter != None and not filter(info):
                continue

            segList.append(info)
            # print(song, bpm, segment, segLenth)
    return segList




def main():
    path = 'G:/code/mobile_dancer/x5_mobile/mobile_dancer_resource/Resources/美术资源/动作/fbx/art/role/dance_actions'
    l = ListMotionSegment(path, FilterTwoBars)
    print(len(l))

    
    


if __name__ == '__main__':
    main()
