# author: haru233

from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Sleeping Dogs Model", ".bin")
    noesis.setHandlerTypeCheck(handle, noesisCheckType)
    noesis.setHandlerLoadModel(handle, noesisLoadModel)
    return 1

def noesisCheckType(data):
    return True

def noesisLoadModel(data, mdlList):
    bs = NoeBitStream(data)

    Indices = []
    Vertices = []

    
  
  

    while bs.tell() < len(data):
        print(bs.tell())
        ChunkID = bs.readUInt()
        bs.seek(4, 1)
        ChunkSize = bs.readUInt()
        bs.seek(4, 1)

        print(ChunkID)
        print(ChunkSize)

        if ChunkID != 2056721529:
            bs.read(ChunkSize)
            continue

        else:
            # First comes Index Buffer
            curOffset = bs.tell()
            padding = (16 - (curOffset % 16)) % 16
            bs.seek(padding, 1)

            bs.seek(68, 1)
            IndexBufferSize = bs.readUInt()
            bs.seek(8, 1)
            IndexCount = bs.readUInt() # IndexBufferSize // 2
            print(IndexCount)
            bs.seek(108, 1)
            for i in range(IndexCount):
                Index = bs.readUShort()
                Indices.append(Index)
            
            # Second comes Vertex Buffer
            # No reading chunk header here, (already read at the start of the loop till Index Buffer)
            curOffset = bs.tell()
            padding = (16 - (curOffset % 16)) % 16
            bs.seek(padding, 1)

            bs.seek(84, 1)
            VertexBufferSize = bs.readUInt()
            bs.seek(8, 1)
            VertexCount = bs.readUInt()
            bs.seek(108, 1)
            VertexStride = VertexBufferSize // VertexCount
            for i in range(VertexCount):
                positionX = bs.readShort() / 32767
                positionZ = bs.readShort() / 32767
                positionY = bs.readShort() / 32767
                
                bs.seek(VertexStride-6, 1)
                Vertices.append(NoeVec3([positionX, positionZ, positionY]))
            break

        

    mesh = NoeMesh(Indices, Vertices, "mesh0")

    model = NoeModel([mesh])

    mdlList.append(model)

    return 1

    