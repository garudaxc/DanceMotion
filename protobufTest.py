import google.protobuf
import animation_data_pb2



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





if __name__ == '__main__':
    Test()
