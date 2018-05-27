import google.protobuf
import animation_data_pb2


a = animation_data_pb2.AnimationCurve()

print(type(a))
print(type(a.path))

print(type(a.data))

a.path = '123'
a.data.append(1.0)
print(a)

buf = a.SerializeToString()
print(buf)